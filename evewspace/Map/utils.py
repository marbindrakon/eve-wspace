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
#from Map.models import *
from django.conf import settings
import json
import datetime
from datetime import timedelta
import pytz
from django.contrib.sites.models import Site
from math import pow, sqrt
from core.models import SystemJump, Type, Location
from core.utils import get_config
from collections import OrderedDict
from django.core.cache import cache

class MapJSONGenerator(object):
    """
    A MapJSONGenerator is instantiated with a map and user. It provides
    a method that returns the JSON representation of the map.
    """

    def __init__(self, map, user):
        self.map = map
        self.user = user
        self.levelY = 0

    def get_path_to_map_system(self, system):
        """
        Returns a list of MapSystems on the route between the map root and
        the provided MapSystem.
        """
        systemlist = []
        parent = system
        while parent:
            systemlist.append(parent)
            if parent.parentsystem and not parent.parent_wormhole.collapsed:
                parent = parent.parentsystem
            else:
                parent = None
        return systemlist

    def get_system_icon(self, system):
        """
        Takes a MapSystem and returns the appropriate icon to display on the map
        as a realative URL.
        """
        pvp_threshold = int(get_config("MAP_PVP_THRESHOLD", self.user).value)
        npc_threshold = int(get_config("MAP_NPC_THRESHOLD", self.user).value)
        staticPrefix = "%s" % (settings.STATIC_URL + "images/")
        if system.system.active_pilots.filter(user=self.user).count():
            return staticPrefix + "mylocation.png"

        if system.system.stfleets.filter(ended__isnull=True).count() != 0:
            return staticPrefix + "farm.png"

        if system.system.shipkills + system.system.podkills > pvp_threshold:
            return staticPrefix + "pvp.png"

        if system.system.npckills > npc_threshold:
            return staticPrefix + "carebears.png"

        return None

    def system_to_dict(self, system, levelX):
        """
        Takes a MapSystem and X,Y data and returns the dict of information to be passed to
        the map JS as JSON.
        """
        interesttime = int(get_config("MAP_INTEREST_TIME", self.user).value)
        threshold = datetime.datetime.now(pytz.utc) - timedelta(minutes=interesttime)
        if system.interesttime and system.interesttime > threshold:
            interest = True
        else:
            interest = False
        if system.map.systems.filter(interesttime__gt=threshold).count() != 0:
            path = False
            for sys in system.map.systems.filter(interesttime__gt=threshold).all():
                if system in self.get_path_to_map_system(sys):
                    path = True
        else:
            path = False
        activity_estimate = (system.system.podkills + system.system.npckills +
                system.system.shipkills)
        from Map.models import WSystem
        if system.system.is_wspace():
            effect = WSystem.objects.get(pk=system.system.pk).effect
        else:
            effect = None
        if system.parentsystem:
            parentWH = system.parent_wormhole
            if parentWH.collapsed:
                collapsed = True
            else:
                collapsed = False
            result = {'sysID': system.system.pk, 'Name': system.system.name,
                    'LevelX': levelX,'activity': activity_estimate,
                    'LevelY': self.levelY, 'SysClass': system.system.sysclass,
                    'Friendly': system.friendlyname, 'interest': interest,
                    'interestpath': path, 'ParentID': system.parentsystem.pk,
                    'activePilots': system.system.active_pilots.count(),
                    'WhToParent': parentWH.bottom_type.name,
                    'WhFromParent': parentWH.top_type.name,
                    'WhMassStatus': parentWH.mass_status,
                    'WhTimeStatus': parentWH.time_status,
                    'WhToParentBubbled': parentWH.bottom_bubbled,
                    'WhFromParentBubbled': parentWH.top_bubbled,
                    'imageURL': self.get_system_icon(system),
                    'whID': parentWH.pk, 'msID': system.pk,
                    'effect': effect, 'collapsed': collapsed}
        else:
            result = {'sysID': system.system.pk, 'Name': system.system.name,
                    'LevelX': levelX, 'activity': activity_estimate,
                    'LevelY': self.levelY, 'SysClass': system.system.sysclass,
                    'Friendly': system.friendlyname, 'interest': interest,
                    'interestpath': path, 'ParentID': None,
                    'activePilots': system.system.active_pilots.count(),
                    'WhToParent': "", 'WhFromParent': "",
                    'WhMassStatus': None, 'WhTimeStatus': None,
                    'WhToParentBubbled': None, 'WhFromParentBubbled': None,
                    'imageURL': self.get_system_icon(system),
                    'whID': None, 'msID': system.pk,
                    'effect': effect, 'collapsed': False}
        return result


    def get_systems_json(self):
        """Returns a JSON string representing the systems in a map."""
        syslist = []
        root = self.map.systems.get(parentsystem__isnull=True)
        syslist.append(self.system_to_dict(root, 0))
        self.recursive_system_data_generator(root.childsystems.all(), syslist, 1)
        return json.dumps(syslist, sort_keys=True)


    def recursive_system_data_generator(self, mapSystems, syslist, levelX):
        """
        Prepares a list of MapSystem objects for conversion to JSON for map JS.
        Takes a queryset of MapSystems and the current list of systems prepared
        for JSON.
        """
        # We will need an index later, so let's enumerate the mapSystems
        enumSystems = enumerate(mapSystems, start=0)
        for item in enumSystems:
            i = item[0]
            system = item[1]
            if i > 0:
                self.levelY +=1
            syslist.append(self.system_to_dict(system, levelX))
            self.recursive_system_data_generator(system.childsystems.all(),
                    syslist, levelX + 1)


def get_wormhole_type(system1, system2):
    """Gets the one-way wormhole types between system1 and system2."""
    from Map.models import WormholeType
    source = "K"
    destination = "K"
    # Set the source and destination for system1 > system2
    if system1.sysclass < 7:
        source = str(system1.sysclass)
    if system1.sysclass == 7:
        source = "H"
    if system1.sysclass > 7:
        source = "NH"

    destination = system2.sysclass

    sourcewh = None

    if source == "H":
        if WormholeType.objects.filter(source="H",
                destination=destination).count() == 0:
            sourcewh = WormholeType.objects.filter(source="K",
                    destination=destination).all()
        else:
            sourcewh = WormholeType.objects.filter(source="H",
                    destination=destination).all()
    if source == "NH":
        if WormholeType.objects.filter(source="NH",
                destination=destination).count() == 0:
            sourcewh = WormholeType.objects.filter(source="K",
                    destination=destination).all()
        else:
            sourcewh = WormholeType.objects.filter(source="NH",
                    destination=destination).all()
    if source == "5" or source == "6":
        if WormholeType.objects.filter(source="Z",
                destination=destination).count() != 0:
            sourcewh = WormholeType.objects.filter(source="Z",
                    destination=destination).all()

    if sourcewh == None:
        sourcewh = WormholeType.objects.filter(source=source,
                destination=destination).all()
    return sourcewh


def get_possible_wh_types(system1, system2):
    """Takes two systems and gets the possible wormhole types between them.
    For example, given system1 as highsec and system2 as C2, it should return
    R943 and B274. system1 is the source and system2 is the destination.
    Results are returned as lists because some combinations have multiple possibilities.
    Returns a dict in the format {system1: [R943,], system2: [B274,]}.

    """

    # Get System1 > System2

    forward = get_wormhole_type(system1, system2)

    # Get Reverse

    reverse = get_wormhole_type(system2, system1)

    result = {'system1': forward, 'system2': reverse}

    return result


def convert_signature_id(sigid):
    """
    Standardize the signature ID to XXX-XXX if info is available.
    """
    escaped_sigid = sigid.replace(' ','').replace('-','').upper()
    if len(escaped_sigid) == 6:
        return "%s-%s" % (escaped_sigid[:3], escaped_sigid[3:])
    else:
        return sigid.upper()


class RouteFinder(object):
    """
    A RouteFinder object is created with two system objects and has methods
    for getting the shortest stargate jump route length, the light-year distance,
    and the shortest stargate route as a list of KSystem objects.
    """

    def __init__(self):
        from django.core.cache import cache
        if not cache.get('route_graph'):
            self._cache_graph()
        else:
            import cPickle
            self.graph = cPickle.loads(cache.get('route_graph'))

    def _get_ly_distance(self, sys1, sys2):
        """
        Gets the distance in light years between two systems.
        """
        x1 = sys1.x
        y1 = sys1.y
        z1 = sys1.z
        x2 = sys2.x
        y2 = sys2.y
        z2 = sys2.z

        distance = sqrt(pow(x1 - x2 ,2) + pow(y1-y2,2) + pow(z1-z2,2)) / 9.4605284e+15
        return distance

    def ly_distance(self, sys1, sys2):
        return self._get_ly_distance(sys1, sys2)

    def route_as_ids(self, sys1, sys2):
        return self._find_route(sys1, sys2)

    def route(self, sys1, sys2):
        from Map.models import KSystem
        return [KSystem.objects.get(pk=sysid) for sysid in self._find_route(sys1, sys2)]

    def route_length(self, sys1, sys2):
        return len(self._find_route(sys1, sys2))

    def _cache_graph(self):
        from Map.models import KSystem
        from core.models import SystemJump
        from django.core.cache import cache
        import cPickle
        import networkx as nx
        if not cache.get('route_graph'):
            graph = nx.Graph()
            for from_system in KSystem.objects.all():
                for to_system in SystemJump.objects.filter(fromsystem=from_system.pk):
                    graph.add_edge(from_system.pk, to_system.tosystem)
            cache.set('route_graph', cPickle.dumps(graph, cPickle.HIGHEST_PROTOCOL), 0)
            self.graph = graph

    def _find_route(self, sys1, sys2):
        """
        Takes two system objects (can be KSystem or SystemData).
        Returns a list of system IDs that comprise the route.
        """
        import networkx as nx
        import cPickle
        if not self.graph:
            if not cache.get('route_graph'):
                from django.core.cache import cache
                self._cache_graph()
                self.graph = cPickle.loads(cache.get('route_graph'))
            else:
                self.graph = cPickle.loads(cache.get('route_graph'))
        return nx.shortest_path(self.graph, source=sys1.pk, target=sys2.pk)
