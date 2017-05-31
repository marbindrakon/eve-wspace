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
from collections import defaultdict
from datetime import timedelta
from math import pow, sqrt
import datetime
import json

from core.utils import get_config
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
import pytz


class MapJSONGenerator(object):
    """Provides methods create a JSON representation of a Map.

    Instantiated with a map and user.
    Provides a method that returns the JSON representation of the map.
    """
    def __init__(self, map, user):
        self.map = map
        self.user = user
        self.pvp_threshold = int(get_config("MAP_PVP_THRESHOLD", user).value)
        self.npc_threshold = int(get_config("MAP_NPC_THRESHOLD", user).value)
        self.interest_time = int(get_config("MAP_INTEREST_TIME", user).value)

    def _get_interest_path(self):
        """Get all MapSystems contained in a path to a system of interest."""
        try:
            return self._interest_path
        except AttributeError:
            threshold = (datetime.datetime.now(pytz.utc) -
                         timedelta(minutes=self.interest_time))
            systems = []
            for system in self.map.systems.filter(
                    interesttime__gt=threshold).iterator():
                systems.extend(self.get_path_to_map_system(system))
            self._interest_path = systems
            return systems

    @staticmethod
    def get_cache_key(map_inst):
        return '%s_map' % map_inst.pk

    @staticmethod
    def get_path_to_map_system(system):
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
        """Get URL to system background icon.

        Takes a MapSystem and returns the appropriate icon to
        display on the map as a relative URL.
        """
        pvp_threshold = self.pvp_threshold
        npc_threshold = self.npc_threshold
        static_prefix = "%s" % (settings.STATIC_URL + "images/")
        if system.system.sysclass == 99:
            return static_prefix + "scan.png"
        
        if system.system.stfleets.filter(ended__isnull=True).exists():
            return static_prefix + "farm.png"

        if system.system.shipkills + system.system.podkills > pvp_threshold:
            return static_prefix + "pvp.png"

        if system.system.npckills > npc_threshold:
            return static_prefix + "carebears.png"

        # unscanned for >24h
        if not system.system.signatures.filter(modified_time__gte=(datetime.datetime.now(pytz.utc)-datetime.timedelta(days=1))).filter(sigtype__isnull=False).exists():
            return static_prefix + "scan.png"

        # partially scanned
        if system.system.signatures.filter(sigtype__isnull=True).exists():
            return static_prefix + "isis_scan.png"

        return None

    def system_to_dict(self, system, level_x, level_y):
        """Get dict representation of a system.

        Takes a MapSystem and X, Y data.
        Returns the dict of information to be passed to the map JS as JSON.
        """
        system_obj = system.system
        is_wspace = system_obj.is_wspace()
        system_dict = {
            'sysID': system_obj.pk,
            'Name': system_obj.name,
            'LevelX': level_x,
            'LevelY': level_y,
            'SysClass': system_obj.sysclass,
            'Friendly': system.friendlyname,
            'interest':
                system.interesttime and
                system.interesttime > datetime.datetime.now(pytz.utc) -
                timedelta(minutes=self.interest_time),
            'interestpath': system in self._get_interest_path(),
            'activePilots': len(system_obj.pilot_list),
            'pilot_list': [x[1][1] for x in system_obj.pilot_list.items()
                           if x[1][1] != "OOG Browser"],
            'iconImageURL': self.get_system_icon(system),
            'msID': system.pk,
            'backgroundImageURL': self.get_system_background(system),
            'effect': system_obj.wsystem.effect if is_wspace else None,
            'importance': system_obj.importance,
            'shattered':
                system_obj.wsystem.is_shattered if is_wspace else False,
        }

        if system.parentsystem:
            parent_wh = system.parent_wormhole
            system_dict.update({
                'ParentID': system.parentsystem.pk,
                'WhToParent': parent_wh.bottom_type.name,
                'WhFromParent': parent_wh.top_type.name,
                'WhMassStatus': parent_wh.mass_status,
                'WhTimeStatus': parent_wh.time_status,
                'WhTotalMass': parent_wh.max_mass,
                'WhJumpMass': parent_wh.jump_mass,
                'WhToParentBubbled': parent_wh.bottom_bubbled,
                'WhFromParentBubbled': parent_wh.top_bubbled,
                'whID': parent_wh.pk,
                'collapsed': bool(parent_wh.collapsed),
            })
        else:
            system_dict.update({
                'ParentID': None,
                'WhToParent': "",
                'WhFromParent': "",
                'WhTotalMass': None,
                'WhJumpMass': None,
                'WhMassStatus': None,
                'WhTimeStatus': None,
                'WhToParentBubbled': None,
                'WhFromParentBubbled': None,
                'whID': None,
                'collapsed': False,
            })

        return system_dict

    @staticmethod
    def get_system_background(system):
        """
        Takes a MapSystem and returns the appropriate background icon
        as a relative URL or None.
        """
        importance = system.system.importance
        if importance == 0:
            return None
        elif importance == 1:
            image = 'skull.png'
        elif importance == 2:
            image = 'mark.png'
        else:
            raise ValueError

        return "{0}images/{1}".format(settings.STATIC_URL, image)

    def get_systems_json(self):
        """Returns a JSON string representing the systems in a map."""
        cache_key = self.get_cache_key(self.map)
        systems = cache.get(cache_key)
        if systems is None:
            systems = self.create_syslist()
            cache.set(cache_key, systems, 15)

        user_locations_dict = cache.get('user_%s_locations' % self.user.pk)
        if user_locations_dict:
            user_img = "%s/images/mylocation.png" % (settings.STATIC_URL,)
            user_locations = [i[1][0] for i in user_locations_dict.items()]
            for system in systems:
                if (system['sysID'] in user_locations and
                        system['iconImageURL'] is None):
                    system['iconImageURL'] = user_img
        return json.dumps(systems, sort_keys=True)

    def create_syslist(self):
        """
        Return list of system dictionaries with appropriate x/y levels
        for map display.
        """
        # maps system ids to child/parent system ids
        children = defaultdict(list)
        # maps system ids to objects
        systems = dict()
        # maps system ids to priorities
        priorities = dict()

        for system in (self.map.systems.all()
                       .select_related('system', 'parentsystem',
                                       'parent_wormhole')
                       .iterator()):
            children[system.parentsystem_id].append(system.pk)
            systems[system.pk] = system
            priorities[system.pk] = system.display_order_priority

        # sort children by priority
        for l in children.values():
            l.sort(key=priorities.__getitem__)

        # actual map layout generation
        layout_gen = LayoutGenerator(children)
        system_positions = layout_gen.get_layout()

        # generate list of system dictionaries for conversion to JSON
        syslist = []
        for sys_id in layout_gen.processed:
            sys_obj = systems[sys_id]
            x, y = system_positions[sys_id]
            syslist.append(self.system_to_dict(sys_obj, x, y))

        return syslist


def get_wormhole_type(system1, system2):
    """Gets the one-way wormhole types between system1 and system2."""
    from Map.models import WormholeType
    source = "K"
    # Set the source and destination for system1 > system2
    if system1.is_wspace:
        source = str(system1.sysclass)
    if system1.sysclass == 7:
        source = "H"
    if system1.sysclass in [8, 9, 10, 11]:
        source = "NH"

    destination = system2.sysclass

    sourcewh = None

    if source == "H":
        if WormholeType.objects.filter(
                source="H", destination=destination).count() == 0:
            sourcewh = WormholeType.objects.filter(
                source="K", destination=destination).all()
        else:
            sourcewh = WormholeType.objects.filter(
                source="H", destination=destination).all()
    if source == "NH":
        if WormholeType.objects.filter(
                source="NH", destination=destination).count() == 0:
            sourcewh = WormholeType.objects.filter(
                source="K", destination=destination).all()
        else:
            sourcewh = WormholeType.objects.filter(
                source="NH", destination=destination).all()
    if source == "5" or source == "6":
        if WormholeType.objects.filter(
                source="Z", destination=destination).count() != 0:
            sourcewh = (WormholeType.objects
                        .filter(Q(source="Z") | Q(source='W'))
                        .filter(destination=destination).all())

    if sourcewh is None:
        sourcewh = (WormholeType.objects
                    .filter(Q(source=source) | Q(source='W'))
                    .filter(destination=destination).all())
    return sourcewh


def get_possible_wh_types(system1, system2):
    """Takes two systems and gets the possible wormhole types between them.

    For example, given system1 as highsec and system2 as C2, it should return
    R943 and B274. system1 is the source and system2 is the destination.
    Results are returned as lists because some combinations have
    multiple possibilities.

    Returns a dict in the format {system1: [R943,], system2: [B274,]}.
    """

    # Get System1 > System2

    forward = get_wormhole_type(system1, system2)

    # Get Reverse

    reverse = get_wormhole_type(system2, system1)

    result = {'system1': forward, 'system2': reverse}

    return result


def convert_signature_id(sigid):
    """Standardize the signature ID to XXX-XXX if info is available."""
    escaped_sigid = sigid.replace(' ', '').replace('-', '').upper()
    if len(escaped_sigid) == 6:
        return "%s-%s" % (escaped_sigid[:3], escaped_sigid[3:])
    else:
        return sigid.upper()


class RouteFinder(object):
    """Provides methods for finding distances between systems.

    Has methods for getting the shortest stargate jump route length,
    the light-year distance, and the shortest stargate route
    as a list of KSystem objects.
    """
    def __init__(self):
        from django.core.cache import cache
        if not cache.get('route_graph'):
            self._cache_graph()
        else:
            import pickle
            self.graph = pickle.loads(cache.get('route_graph'))

    @staticmethod
    def _get_ly_distance(sys1, sys2):
        """
        Gets the distance in light years between two systems.
        """
        x1 = sys1.x
        y1 = sys1.y
        z1 = sys1.z
        x2 = sys2.x
        y2 = sys2.y
        z2 = sys2.z

        distance = sqrt(pow(x1 - x2, 2) +
                        pow(y1 - y2, 2) +
                        pow(z1 - z2, 2)) / 9.4605284e+15
        return distance

    def ly_distance(self, sys1, sys2):
        return self._get_ly_distance(sys1, sys2)

    def route_as_ids(self, sys1, sys2):
        return self._find_route(sys1, sys2)

    def route(self, sys1, sys2):
        from Map.models import KSystem
        return [KSystem.objects.get(pk=sysid)
                for sysid in self._find_route(sys1, sys2)]

    def route_length(self, sys1, sys2):
        return len(self._find_route(sys1, sys2))

    def _cache_graph(self):
        from Map.models import KSystem
        from core.models import SystemJump
        from django.core.cache import cache
        import pickle
        import networkx as nx
        if not cache.get('route_graph'):
            graph = nx.Graph()
            for from_system in KSystem.objects.all():
                for to_system in (SystemJump.objects
                                  .filter(fromsystem=from_system.pk)):
                    graph.add_edge(from_system.pk, to_system.tosystem)
            cache.set('route_graph',
                      pickle.dumps(graph, pickle.HIGHEST_PROTOCOL), 0)
            self.graph = graph

    def _find_route(self, sys1, sys2):
        """
        Takes two system objects (can be KSystem or SystemData).
        Returns a list of system IDs that comprise the route.
        """
        import networkx as nx
        import pickle
        if not self.graph:
            from django.core.cache import cache
            if not cache.get('route_graph'):
                self._cache_graph()
                self.graph = pickle.loads(cache.get('route_graph'))
            else:
                self.graph = pickle.loads(cache.get('route_graph'))
        return nx.shortest_path(self.graph, source=sys1.pk, target=sys2.pk)


class LayoutGenerator(object):
    """Provides methods for generating the map layout."""
    def __init__(self, children):
        """Create new LayoutGenerator.

        children should be a dictionary of system ids as
                 keys and their child ids as values.
        """
        self.children = children
        self.positions = None
        self.occupied = [-1]

        # after processing is done, this contains the processed
        # system ids in drawing order
        self.processed = []

    def get_layout(self):
        """Create map layout.

        returns a dictionary containing x, y positions for
        the given system ids.
        """
        if self.positions is not None:
            return self.positions

        self.positions = {}
        root_node = self.children[None][0]
        self._place_node(root_node, 0, 0)
        return self.positions

    def _place_node(self, node_id, x, min_y):
        """Determine x, y position for a node.

        node_id: id of the node to be positioned
        x: x position (depth) of the node
        min_y: minimal y position of the node
               (can't be above parent nodes)

        returns: y offset relative to min_y
        """
        self.processed.append(node_id)

        # initially set y to the next free y in this column
        # or min_y, whichever is greater
        try:
            y_occupied = self.occupied[x]
        except IndexError:
            self.occupied.append(-1)
            y_occupied = -1
        y = max(min_y, y_occupied + 1)

        # position first child (and thus its children)
        # and move this node down if child moved down
        try:
            first_child = self.children[node_id][0]
            y += self._place_node(first_child, x + 1, y)
        except IndexError:
            pass  # node has no children, ignore that.

        # system position is now final, save it
        self.occupied[x] = y
        self.positions[node_id] = (x, y)

        # place the rest of the children
        for child in self.children[node_id][1:]:
            self._place_node(child, x + 1, y)

        return y - min_y
