#    Eve W-Space
#    Copyright (C) 2013  Andrew Austin and other contributors
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version. An additional term under section
#    7 of the GPL is included in the LICENSE file.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.db import models
from django.contrib.auth.models import User
# Core models contains models used across multiple apps

class NewsFeed(models.Model):
    """
    Contains information about an RSS feed. If user is None, the feed is
    global.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='feeds', null=True)

    class Meta:
        ordering = ['name']

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


class ConfigEntry(models.Model):
    """A configuration setting that may be changed at runtime."""
    name = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name='settings', null=True, blank=True)


class MarketGroup(models.Model):
    """A market group from the Eve SDD."""
    id = models.IntegerField(primary_key=True, db_column='marketGroupID')
    name = models.CharField(max_length = 100, null=True, blank=True,
            db_column='marketGroupName')
    parentgroup = models.ForeignKey("self", related_name="childgroups",
            blank=True, null=True, db_column='parentGroupID')
    description = models.CharField(max_length = 200, null=True, blank=True)
    hasTypes = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'invMarketGroups'
        managed = False


class Type(models.Model):
    """A type from the Eve SDD invTypes table."""
    id = models.IntegerField(primary_key=True, db_column='typeID')
    name = models.CharField(max_length = 100, db_column='typeName')
    description = models.TextField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    marketgroup = models.ForeignKey(MarketGroup, null=True, blank=True, related_name="types",
            db_column='marketGroupID')
    published = models.BooleanField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'invTypes'
        managed = False


class Region(models.Model):
    """Core model for static region data"""

    id   = models.IntegerField(primary_key=True, db_column='regionID')
    name = models.CharField(max_length=100, db_column='regionName')
    x    = models.FloatField()
    y    = models.FloatField()
    z    = models.FloatField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mapRegions'
        managed = False


class Constellation(models.Model):
    """Core model for static constellation data, references Region"""
    id = models.IntegerField(primary_key=True, db_column='constellationID')
    name = models.CharField(max_length=100, db_column='constellationName')
    region = models.ForeignKey(Region, related_name='constellations',
            db_column='regionID')
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mapConstellations'
        managed = False


class SystemData(models.Model):
    """Core model for static system data from the SDD, references Region and Constellation"""
    id = models.IntegerField(primary_key=True, db_column='solarSystemID')
    name = models.CharField(max_length=100, db_column='solarSystemName')
    constellation = models.ForeignKey(Constellation, related_name='systems',
            db_column='constellationID')
    region = models.ForeignKey(Region, related_name='systems', db_column='regionID')
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    security = models.FloatField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mapSolarSystems'
        managed = False


class StarbaseResourcePurpose(models.Model):
    """Core model for SDD invControlTowerResourcePurpose table."""
    purpose = models.IntegerField(primary_key=True)
    purposeText = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.purposeText

    class Meta:
        db_table = 'invControlTowerResourcePurposes'
        managed = False


class StarbaseResource(models.Model):
    """Core model for SDD invStarbaseResources table. Maps tower types
    to their fuel"""
    towerType = models.ForeignKey(Type, related_name='posesfueled',
            db_column='controlTowerTypeID', primary_key=True)
    resourceType = models.ForeignKey(Type, related_name='posfuel',
            db_column='resourceTypeID')
    purpose = models.ForeignKey(StarbaseResourcePurpose, related_name='usedby',
            db_column='purpose', blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True, db_column='quantity')
    minSecurityLevel = models.FloatField(blank=True, null=True, db_column='minSecurityLevel')

    def __unicode__(self):
        return '%s %s' % (self.towerType.name, self.resourceType.name)

    class Meta:
        db_table = 'invControlTowerResources'
        managed = False


class Location(models.Model):
    """Core model for SDD mapDenormalize table that generic locations map to."""
    itemid = models.IntegerField(primary_key=True, db_column='itemID')
    typeid = models.ForeignKey(Type, null=True, blank=True, related_name='mapentries',
            db_column='typeID')
    system = models.ForeignKey(SystemData, null=True, blank=True, related_name='mapentries',
            db_column='solarSystemID')
    constellation = models.ForeignKey(Constellation, null=True, blank=True,
            related_name='mapentries', db_column='constellationID')
    region = models.ForeignKey(Region, null=True, blank=True, related_name='mapentries',
            db_column='regionID')
    orbitparent = models.ForeignKey('Location', null=True, blank=True,
            related_name='satellites', db_column='orbitID')
    name = models.CharField(max_length=100, null=True, blank=True, db_column='itemName')
    x = models.FloatField(null=True, blank=True, db_column='x')
    y = models.FloatField(null=True, blank=True, db_column='y')
    z = models.FloatField(null=True, blank=True, db_column='z')
    security = models.FloatField(null=True, blank=True, db_column='security')

    class Meta:
        db_table='mapDenormalize'
        managed = False


class LocationWormholeClass(models.Model):
    """Core model for SDD mapLocationWormholeClasses used to generate system tables."""
    location = models.ForeignKey(Location, primary_key=True, related_name="whclass",
            db_column='locationID')
    sysclass = models.IntegerField(null=True, blank=True, db_column='wormholeClassID')

    class Meta:
        db_table='mapLocationWormholeClasses'
        managed = False


class SystemJump(models.Model):
    """Core model for SDD mapSolarSystemJumps used in A* calcs."""
    fromregion = models.IntegerField(db_column="fromRegionID")
    fromconstellation = models.IntegerField(db_column="fromConstellationID")
    fromsystem = models.IntegerField(db_column="fromSolarSystemID", primary_key=True)
    tosystem = models.IntegerField(db_column="toSolarSystemID", primary_key=True)
    toconstellation = models.IntegerField(db_column="toConstellationID")
    toregion = models.IntegerField(db_column="toRegionID")

    class Meta:
        db_table='mapSolarSystemJumps'
        managed = False


class Faction(models.Model):
    id = models.IntegerField(primary_key=True, db_column='factionID')
    name = models.CharField(max_length=300, db_column='factionName', blank=True)
    description = models.CharField(max_length=3000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True)
    class Meta:
        managed = False
        db_table = u'chrFactions'
