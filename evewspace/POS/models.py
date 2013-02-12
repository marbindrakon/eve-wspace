from django.db import models
from core.models import Type, Location
from Map.models import System
import csv
from django.contrib.auth.models import User
import pytz

class Alliance(models.Model):
    """Represents an alliance, data pulled from api"""
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=100)
    executor = models.ForeignKey('Corporation', blank=True, null=True, related_name='+')

    def __unicode__(self):
        return self.name


class Corporation(models.Model):
    """Represents a corporation, data pulled from api"""
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=100)
    alliance = models.ForeignKey(Alliance, null=True, blank=True, related_name='member_corps')
    member_count = models.IntegerField()

    def __unicode__(self):
        return self.name


class POS(models.Model):
    """Represents a POS somewhere in space."""
    system = models.ForeignKey(System, related_name="poses")
    planet = models.IntegerField()
    moon   = models.IntegerField()
    towertype = models.ForeignKey(Type, related_name="inspace")
    corporation = models.ForeignKey(Corporation, related_name="poses")
    posname = models.CharField(max_length=100, blank=True, null=True)
    fitting = models.TextField(blank=True, null=True)
    #Using CCP's status codes here for sanity with API checks
    status = models.IntegerField(choices = ((0, 'Unanchored'), (1, 'Anchored'),
        (2, 'Onlining'), (3, 'Reinforced'), (4, 'Online')))

    #This should be the time the tower exits RF
    #TODO: add a validator to make sure this is only set if status = 3 (Reinforced)
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

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.rftime and self.status != 3:
            raise ValidationError("A POS cannot have an rftime unless it is reinforced")

    def __unicode__(self):
        return self.posname

    #overide save to implement posname defaulting to towertype.name
    def save(self, *args, **kwargs):
        if not self.posname:
            self.posname = self.towertype.name
        # Ensure that any newline characters in fitting are changed to <br>
        self.fitting = self.fitting.replace("\n", "<br />")
        # Mark tower as having been updated
        from datetime import datetime
        import pytz
        self.updated = datetime.now(pytz.utc)
        super(POS, self).save(*args, **kwargs)

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
        import csv
        from core.models import Type
        itemDict={}
        # marketGroupIDs to consider guns, ewar, hardeners, and smas
        gunsGroups = [480, 479, 594, 595, 596]
        ewarGroups = [481, 1009]
        smaGroups = [484,]
        hardenerGroups = [485,]
        towers = 0
        self.sma = 0
        self.hardener = 0
        self.guns = 0
        self.ewar = 0
        for row in csv.reader(dscan.splitlines(), delimiter="\t"):
            itemType = Type.objects.get(name=row[1])
            if itemType.marketgroup:
                groupTree = []
                parent = itemType.marketgroup
                while parent:
                    groupTree.append(parent.id)
                    parent = parent.parentgroup
                if itemType.marketgroup.id in gunsGroups:
                    self.guns += 1
                if itemType.marketgroup.id in ewarGroups:
                    self.ewar += 1
                if itemType.marketgroup.id in smaGroups:
                    self.sma += 1
                if itemType.marketgroup.id in hardenerGroups:
                    self.hardener += 1
                if itemType.marketgroup.id == 478:
                    towers += 1
                if itemDict.has_key(itemType.name):
                    itemDict[itemType.name] += 1
                elif 1285 in groupTree and 478 not in groupTree:
                    itemDict.update({itemType.name: 1})

        self.fitting = "Imported from D-Scan:\n"
        for itemtype in itemDict:
            self.fitting += "\n%s : %s" % (itemtype, itemDict[itemtype])
        if towers <= 1:
            self.save()
        else:
            raise AttributeError('Too many towers detected in the D-Scan!')

class CorpPOS(POS):
    """A corp-controlled POS with manager and password data."""
    manager = models.ForeignKey(User, null=True, blank=True, related_name='poses')
    password = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    #Let's store the CCP Item ID for the tower here to make API lookup easier
    #If it is null, then we are not tracking this POS via API
    apiitemid = models.BigIntegerField(null=True, blank=True)
    from API.models import CorpAPIKey
    apikey = models.ForeignKey(CorpAPIKey, null=True, blank=True, related_name='poses')

    class Meta:
        permissions = (('can_see_pos_pw', 'Can see corp POS passwords.'),
        ('can_see_all_pos', 'Sees all corp POSes regardless of manager.'),)


class POSApplication(models.Model):
    """Represents an application for a personal POS."""
    applicant = models.ForeignKey(User, null=True, blank=True, related_name='posapps')
    towertype = models.ForeignKey(Type, null=True, blank=True, related_name='posapps')
    residents = models.ManyToManyField(User)
    normalfit = models.TextField()
    siegefit = models.TextField()
    #Once it is approved, we will fill in these two to tie the records together
    approved = models.DateTimeField(blank=True, null=True)
    posrecord = models.ForeignKey(CorpPOS, blank=True, null=True, related_name='application')

    class Meta:
        permissions = (('can_close_pos_app', 'Can dispose of corp POS applications.'),)

    def __unicode__(self):
        return 'Applicant: %s  Tower: %s' % (self.applicant.username, self.towertype.name)


class POSVote(models.Model):
    """Represents a vote on a personal POS application."""
    application = models.ForeignKey(POSApplication, related_name='votes')
    voter = models.ForeignKey(User, related_name='posvotes')
    vote = models.IntegerField(choices=((0,'Deny'), (1, 'Approve'), (2, 'Abstain')))
