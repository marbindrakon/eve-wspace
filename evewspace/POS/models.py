#   Eve W-Space
#   Copyright 2014 Andrew Austin and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import csv

from django.db import models
from django.conf import settings
import eveapi

from core.models import Type, Location
from API.models import CorpAPIKey
from core.models import Corporation, Alliance
from Map.models import System, MapSystem, Map
from API import cache_handler as handler


User = settings.AUTH_USER_MODEL


class POS(models.Model):
    """Represents a POS somewhere in space."""
    system = models.ForeignKey(System, related_name="poses")
    planet = models.IntegerField()
    moon = models.IntegerField()
    towertype = models.ForeignKey(Type, related_name="inspace")
    corporation = models.ForeignKey(Corporation, related_name="poses")
    posname = models.CharField(max_length=100, blank=True, null=True)
    fitting = models.TextField(blank=True, null=True)
    # Using CCP's status codes here for sanity with API checks
    status = models.IntegerField(choices=((0, 'Unanchored'),
                                          (1, 'Anchored'),
                                          (2, 'Onlining'),
                                          (3, 'Reinforced'),
                                          (4, 'Online')))

    # This should be the time the tower exits RF
    # TODO: add a validator to make sure this is only set
    #       if status = 3 (Reinforced)
    rftime = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField()
    # These values will be set by the TSV parser from d-scan data if available
    guns = models.IntegerField(null=True, blank=True)
    ewar = models.IntegerField(null=True, blank=True)
    sma = models.IntegerField(null=True, blank=True)
    hardener = models.IntegerField(null=True, blank=True)
    # This is a short comment that is displayed as a warning
    warpin_notice = models.CharField(blank=True, null=True, max_length=64)

    class Meta:
        ordering = ['system__name', 'planet', 'moon']

    @classmethod
    def update_from_import_list(cls, system, import_list):
        """
        Imports starbases from YAML importer.
        """
        for pos in import_list:
            planet = pos['planet']
            moon = pos['moon']
            warpin = pos['warpin']
            status = pos['status']
            rftime = pos['rftime']
            name = pos['name']
            tower = Type.objects.get(name=pos['tower'])
            try:
                owner = Corporation.objects.get(name=pos['owner'])
            except Corporation.DoesNotExist:
                from core import tasks
                api = eveapi.EVEAPIConnection(cacheHandler=handler)
                corp_id = api.eve.CharacterID(
                    names=pos['owner']).characters[0].characterID
                owner = tasks.update_corporation(corp_id, True)
            if POS.objects.filter(system=system, planet=planet,
                                  moon=moon, corporation=owner).exists():
                # Update first existing record
                starbase = POS.objects.filter(system=system, planet=planet,
                                              moon=moon,
                                              corporation=owner).all()[0]
                starbase.status = status
                starbase.name = name
                starbase.towertype = tower
                if status == 3:
                    starbase.rftime = rftime
                starbase.warpin_notice = warpin
            else:
                new_pos = POS(system=system, planet=planet, moon=moon,
                              corporation=owner, towertype=tower,
                              warpin_notice=warpin, status=status)
                if status == 3:
                    new_pos.rftime = rftime
                new_pos.save()

    def as_dict(self):
        data = {
            'planet': self.planet, 'moon': self.moon,
            'tower': self.towertype.name, 'owner': self.corporation.name,
            'status': self.status, 'name': self.posname,
            'rftime': self.rftime, 'warpin': self.warpin_notice,
        }
        return data

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.rftime and self.status != 3:
            raise ValidationError("A POS cannot have an rftime unless "
                                  "it is reinforced")

    def __unicode__(self):
        return self.posname

    # override save to implement posname defaulting to towertype.name
    def save(self, *args, **kwargs):
        if not self.posname:
            self.posname = self.towertype.name
        # Mark tower as having been updated
        from datetime import datetime
        import pytz
        self.updated = datetime.now(pytz.utc)
        super(POS, self).save(*args, **kwargs)

    def log(self, user, action, map_system):
        """
        Records a log entry for POS updates and additions.
        """
        map_system.map.add_log(
            user,
            "%s POS (Planet %s Moon %s, owner %s) in %s (%s), %s jumps out from root system."
            %(action, self.planet, self.moon, self.corporation, map_system.system.name,
              map_system.friendlyname, map_system.distance_from_root()))

    def size(self):
        """
        Returns the size of the tower, Small Medium or Large.
        """
        if u'Small' in self.towertype.name:
            return u'Small'
        if u'Medium' in self.towertype.name:
            return u'Medium'

        return u'Large'

    def fit_from_dscan(self, dscan):
        """
        Fills in a POS's fitting from a copy / paste of d-scan results.
        """
        return self.fit_from_iterable(csv.reader(dscan.splitlines(),
                                                 delimiter="\t"))

    def fit_from_iterable(self, fit):
        """
        Fills in a POS's fitting from an iterable (normally parsed d-scan)
        """
        from core.models import Type
        item_dict = dict()
        # marketGroupIDs to consider guns, ewar, hardeners, and smas
        guns_groups = [480, 479, 594, 595, 596]
        ewar_groups = [481, 1009]
        sma_groups = [484]
        hardener_groups = [485]
        towers = 0
        self.sma = 0
        self.hardener = 0
        self.guns = 0
        self.ewar = 0
        for row in fit:
            try:
                item_type = Type.objects.get(name=row[1])
            # odd bug where invalid items get into dscan
            except Type.DoesNotExist:
                continue
            if item_type.marketgroup:
                group_tree = []
                parent = item_type.marketgroup
                while parent:
                    group_tree.append(parent.id)
                    parent = parent.parentgroup
                if item_type.marketgroup.id in guns_groups:
                    self.guns += 1
                if item_type.marketgroup.id in ewar_groups:
                    self.ewar += 1
                if item_type.marketgroup.id in sma_groups:
                    self.sma += 1
                if item_type.marketgroup.id in hardener_groups:
                    self.hardener += 1
                if item_type.marketgroup.id == 478:
                    towers += 1
                    towertype = item_type
                    posname = row[0]
                if item_type.name in item_dict:
                    item_dict[item_type.name] += 1
                elif 1285 in group_tree and 478 not in group_tree:
                    item_dict.update({item_type.name: 1})

        self.fitting = "Imported from D-Scan:\n"
        for itemtype in item_dict:
            self.fitting += "\n%s : %s" % (itemtype, item_dict[itemtype])
        if towers == 1 and self.towertype_id is None and self.posname is None:
            self.towertype = towertype
            self.posname = posname
        if towers == 0 and self.towertype_id is None:
            raise AttributeError('No POS in the D-Scan!')
        elif towers <= 1:
            self.save()
        else:
            raise AttributeError('Too many towers detected in the D-Scan!')

    def statuslabel(self):
        if self.status == 0:
            return "Unanchored"
        if self.status == 1:
            return "Anchored"
        if self.status == 2:
            return "Onlining"
        if self.status == 3:
            return "Reinforced"
        if self.status == 4:
            return "Online"

class CorpPOS(POS):
    """A corp-controlled POS with manager and password data."""
    manager = models.ForeignKey(User, null=True, blank=True,
                                related_name='poses')
    password = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    # Let's store the CCP Item ID for the tower here to make API lookup easier
    # If it is null, then we are not tracking this POS via API
    apiitemid = models.BigIntegerField(null=True, blank=True)
    apikey = models.ForeignKey(CorpAPIKey, null=True, blank=True,
                               related_name='poses')

    class Meta:
        permissions = (('can_see_pos_pw', 'Can see corp POS passwords.'),
                       ('can_see_all_pos', 'Sees all corp POSes '
                                           'regardless of manager.'),)


class POSApplication(models.Model):
    """Represents an application for a personal POS."""
    applicant = models.ForeignKey(User, null=True, blank=True,
                                  related_name='posapps')
    towertype = models.ForeignKey(Type, null=True, blank=True,
                                  related_name='posapps')
    residents = models.ManyToManyField(User)
    normalfit = models.TextField()
    siegefit = models.TextField()
    # Once it is approved, we will fill in these two to tie the records together
    approved = models.DateTimeField(blank=True, null=True)
    posrecord = models.ForeignKey(CorpPOS, blank=True, null=True,
                                  related_name='application')

    class Meta:
        permissions = (('can_close_pos_app',
                        'Can dispose of corp POS applications.'),)

    def __unicode__(self):
        return 'Applicant: %s  Tower: %s' % (self.applicant.username,
                                             self.towertype.name)


class POSVote(models.Model):
    """Represents a vote on a personal POS application."""
    application = models.ForeignKey(POSApplication, related_name='votes')
    voter = models.ForeignKey(User, related_name='posvotes')
    vote = models.IntegerField(choices=((0, 'Deny'),
                                        (1, 'Approve'),
                                        (2, 'Abstain')))
