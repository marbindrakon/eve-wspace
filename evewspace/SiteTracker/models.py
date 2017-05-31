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
from django.db import models
from django.conf import settings
from Map.models import Map, System, MapSystem
from core.utils import get_config
from datetime import datetime
import pytz

# Create your models here.

User = settings.AUTH_USER_MODEL

class Fleet(models.Model):
    """Represents a SiteTracker fleet."""
    system = models.ForeignKey(System, related_name="stfleets")
    initial_boss = models.ForeignKey(User, related_name="bossfleets")
    current_boss = models.ForeignKey(User, related_name="currently_bossing")
    started = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(blank=True, null=True)
    roles_needed = models.ManyToManyField('SiteRole', related_name="fleets_need")

    class Meta:
        permissions = (("can_sitetracker", "Use the Site Tracker system."),)

    def __unicode__(self):
        return "MapSystem: %s Boss: %s  Started: %s  Ended: %s" % (self.system.name,
                self.current_boss.username, self.started, self.ended)

    def __contains__(self, user):
        """
        Allow for user in fleet syntax to determine both inactive and active
        user records for a fleet.
        """
        if user is None:
            return False
        return self.members.filter(user=user).exists()

    def __iter__(self):
        """
        Provide support for syntax: for User in fleet
        """
        for member_rec in self.members.all():
            yield member_rec.user

    def credit_site(self, site_type, system, boss):
        """
        Credits a site.
        """
        # Get the fleet member weighting variable and multiplier
        x = float(get_config("ST_SIZE_WEIGHT", None).value)
        n = self.members.filter(leavetime=None).count()
        if x > 1:
            weight_factor = x / float(n + (x - 1))
        else:
            # If the factor is set to anything equal to or less than 1,
            # we will not weight the results by fleet size
            weight_factor = float(1)
        if SystemWeight.objects.filter(system=system).count():
            weight_factor = weight_factor * system.st_weight.weight
        raw_points = SiteWeight.objects.get(site_type=site_type,
                sysclass=system.sysclass).raw_points
        site = SiteRecord(fleet=self, site_type=site_type, system=system,
                boss=boss, fleetsize=self.members.filter(leavetime=None).count(),
                raw_points=raw_points,
                weighted_points = raw_points * weight_factor)
        site.save()
        for user in self.members.filter(leavetime=None).all():
            site.members.add(UserSite(site=site, user=user.user, pending=False))
        return site


    def close_fleet(self):
        """
        Closes the SiteTracker fleet.
        """
        for member in self.members.filter(leavetime=None):
            member.leavetime = datetime.now(pytz.utc)
            member.save()
        self.ended = datetime.now(pytz.utc)
        self.save()

    def join_fleet(self, user):
        """
        Adds user to fleet.
        """
        if not self.members.filter(user=user, leavetime=None).count():
            u = UserLog(fleet=self, user=user).save()
        else:
            u = self.members.get(user=user, leavetime=None)
        return u

    def active_members(self):
        """
        Return a list of active members.
        """
        return self.members.filter(leavetime=None)

    def leave_fleet(self, user):
        """
        Removes user from fleet.
        """
        if self.members.filter(leavetime=None).count() == 1:
            # We're the only member left, close the fleet.
            self.close_fleet()
            return None
        elif self.current_boss == user:
            # We're the boss, give it to the first schmuck we can.
            self.current_boss = self.members.exclude(user=user).filter(
                    leavetime=None).all()[0].user
            self.save()
        UserLog.objects.filter(fleet=self,
                user=user, leavetime=None).update(leavetime=datetime.now(pytz.utc))

    def make_boss(self, user):
        """
        Change the current fleet boss.
        """
        self.current_boss = user
        self.save()


class SiteRole(models.Model):
    """Represents a role for a sitetracker fleet."""
    short_name = models.CharField(max_length=32, unique=True)
    long_name = models.CharField(max_length=255, unique=True)


class SiteType(models.Model):
    """Represents a type of site that can be credited."""
    shortname = models.CharField(max_length=8, unique=True)
    longname = models.CharField(max_length=80, unique=True)
    # Defunct site types are maintained in the databse for relational purposes but can no longer be credited
    defunct = models.BooleanField(default=False)

    def __unicode__(self):
        return self.longname


class SiteWeight(models.Model):
    """
    Represents the raw points available for a site type / system class combo
    """
    site_type = models.ForeignKey(SiteType, related_name='weights')
    sysclass = models.IntegerField(choices=[(1, "C1"), (2, "C2"), (3, "C3"),
        (4, "C4"), (5, "C5"), (6, "C6"), (7, "High Sec"), (8, "Low Sec"),
        (9, "Null Sec"), (10, "Jove"), (11, "Jove"), (12, "Thera"),
        (13, "Small Ship")])
    raw_points = models.IntegerField()


class SystemWeight(models.Model):
    """
    Respresents a multiplier for site credit for a system.
    """
    system = models.OneToOneField(System, primary_key=True, related_name='st_weight')
    weight = models.FloatField()


class SiteRecord(models.Model):
    """Represents the record of a site run."""
    fleet = models.ForeignKey(Fleet, related_name="sites")
    site_type = models.ForeignKey(SiteType, related_name="sitesrun")
    timestamp = models.DateTimeField(auto_now_add=True)
    system = models.ForeignKey(System, related_name="sitescompleted")
    boss = models.ForeignKey(User, related_name="sitescredited")
    fleetsize = models.IntegerField()
    raw_points = models.IntegerField()
    weighted_points = models.FloatField()

    def __unicode__(self):
        return "System: %s Time: %s  Type: %s" % (self.system.name, self.timestamp, self.type.shortname)

    def __contains__(self, user):
        """
        Allow for if user in siterecord to determine if a user has an entry.
        """
        if user is None:
            return False
        return self.members.filter(user=user).exists()

    def __iter__(self):
        """
        Allow for syntax: for user in siterecord.
        """
        for log in self.members.all():
            yield log.user

    def is_pending(self, user):
        """
        Return True if user's credit is pending.
        """
        return self.members.get(user=user).pending


class UserSite(models.Model):
    """Represents a user's credit for a site."""
    site = models.ForeignKey(SiteRecord, related_name="members")
    user = models.ForeignKey(User, related_name="sites")
    pending = models.BooleanField(default=False)

    def approve(self):
        """
        Mark the site approved.
        """
        new_fleetsize = self.site.fleetsize + 1
        x = float(get_config("ST_SIZE_WEIGHT", None).value)
        n = new_fleetsize
        if x > 1:
            weight_factor = x / float(n + (x - 1))
        else:
            weight_factor = float(1)
        self.site.fleetsize = new_fleetsize
        self.site.weighted_points = self.site.raw_points * weight_factor
        self.site.save()
        self.pending = False
        self.save()


class UserLog(models.Model):
    """Represents a user's sitetracker log."""
    fleet = models.ForeignKey(Fleet, related_name="members")
    user = models.ForeignKey(User, related_name="sitetrackerlogs")
    jointime = models.DateTimeField(auto_now_add=True)
    leavetime = models.DateTimeField(null=True, blank=True)

    def pending_sites(self):
        """
        Returns a list of site records which are pending credit.
        """
        pending_sites = []
        for site in self.fleet.sites.all():
            if UserSite.objects.filter(user=self.user, site=site,
                    pending=True).exists():
                pending_sites.append(site)
        return pending_sites

class ClaimPeriod(models.Model):
    """Represents a claim period that Users can claim against."""
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    name = models.CharField(max_length = 80)
    closetime = models.DateTimeField(blank=True, null=True)
    loothauledby = models.ForeignKey(User, related_name="loothauled", null=True, blank=True)
    lootsoldby = models.ForeignKey(User, related_name="lootsold", null=True, blank=True)
    class Meta:
        permissions = (("can_close_claims", "Close the claims period early."),
                         ("can_reopen_claims", "Reopen the claims period."),
                         ("can_haul_loot", "Mark the claim period as hauled."),
                         ("can_sell_loot", "Mark the claim period as sold."),)


    def __unicode__(self):
        return self.name

class Claim(models.Model):
    """Represents a User's claim for a claim period."""
    period = models.ForeignKey(ClaimPeriod, related_name="claims")
    user = models.ForeignKey(User, related_name="claims")
    shareclaimed = models.FloatField()
    description = models.TextField()
    bonus = models.FloatField(blank=True, null=True)

class PayoutReport(models.Model):
    """Represents a payout report and contains general information about the payout period."""
    period = models.ForeignKey(ClaimPeriod, related_name="reports")
    createdby = models.ForeignKey(User, related_name="payoutreports")
    grossprofit = models.BigIntegerField()
    datepaid = models.DateTimeField(blank=True, null=True)

class PayoutEntry(models.Model):
    """Represents an entry in the payout report."""
    report = models.ForeignKey(PayoutReport, related_name="entries")
    user = models.ForeignKey(User, related_name="payouts")
    claim = models.ForeignKey(Claim, related_name="payout")
    iskshare = models.BigIntegerField()





