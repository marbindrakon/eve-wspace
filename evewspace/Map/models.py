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
from django.contrib.auth.models import Group
from core.models import SystemData
from django import forms
from django.forms import ModelForm
from datetime import datetime, timedelta
import pytz
import time
import yaml
from Map import utils
from Map.utils import MapJSONGenerator
from django.core.cache import cache
# Create your models here.

User = settings.AUTH_USER_MODEL


class WormholeType(models.Model):
    """Stores the permanent information on wormhole types.

    Any changes to this table should be made with caution.
    """
    name = models.CharField(max_length=4, unique=True)
    maxmass = models.BigIntegerField()
    jumpmass = models.BigIntegerField()
    lifetime = models.IntegerField()
    # source is a  2-char fields that can be:
    # 1-6 : Wormhole classes 1-6
    # H : High Sec Only (e.g. freighter capable K > C5 in high)
    # NH : Low or Nullsec (e.g. cap capable K > C5)
    # K : Any K-space (e.g. X702 to a C3)
    # W: Any W-space (i.e. Hyperion frig holes)
    # N: Nullsec
    # L: Lowsec
    # Z: Class 5 or 6 (5/6 > K holes)
    # X: Special ID for K162 and stargates
    source = models.CharField(max_length=2)
    # Destination is an integer representation of System.sysclass
    # Except that it may be 0 which indicates a K162 or Stargate
    destination = models.IntegerField()
    target = models.CharField(max_length=15)

    def __unicode__(self):
        """Returns Wormhole ID as unicode representation."""
        return self.name

    def dest_string(self):
        """Returns a readable destination.

        Cx for w-space and H, L, N otherwise.
        """
        if 7 > self.destination > 0:
            return "C%s" % (self.destination,)
        if self.destination == 0:
            return "Varies"
        if self.destination == 7:
            return "High Sec"
        if self.destination == 8:
            return "Low Sec"
        if self.destination == 9:
            return "Null Sec"
        return "Unknown"


class System(SystemData):
    """Stores the permanent record of a solar system.

    This table should not have rows added or removed through Django.
    """
    sysclass_choices = ((1, "C1"), (2, "C2"), (3, "C3"), (4, "C4"), (5, "C5"),
                        (6, "C6"), (7, "High Sec"), (8, "Low Sec"),
                        (9, "Null Sec"))
    sysclass = models.IntegerField(choices=sysclass_choices)
    importance_choices = ((0, "Regular"),
                          (1, "Dangerous System"),
                          (2, "Important System"))
    importance = models.IntegerField(choices=importance_choices, default=0)
    occupied = models.TextField(blank=True)
    info = models.TextField(blank=True)
    lastscanned = models.DateTimeField()
    npckills = models.IntegerField(null=True, blank=True)
    podkills = models.IntegerField(null=True, blank=True)
    shipkills = models.IntegerField(null=True, blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    first_visited = models.DateTimeField(null=True, blank=True)
    last_visited = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        """Returns name of System as unicode representation"""
        return self.name

    @property
    def class_string(self):
        if self.sysclass < 7:
            return 'C%s' % self.sysclass
        if self.sysclass == 7:
            return 'Highsec'
        if self.sysclass == 8:
            return 'Lowsec'
        if self.sysclass == 9:
            return 'Nullsec'
        # Class 10/11 appear in two Jovian constellations. Reason unknown.
        if self.sysclass == 10:
            return 'Odd Jove Space'
        if self.sysclass == 11:
            return 'Odd Jove Space'
        if self.sysclass == 12:
            return 'Thera'
        if self.sysclass == 13:
            return 'Small Ship'

    def is_kspace(self):
        if self.sysclass in range(7, 12):
            return True

    def is_wspace(self):
        if self.sysclass not in range(7, 12):
            return True

    def is_rhea_space(self):
        if self.sysclass == 13:
            return True

    def get_spec(self):
        if self.sysclass in range(7, 12):
            return self.ksystem
        else:
            return self.wsystem

    def save(self, *args, **kwargs):
        self.updated = datetime.now(pytz.utc)
        if self.lastscanned < datetime.now(pytz.utc) - timedelta(days=3):
            self.lastscanned = datetime.now(pytz.utc)
        if not self.first_visited:
            self.first_visited = datetime.now(pytz.utc)
            self.last_visited = datetime.now(pytz.utc)
        if self.last_visited < datetime.now(pytz.utc) - timedelta(days=2):
            self.last_visited = datetime.now(pytz.utc)

        super(System, self).save(*args, **kwargs)

    def add_active_pilot(self, username, charid, charname,
                         shipname, shiptype):
        sys_cache_key = 'sys_%s_locations' % self.pk
        current_time = time.time()
        time_threshold = current_time - (15 * 60)
        sys_location_dict = cache.get(sys_cache_key)
        location = (username, charname, shipname, shiptype, current_time)
        if sys_location_dict:
            sys_location_dict.pop(charid, None)
            sys_location_dict[charid] = location
        else:
            sys_location_dict = {charid: location}

        # Prune dict to prevent carrying over stale entries
        for charid, location in sys_location_dict.items():
            if location[4] < time_threshold:
                sys_location_dict.pop(charid, None)

        cache.set(sys_cache_key, sys_location_dict, 15 * 60)
        return location

    def remove_active_pilot(self, charid):
        current_time = time.time()
        time_threshold = current_time - (15 * 60)
        sys_cache_key = 'sys_%s_locations' % self.pk
        sys_location_dict = cache.get(sys_cache_key)
        if sys_location_dict:
            sys_location_dict.pop(charid, None)
            # Prune dict to prevent carrying over stale entries
            for charid, location in sys_location_dict.items():
                if location[4] < time_threshold:
                    sys_location_dict.pop(charid, None)
            cache.set(sys_cache_key, sys_location_dict, 15 * 60)
        return True

    def _active_pilot_list(self):
        sys_cache_key = 'sys_%s_locations' % self.pk
        sys_location_dict = cache.get(sys_cache_key)
        if sys_location_dict:
            return sys_location_dict
        else:
            return {}

    pilot_list = property(_active_pilot_list)

    def clear_sig_cache(self):
        cache.delete('sys_%s_sig_list' % self.pk)


class KSystem(System):
    """Represents a k-space system."""
    sov = models.CharField(max_length=100)
    jumps = models.IntegerField(blank=True, null=True)

    def jumps_to(self, destination):
        """Returns the number of gate jumps to a system by shortest route."""
        return utils.RouteFinder().route_length(self, destination)

    def distance(self, destination):
        """Returns the light-year distance to the destination."""
        return utils.RouteFinder().ly_distance(self, destination)


class WSystem(System):
    """Represents a w-space system."""
    static1 = models.ForeignKey(WormholeType, blank=True, null=True,
                                related_name="primary_statics")
    static2 = models.ForeignKey(WormholeType, blank=True, null=True,
                                related_name="secondary_statics")
    effect = models.CharField(max_length=50, blank=True, null=True)
    is_shattered = models.NullBooleanField(default=False)


class Map(models.Model):
    """Stores the maps available in the map tool.

    root relates to System model.
    """
    name = models.CharField(max_length=100, unique=True)
    root = models.ForeignKey(System, related_name="root")
    # Maps with explicitperms = True
    # require an explicit permission entry to access.
    explicitperms = models.BooleanField(default=False)
    truncate_allowed = models.BooleanField(default=True)

    class Meta:
        permissions = (("map_unrestricted",
                        "Do not require excplicit access to maps."),
                       ("map_admin", "Access map configuration."),)

    def __unicode__(self):
        """Returns name of Map as unicode representation."""
        return self.name

    def __contains__(self, system):
        """Check if a MapSystem is contained in this map.

        A convience to allow 'if system in map:' type statements to
        determine if there exist a MapSystem with
        system.map = self and system in self.systems
        NOTE: system must be a System, NOT a MapSystem
        """
        # I *think* this should be handled by the filter used in the
        # main return statement, but as I require this behaviour
        # I'll make it explicit
        if system is None:
            return False

        return self.systems.filter(system=system).exists()

    # Given a __contains__ function I guess it makes sense to implement this
    # so for ... in ... will work too.
    def __iter__(self):
        """Returns an iterator over all Systems in the map.

        NOTE: returns Systems not MapSystems
        """
        for msys in self.systems.all():
            yield msys.system

    @classmethod
    def yaml_import(self, user, yaml_string):
        """Imports a YAML export string into a new Map."""
        yaml_dict = yaml.safe_load(yaml_string)
        map_name = yaml_dict['map_name']
        root_system = yaml_dict['systems'][0]
        root_sys = System.objects.get(name=root_system['system'])
        new_map = Map(name=map_name, root=root_sys)
        new_map.save()
        root_mapsys = new_map.add_system(user=user, system=root_sys,
                                         friendlyname=root_system['tag'])
        for sig in root_system['signatures']:
            sig_id = sig['id']
            info = sig['info']
            if sig['type']:
                sig_type = SignatureType.objects.get(shortname=sig['type'])
            else:
                sig_type = None
            if not Signature.objects.filter(
                    sigid=sig_id, system=root_mapsys.system).exists():
                Signature(sigid=sig_id, sigtype=sig_type,
                          system=root_mapsys.system, info=info,
                          updated=bool(sig_type)).save()
        from POS.models import POS
        POS.update_from_import_list(root_mapsys.system,
                                    root_system['starbases'])
        root_mapsys.add_children_from_list(root_system['children'])
        return new_map

    def add_log(self, user, action, visible=False):
        """Adds a log entry into a MapLog for the map."""
        log = MapLog(user=user, map=self, action=action,
                     timestamp=datetime.now(pytz.utc),
                     visible=visible)
        log.save()

    def get_permission(self, user):
        """Returns the highest permision that user has on the map.

        0 = No Access
        1 = Read Access
        2 = Write Access
        """
        # Anonymous users always return 0
        if user.is_anonymous():
            return 0
        # Special case: If user is a map admin, always return 2
        if user.has_perm('Map.map_admin'):
            return 2
        # Special case: if user is unrestricted we don't care unless the map
        # requires explicit permissions
        if user.has_perm('Map.map_unrestricted') and not self.explicitperms:
            return 2

        # Otherwise take the highest of the permissions granted by the groups
        # user is a member of
        highestperm = 0
        # query set of all groups the user is a member of
        groups = user.groups.all()
        # Done this way there should only be one db hit which gets all relevant
        # permissions
        for perm in self.grouppermissions.filter(group__in=groups):
            highestperm = max(highestperm, perm.access)

        return highestperm

    def add_system(self, user, system, friendlyname, parent=None):
        """Add a system to this map.

        Adds the provided system to the map with the provided
        friendly name. Returns the new MapSystem object.
        """
        mapsystem = MapSystem(map=self, system=system,
                              friendlyname=friendlyname,
                              parentsystem=parent)
        mapsystem.save()
        self.add_log(user, "Added system: %s" % system.name, True)
        return mapsystem

    def as_json(self, user):
        """Returns the json representation of the map.

        Used for passing map to the mapping Javascript."""
        return utils.MapJSONGenerator(self, user).get_systems_json()

    def as_yaml(self):
        """Returns the yaml representation of the map for import/export."""
        data = {'map_name': self.name,
                'export_time': datetime.now(pytz.utc),
                'systems': [x.as_dict() for x in
                            self.systems.filter(parentsystem=None).all()]}
        return yaml.safe_dump(data, encoding='utf-8', allow_unicode=True)

    def snapshot(self, user, name, description):
        """Makes and returns a snapshot of the map."""
        result = Snapshot(user=user, name=name, description=description,
                          json=self.as_json(user))
        result.save()
        self.add_log(user, "Created Snapshot: %s" % (name,))
        return result

    def clear_caches(self):
        """Clears the tooltip and json caches for the map."""
        cache.delete('map_%s_wh_tooltip' % self.pk)
        cache.delete('map_%s_sys_tooltip' % self.pk)
        cache.delete(MapJSONGenerator.get_cache_key(self))


class MapSystem(models.Model):
    """Represents a system contained in a map.

    Stores information regarding which systems are active in which maps
    at the present time.
    """
    map = models.ForeignKey(Map, related_name="systems")
    system = models.ForeignKey(System, related_name="maps")
    friendlyname = models.CharField(max_length=255)
    interesttime = models.DateTimeField(null=True, blank=True)
    parentsystem = models.ForeignKey('self', related_name="childsystems",
                                     null=True, blank=True)
    display_order_priority = models.IntegerField(default=0)

    def __unicode__(self):
        return "system %s in map %s" % (self.system.name, self.map.name)

    def add_children_from_list(self, children=None):
        """Adds child systems from list generated by the YAML importer."""
        if not children:
            children = []
        print "Adding %s children to %s" % (len(children), self.system.name)
        for child in children:
            new_sys = System.objects.get(name=child['system'])
            friendlyname = child['tag']
            new_mapsys = MapSystem(map=self.map, system=new_sys,
                                   friendlyname=friendlyname,
                                   parentsystem=self)
            new_mapsys.save()
            parent_wh = child['parent_wh']
            top_type = WormholeType.objects.get(name=parent_wh['near_type'])
            bottom_type = WormholeType.objects.get(name=parent_wh['far_type'])
            top_bubbled = parent_wh['top_bubbled']
            bottom_bubbled = parent_wh['bottom_bubbled']
            mass_status = parent_wh['mass_status']
            time_status = parent_wh['time_status']

            wh = new_mapsys.connect_to(
                system=self, top_type=top_type,
                bottom_type=bottom_type, top_bubbled=top_bubbled,
                bottom_bubbled=bottom_bubbled, time_status=time_status,
                mass_status=mass_status)
            wh.save()

            for sig in child['signatures']:
                sig_id = sig['id']
                info = sig['info']
                if sig['type']:
                    sig_type = SignatureType.objects.get(shortname=sig['type'])
                else:
                    sig_type = None
                if sig_type:
                    updated = True
                else:
                    updated = False
                if not Signature.objects.filter(
                        system=self.system, sigid=sig_id).exists():
                    Signature(sigid=sig_id, sigtype=sig_type,
                              system=self.system, info=info,
                              updated=updated).save()
            from POS.models import POS
            POS.update_from_import_list(self.system, child['starbases'])
            new_mapsys.add_children_from_list(child['children'])

    def connect_to(self, system,
                   top_type, bottom_type,
                   top_bubbled=False, bottom_bubbled=False,
                   time_status=0, mass_status=0):
        """Add a new connection to this system.

        Connect self to system and add the connecting WH to map, self is the
        bottom system. Returns the connecting wormhole.
        """
        wormhole = Wormhole(
            map=self.map, top=system, bottom=self,
            top_type=top_type, bottom_type=bottom_type,
            top_bubbled=top_bubbled, bottom_bubbled=bottom_bubbled,
            time_status=time_status, mass_status=mass_status)
        wormhole.save()
        return wormhole

    def save(self, *args, **kwargs):
        self.friendlyname = self.friendlyname.upper()
        self.map.clear_caches()
        super(MapSystem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.map.clear_caches()
        super(MapSystem, self).delete(*args, **kwargs)

    def remove_system(self, user):
        """Removes the supplied system and all of its children."""
        # Raise ValueError if we're trying to delete the root
        if not self.parentsystem:
            raise ValueError("Cannot remove the root system.")
        self.parent_wormhole.delete()
        for system in self.childsystems.all():
            system.remove_system(user)
        self.map.add_log(user, "Removed system: %s (%s)" %
                         (self.system.name, self.friendlyname), True)
        self.delete()

    def get_all_children(self):
        child_list = []
        for system in self.childsystems.all():
            for sys in system.get_all_children():
                child_list.append(sys)
        child_list.append(self)
        return child_list

    def promote_system(self, user):
        """Makes this system the root system and deletes all other chains."""
        if not self.parentsystem:
            # This is already the root system
            return True
        # Cut all ties
        self.parent_wormhole.delete()
        self.parentsystem = None
        self.save()
        # Generate a list of systems to delete
        child_list = self.get_all_children()
        for sys in self.map.systems.all():
            if sys not in child_list:
                try:
                    sys.parent_wormhole.delete()
                except Exception:
                    # Nasty hack because of race condition for deleting hole
                    pass
                sys.delete()
        self.map.add_log(
            user,
            "Truncated to: %s (%s)" % (self.system.name, self.friendlyname),
            True)

    def move_up(self):
        """Assigns this system the highest display priority of its siblings"""
        if not self.parentsystem:
            return

        max_priority = self.parentsystem.childsystems.aggregate(
            max_prio=models.Max('display_order_priority'))['max_prio']
        self.display_order_priority = max_priority + 1
        self.save()

    def as_dict(self):
        """Returns a dict representation of the system."""
        try:
            parent_wh_dict = {
                'near_type': self.parent_wormhole.top_type.name,
                'far_type': self.parent_wormhole.bottom_type.name,
                'updated': self.parent_wormhole.updated,
                'top_bubbled': self.parent_wormhole.top_bubbled,
                'bottom_bubbled': self.parent_wormhole.bottom_bubbled,
                'mass_status': self.parent_wormhole.mass_status,
                'time_status': self.parent_wormhole.time_status,
                'collapsed': self.parent_wormhole.collapsed,
            }
        except Wormhole.DoesNotExist:
            parent_wh_dict = None

        data = {
            'tag': self.friendlyname,
            'system': self.system.name,
            'signatures': [sig.as_dict() for sig in
                           self.system.signatures.all()],
            'starbases': [pos.as_dict() for pos in self.system.poses.all()],
            'parent_wh': parent_wh_dict,
            'children': [x.as_dict() for x in self.childsystems.all()],
        }
        return data

    def has_siblings(self):
        parent_sys = self.parentsystem
        if parent_sys is None:
            return False
        return parent_sys.childsystems.count() > 1

    def distance_from_root(self):
        distance = 0
        parent_sys = self.parentsystem
        while parent_sys != None:
            parent_sys = parent_sys.parentsystem
            distance +=1
            if parent_sys == None or distance > 100:
                break
        return distance


class Wormhole(models.Model):
    """An instance of a wormhole in a  map.

    Wormhole have a 'top' and a 'bottom', the top refers to the
    side that is found first (and the bottom is obviously the other side)
    """
    map = models.ForeignKey(Map, related_name='wormholes')
    top = models.ForeignKey(MapSystem, related_name='child_wormholes')
    top_type = models.ForeignKey(WormholeType, related_name='+')
    top_bubbled = models.NullBooleanField(null=True, blank=True)
    bottom = models.OneToOneField(MapSystem, null=True,
                                  related_name='parent_wormhole')
    bottom_type = models.ForeignKey(WormholeType, related_name='+')
    bottom_bubbled = models.NullBooleanField(null=True, blank=True)
    time_status = models.IntegerField(choices=((0, "Fine"),
                                               (1, "End of Life")))
    mass_status = models.IntegerField(choices=((0, "No Shrink"),
                                               (1, "First Shrink"),
                                               (2, "Critical")))
    updated = models.DateTimeField(auto_now=True)
    eol_time = models.DateTimeField(null=True)
    collapsed = models.NullBooleanField(null=True)

    @property
    def wh_type(self):
        if self.top_type.maxmass:
            return self.top_type
        if self.bottom_type.maxmass:
            return self.bottom_type
        # Default to first side of hole
        return self.top_type

    @property
    def max_mass(self):
        if self.top_type.maxmass:
            return self.top_type.maxmass
        if self.bottom_type.maxmass:
            return self.bottom_type.maxmass
        return 0

    @property
    def jump_mass(self):
        if self.top_type.jumpmass:
            return self.top_type.jumpmass
        if self.bottom_type.jumpmass:
            return self.bottom_type.jumpmass
        return 0

    def save(self, *args, **kwargs):
        self.map.clear_caches()
        if self.time_status == 1 and not self.eol_time:
            self.eol_time = datetime.now(pytz.utc)
        elif self.time_status != 1:
            self.eol_time = None
        super(Wormhole, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.map.clear_caches()
        super(Wormhole, self).save(*args, **kwargs)


class SignatureType(models.Model):
    """Stores the list of possible signature types for the map tool.

    Custom signature types may be added at will.
    """
    shortname = models.CharField(max_length=6)
    longname = models.CharField(max_length=100)
    # sleepersite and escalatable are used to track wormhole comabt sites.
    # sleepersite = true should give a "Rats cleared" option
    # escalatable = true should cause escalation tracking to kick in in C5/6
    sleeprsite = models.BooleanField(default=False)
    escalatable = models.BooleanField(default=False)

    def __unicode__(self):
        """Returns short name as unicode representation"""
        return self.shortname


class Signature(models.Model):
    """Stores the signatures active in all systems. Relates to System model."""
    system = models.ForeignKey(System, related_name="signatures")
    modified_by = models.ForeignKey(User, related_name="signatures", null=True)
    sigtype = models.ForeignKey(SignatureType, related_name="sigs",
                                null=True, blank=True)
    sigid = models.CharField(max_length=10)
    updated = models.BooleanField(default=False)
    info = models.CharField(max_length=65, null=True, blank=True)
    # ratscleared and lastescalated are used to track wormhole combat sites.
    # ratscleared is the DateTime that sleepers were cleared initially
    # lastescalated is the last time the site was escalated (if applicable)
    # activated is when the site was marked activated for reference
    # downtimes should be incremented by the server status checker
    activated = models.DateTimeField(null=True, blank=True)
    downtimes = models.IntegerField(null=True, blank=True)
    ratscleared = models.DateTimeField(null=True, blank=True)
    lastescalated = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(auto_now=True, null=True)
    owned_by = models.ForeignKey(User, related_name="sigs_owned", null=True)
    owned_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ['sigid']
        unique_together = ('system', 'sigid')

    def __unicode__(self):
        """Returns sig ID as unicode representation"""
        return self.sigid

    def as_dict(self):
        data = {
            'id': self.sigid,
            'type': self.sigtype.shortname if self.sigtype else None,
            'info': self.info,
        }
        return data

    def activate(self):
        """Toggles the site activation."""
        if not self.activated:
            self.activated = datetime.now(pytz.utc)
            if not self.downtimes:
                self.downtimes = 0
        else:
            self.activated = None
            if self.downtimes == 0:
                self.downtimes = None
        self.save()

    def clear_rats(self):
        """Toggles the NPCs cleared."""
        if not self.ratscleared:
            self.ratscleared = datetime.now(pytz.utc)
        else:
            self.ratscleared = None
        self.save()

    def escalate(self):
        """Toggles the sig escalation."""
        if not self.lastescalated:
            self.lastescalated = datetime.now(pytz.utc)
            if not self.activated:
                self.activate()
        else:
            self.lastescalated = None
        self.save()

    def increment_downtime(self):
        """Increments the downtime count and does downtime cleanup
        of updated and activated."""
        self.activated = None
        self.lastescalated = None
        if self.downtimes:
            self.downtimes += 1
        else:
            self.downtimes = 1
        self.save()

    def update(self):
        """Mark the signature as having been updated since DT."""
        self.updated = True
        self.save()

    def update_from_tsv(self, user, wascreated, row, map_system):
        """Takes a line of copied data, converts it into a signature and checks if the
        import updated an existing signature on the map, and whether or not the update 
        includes new scan data (for logging purposes).

        """
        # map columns
        COL_SIG = 0
        COL_SIG_TYPE = 3
        COL_SIG_GROUP = 2
        COL_SIG_SCAN_GROUP = 1
        COL_SIG_STRENGTH = 4
        COL_DISTANCE = 5
        info = row[COL_SIG_TYPE]
        sig_type = None
        updated = None
        action = "None"

        if wascreated is True:
            # new sig
            updated = False
            action = "Created"
        
        # Is there a valid signature type from pasted data - is it valid?
        scan_group = self._translate_client_string(row[COL_SIG_SCAN_GROUP])
        if scan_group == "Cosmic Signature" or scan_group == "Cosmic Anomaly":
            try:
                # translate names such as Ore Site, Gas Site, from
                # localized clients
                sig_type_name = self._translate_client_string(
                    row[COL_SIG_GROUP])
                sig_type = SignatureType.objects.get(
                    longname=sig_type_name)
            except:
                sig_type = None
        else:
            sig_type = None

        if sig_type:
            if action != "Created" and self.sigtype != sig_type:
                action = "Updated"
            # if there is a valid sig type, set and mark as updated
            self.sigtype = sig_type

        if info:
            # if there is a signature info (site name) field, mark as scanned
            if self.info != info:
                self.info = info
                if action != "Created":
                    action = "Updated"                    
                    if scan_group == "Cosmic Signature":
                        # only record new scanning activity for signatures
                        action = "Scanned"                        
        if action != "None":
            self.log_sig(user, action, map_system)

        self.update()

        # is this still necessary?
        if self.info is None:
            self.info = ''

        return self, action


    def log_sig(self, user, action, map_system):
        """Log the fact that the signature was scanned."""
        
        map_system.map.add_log(
            user, 
            "%s signature %s in %s (%s), %s jumps out from root system."
            %(action, self.sigid, map_system.system.name, 
              map_system.friendlyname, map_system.distance_from_root()))

    def toggle_ownership(self, user):
        """Toggles ownership."""
        if self.owned_by:
            self.owned_by = None
            self.owned_time = None
        else:
            self.owned_by = user
            self.owned_time = datetime.now(pytz.utc)
        self.save()

    def save(self, *args, **kwargs):
        """
        Ensure that Sig IDs are proper.
        """
        self.system.clear_sig_cache()
        self.sigid = utils.convert_signature_id(self.sigid)
        super(Signature, self).save(*args, **kwargs)

    def delete(self, user, mapsys, *args, **kwargs):
        self.log_sig(user, "Deleted", mapsys)
        self.system.clear_sig_cache()
        super(Signature, self).delete(*args, **kwargs)

    def _translate_client_string(self, client_text):
        """Translate text strings from EVE client.

        """
        TRANSLATE_DICT = {
            'Cosmic Signature': 'Cosmic Signature',
            'Cosmic Anomaly': 'Cosmic Anomaly',
            'Ore Site': 'Ore Site',
            'Gas Site': 'Gas Site',
            'Data Site': 'Data Site',
            'Relic Site': 'Relic Site',
            'Wormhole': 'Wormhole',
            'Combat Site': 'Combat Site',
            # Russian
            '\xd0\x98\xd1\x81\xd1\x82\xd0\xbe\xd1\x87\xd0\xbd\xd0\xb8\xd0\xba\xd0'
            '\xb8 \xd1\x81\xd0\xb8\xd0\xb3\xd0\xbd\xd0\xb0\xd0\xbb\xd0\xbe\xd0'
            '\xb2': 'Cosmic Signature',
            '\xd0\x9a\xd0\xbe\xd1\x81\xd0\xbc\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd0'
            '\xba\xd0\xb0\xd1\x8f \xd0\xb0\xd0\xbd\xd0\xbe\xd0\xbc\xd0\xb0\xd0\xbb'
            '\xd0\xb8\xd1\x8f': 'Cosmic Anomaly',
            '\xd0\xa0\xd0\xa3\xd0\x94\xd0\x90: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe'
            '\xd0\xbd \xd0\xb4\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x87\xd0\xb8 \xd1\x80'
            '\xd1\x83\xd0\xb4\xd1\x8b': 'Ore Site',
            '\xd0\x93\xd0\x90\xd0\x97: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe\xd0\xbd '
            '\xd0\xb4\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x87\xd0\xb8 \xd0\xb3\xd0\xb0'
            '\xd0\xb7\xd0\xb0': 'Gas Site',
            '\xd0\x94\xd0\x90\xd0\x9d\xd0\x9d\xd0\xab\xd0\x95: \xd1\x80\xd0\xb0'
            '\xd0\xb9\xd0\xbe\xd0\xbd \xd1\x81\xd0\xb1\xd0\xbe\xd1\x80\xd0\xb0 '
            '\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd1\x85': 'Data Site',
            '\xd0\x90\xd0\xa0\xd0\xa2\xd0\x95\xd0\xa4\xd0\x90\xd0\x9a\xd0\xa2\xd0'
            '\xab: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe\xd0\xbd \xd0\xbf\xd0\xbe\xd0'
            '\xb8\xd1\x81\xd0\xba\xd0\xb0 \xd0\xb0\xd1\x80\xd1\x82\xd0\xb5\xd1'
            '\x84\xd0\xb0\xd0\xba\xd1\x82\xd0\xbe\xd0\xb2': 'Relic Site',
            '\xd0\xa7\xd0\xb5\xd1\x80\xd0\xb2\xd0\xbe\xd1\x82\xd0\xbe\xd1\x87\xd0'
            '\xb8\xd0\xbd\xd0\xb0': 'Wormhole',
            '\xd0\x9e\xd0\x9f\xd0\x90\xd0\xa1\xd0\x9d\xd0\x9e: \xd1\x80\xd0\xb0'
            '\xd0\xb9\xd0\xbe\xd0\xbd \xd0\xbf\xd0\xbe\xd0\xb2\xd1\x8b\xd1\x88'
            '\xd0\xb5\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xbe\xd0\xbf\xd0\xb0'
            '\xd1\x81\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd0\xb8': 'Combat Site',
            # German
            u'Kosmische Signatur': 'Cosmic Signature',
            u'Kosmische Anomalie': 'Cosmic Anomaly',
            u'Mineraliengebiet': 'Ore Site',
            u'Gasgebiet': 'Gas Site',
            u'Datengebiet': 'Data Site',
            u'Reliktgebiet': 'Relic Site',
            u'Wurmloch': 'Wormhole',
            u'Kampfgebiet': 'Combat Site',
            # Japanese
            '\xe5\xae\x87\xe5\xae\x99\xe3\x81\xae\xe3\x82\xb7\xe3\x82\xb0\xe3\x83'
            '\x8d\xe3\x83\x81\xe3\x83\xa3': 'Cosmic Signature',
            '\xe5\xae\x87\xe5\xae\x99\xe3\x81\xae\xe7\x89\xb9\xe7\x95\xb0\xe7\x82'
            '\xb9': 'Cosmic Anomaly',
            '\xe9\x89\xb1\xe7\x9f\xb3\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88':
                'Ore Site',
            '\xe3\x82\xac\xe3\x82\xb9\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88':
                'Gas Site',
            '\xe3\x83\x87\xe3\x83\xbc\xe3\x82\xbf\xe3\x82\xb5\xe3\x82\xa4\xe3'
            '\x83\x88': 'Data Site',
            '\xe9\x81\xba\xe7\x89\xa9\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88':
                'Relic Site',
            '\xe3\x83\xaf\xe3\x83\xbc\xe3\x83\xa0\xe3\x83\x9b\xe3\x83\xbc\xe3\x83'
            '\xab': 'Wormhole',
            '\xe6\x88\xa6\xe9\x97\x98\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88':
                'Combat Site',
        }
        try:
            text = TRANSLATE_DICT[client_text]
            return text
        except KeyError:
            return None


class MapPermission(models.Model):
    """Relates a user group to it's map permissions.

    Non-restricted groups will have change access to all maps.
    """
    group = models.ForeignKey(Group, related_name="mappermissions")
    map = models.ForeignKey(Map, related_name="grouppermissions")
    access = models.IntegerField(choices=((0, 'No Access'),
                                          (1, 'View Only'),
                                          (2, 'View / Change')))


class MapLog(models.Model):
    """Represents an action that has taken place on a map.

    This is used for pushing updates since last page load to clients.
    Includes things like adding a signature.
    """
    map = models.ForeignKey(Map, related_name="logentries")
    user = models.ForeignKey(User, related_name="maplogs")
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255)
    # Visible logs are pushed to clients as they ocurr
    # (e.g. system added to map)
    visible = models.BooleanField(default=False)

    def __unicode__(self):
        return ("Map: %s User: %s Action: %s Time: %s" %
                (self.map.name, self.user.username,
                 self.action, self.timestamp))


class Snapshot(models.Model):
    """Represents a snapshot of the JSON strings used to draw a map."""
    name = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='snapshots')
    json = models.TextField()
    description = models.CharField(max_length=255)


class Destination(models.Model):
    """Represents a corp-wide destination.

    Distance to this destination will be shown in the map."""
    system = models.ForeignKey(KSystem, related_name='destinations')
    user = models.ForeignKey(User, related_name='destinations', null=True)


class SiteSpawn(models.Model):
    """Contains the site spawn list for a site as HTML."""
    sysclass = models.IntegerField()
    sigtype = models.ForeignKey(SignatureType)
    sitename = models.CharField(max_length=255)
    spawns = models.TextField()

    def __unicode__(self):
        return self.sitename


# Model Forms

class InlineModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.pop('widget', forms.widgets.TextInput)
        super(InlineModelChoiceField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and not self.required:
            return None
        try:
            return self.queryset.filter(name=value).get()
        except self.queryset.model.DoesNotExist:
            raise forms.ValidationError(
                "Please enter a valid %s." %
                (self.queryset.model._meta.verbose_name,))


class MapForm(ModelForm):
    root = InlineModelChoiceField(
        queryset=System.objects.all(),
        widget=forms.TextInput(attrs={'class': 'systemAuto'}))

    class Meta:
        model = Map


class SignatureForm(ModelForm):
    """Form for adding a signature.

    This form should only be used with commit=False since it does not
    set the system or updated fields.
    """
    sigid = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-mini'}),
        label="ID:")

    sigtype = forms.ModelChoiceField(
        queryset=SignatureType.objects.all(),
        label="Type:",
        required=False)

    info = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-medium'}),
        label="Info:",
        required=False)

    sigtype.widget.attrs['class'] = 'input-small'

    class Meta:
        model = Signature
        fields = ('sigid', 'sigtype', 'info')
