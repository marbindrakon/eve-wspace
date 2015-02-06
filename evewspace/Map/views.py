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
from datetime import datetime, timedelta
import json
import csv
import pytz

from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views.decorators.cache import cache_page

from Map.models import *
from Map import utils, signals
from core.utils import get_config
from POS.models import POS

# Decorator to check map permissions. Takes request and map_id
# Permissions are 0 = None, 1 = View, 2 = Change
# When used without a permission=x specification, requires Change access


def require_map_permission(permission=2):
    def _dec(view_func):
        def _view(request, map_id, *args, **kwargs):
            current_map = get_object_or_404(Map, pk=map_id)
            if current_map.get_permission(request.user) < permission:
                raise PermissionDenied
            else:
                return view_func(request, map_id, *args, **kwargs)
        _view.__name__ = view_func.__name__
        _view.__doc__ = view_func.__doc__
        _view.__dict__ = view_func.__dict__
        return _view

    return _dec


@login_required
@require_map_permission(permission=1)
def get_map(request, map_id):
    """Get the map and determine if we have permissions to see it.
    If we do, then return a TemplateResponse for the map. If map does not
    exist, return 404. If we don't have permission, return PermissionDenied.
    """
    current_map = get_object_or_404(Map, pk=map_id)
    context = {
        'map': current_map,
        'access': current_map.get_permission(request.user),
    }
    return TemplateResponse(request, 'map.html', context)


@login_required
@require_map_permission(permission=1)
def map_checkin(request, map_id):
    # Initialize json return dict
    json_values = {}
    current_map = get_object_or_404(Map, pk=map_id)

    # AJAX requests should post a JSON datetime called loadtime
    # back that we use to get recent logs.
    if 'loadtime' not in request.POST:
        return HttpResponse(json.dumps({'error': "No loadtime"}),
                            mimetype="application/json")
    time_string = request.POST['loadtime']

    load_time = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S.%f")
    load_time = load_time.replace(tzinfo=pytz.utc)

    if request.is_igb_trusted:
        dialog_html = _checkin_igb_trusted(request, current_map)
        if dialog_html is not None:
            json_values.update({'dialogHTML': dialog_html})
    log_list = MapLog.objects.filter(timestamp__gt=load_time,
                                          visible=True,
                                          map=current_map)

    log_string = render_to_string('log_div.html', {'logs': log_list})
    json_values.update({'logs': log_string})

    return HttpResponse(json.dumps(json_values), mimetype="application/json")



@login_required
@require_map_permission(permission=1)
def map_refresh(request, map_id):
    """
    Returns an HttpResponse with the updated systemJSON for an asynchronous
    map refresh.
    """
    if not request.is_ajax():
        raise PermissionDenied
    current_map = get_object_or_404(Map, pk=map_id)
    result = [
        datetime.strftime(datetime.now(pytz.utc),
                          "%Y-%m-%d %H:%M:%S.%f"),
        utils.MapJSONGenerator(current_map,
                               request.user).get_systems_json()
    ]
    return HttpResponse(json.dumps(result))


def _checkin_igb_trusted(request, current_map):
    """
    Runs the specific code for the case that the request came from an igb that
    trusts us, returns None if no further action is required, returns a string
    containing the html for a system add dialog if we detect that a new system
    needs to be added
    """
    can_edit = current_map.get_permission(request.user) == 2
    current_location = (request.eve_systemid, request.eve_charname,
            request.eve_shipname, request.eve_shiptypename)
    char_cache_key = 'char_%s_location' % request.eve_charid
    old_location = cache.get(char_cache_key)
    result = None
    current_system = get_object_or_404(System, pk=current_location[0])
    silent_map = request.POST.get('silent', 'false') == 'true'
    kspace_map = request.POST.get('kspace', 'false') == 'true'

    if old_location != current_location:
        if old_location:
            old_system = get_object_or_404(System, pk=old_location[0])
            old_system.remove_active_pilot(request.eve_charid)
        request.user.update_location(current_system.pk,
                request.eve_charid, request.eve_charname, request.eve_shipname,
                request.eve_shiptypename)
        cache.set(char_cache_key, current_location, 60 * 5)
    #Conditions for the system to be automagically added to the map.
        if (can_edit and
            old_location and
            old_system in current_map
            and current_system not in current_map
            and not _is_moving_from_kspace_to_kspace(old_system,
                current_system, kspace_map)
        ):
            context = {
                'oldsystem': current_map.systems.filter(
                    system=old_system).all()[0],
                'newsystem': current_system,
                'wormholes': utils.get_possible_wh_types(old_system,
                                                         current_system),
            }

            if request.POST.get('silent', 'false') != 'true':
                result = render_to_string('igb_system_add_dialog.html', context,
                                      context_instance=RequestContext(request))
            else:
                new_ms = current_map.add_system(request.user, current_system, '',
                        context['oldsystem'])
                k162_type = WormholeType.objects.get(name="K162")
                new_ms.connect_to(context['oldsystem'], k162_type, k162_type)
                result = 'silent'
    else:
        cache.set(char_cache_key, current_location, 60 * 5)
        # Use add_active_pilot to refresh the user's record in the global
        # location cache
        current_system.add_active_pilot(request.user.username,
                request.eve_charid, request.eve_charname, request.eve_shipname,
                request.eve_shiptypename)

    return result


def _is_moving_from_kspace_to_kspace(old_system, current_system, kspace_map):
    """
    returns whether we are moving through kspace
    :param old_system:
    :param current_system:
    :return:
    """
    if not kspace_map:
        return old_system.is_kspace() and current_system.is_kspace()
    else:
        # K-space mapping enabled, pass the check
        return False


def get_system_context(ms_id, user):
    map_system = get_object_or_404(MapSystem, pk=ms_id)
    if map_system.map.get_permission(user) == 2:
        can_edit = True
    else:
        can_edit = False
    #If map_system represents a k-space system get the relevant KSystem object
    if map_system.system.is_kspace():
        system = map_system.system.ksystem
    else:
        system = map_system.system.wsystem

    scan_threshold = datetime.now(pytz.utc) - timedelta(
        hours=int(get_config("MAP_SCAN_WARNING", None).value)
    )
    interest_offset = int(get_config("MAP_INTEREST_TIME", None).value)
    interest_threshold = (datetime.now(pytz.utc)
                          - timedelta(minutes=interest_offset))

    scan_warning = system.lastscanned < scan_threshold
    if interest_offset > 0:
        interest = (map_system.interesttime and
                    map_system.interesttime > interest_threshold)
    else:
        interest = map_system.interesttime
        # Include any SiteTracker fleets that are active
    st_fleets = map_system.system.stfleets.filter(ended=None).all()
    locations = cache.get('sys_%s_locations' % map_system.system.pk)
    if not locations:
        locations = {}
    return {'system': system, 'mapsys': map_system,
            'scanwarning': scan_warning, 'isinterest': interest,
            'stfleets': st_fleets, 'locations': locations,
            'can_edit': can_edit}


@login_required
@require_map_permission(permission=2)
def add_system(request, map_id):
    """
    AJAX view to add a system to a current_map. Requires POST containing:
       topMsID: map_system ID of the parent map_system
       bottomSystem: Name of the new system
       topType: WormholeType name of the parent side
       bottomType: WormholeType name of the new side
       timeStatus: Wormhole time status integer value
       massStatus: Wormhole mass status integer value
       topBubbled: 1 if Parent side bubbled
       bottomBubbled: 1 if new side bubbled
       friendlyName: Friendly name for the new map_system
    """
    if not request.is_ajax():
        raise PermissionDenied
    try:
        # Prepare data
        current_map = Map.objects.get(pk=map_id)
        top_ms = MapSystem.objects.get(pk=request.POST.get('topMsID'))
        bottom_sys = System.objects.get(
            name=request.POST.get('bottomSystem')
        )
        top_type = WormholeType.objects.get(
            name=request.POST.get('topType')
        )
        bottom_type = WormholeType.objects.get(
            name=request.POST.get('bottomType')
        )
        time_status = int(request.POST.get('timeStatus'))
        mass_status = int(request.POST.get('massStatus'))
        if request.POST.get('topBubbled', '0') != "0":
            top_bubbled = True
        else:
            top_bubbled = False
        if request.POST.get('bottomBubbled', '0') != "0":
            bottom_bubbled = True
        else:
            bottom_bubbled = False
        # Add System
        bottom_ms = current_map.add_system(
            request.user, bottom_sys,
            request.POST.get('friendlyName'), top_ms
        )
        # Add Wormhole
        bottom_ms.connect_to(top_ms, top_type, bottom_type, top_bubbled,
                             bottom_bubbled, time_status, mass_status)
        current_map.clear_caches()
        return HttpResponse()
    except ObjectDoesNotExist:
        return HttpResponse(status=400)


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def remove_system(request, map_id, ms_id):
    """
    Removes the supplied map_system from a map.
    """
    system = get_object_or_404(MapSystem, pk=ms_id)
    system.remove_system(request.user)
    return HttpResponse()


@login_required
@require_map_permission(permission=2)
def promote_system(request, map_id, ms_id):
    """
    Promotes the MapSystem to map root and truncates other chains.
    """
    map_obj = get_object_or_404(Map, pk=map_id)
    if map_obj.truncate_allowed:
        system = get_object_or_404(MapSystem, pk=ms_id)
        system.promote_system(request.user)
        return HttpResponse()
    else:
        raise PermissionDenied

# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=1)
def system_details(request, map_id, ms_id):
    """
    Returns a html div representing details of the System given by ms_id in
    map map_id
    """
    if not request.is_ajax():
        raise PermissionDenied

    return render(request, 'system_details.html',
            get_system_context(ms_id, request.user))


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=1)
def system_menu(request, map_id, ms_id):
    """
    Returns the html for system menu
    """
    if not request.is_ajax():
        raise PermissionDenied

    return render(request, 'system_menu.html',
            get_system_context(ms_id, request.user))


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=1)
def system_tooltips(request, map_id):
    """
    Returns the system tooltips for map_id
    """
    if not request.is_ajax():
        raise PermissionDenied
    cache_key = 'map_%s_sys_tooltip' % map_id
    cached_tips = cache.get(cache_key)
    if not cached_tips:
        ms_list = MapSystem.objects.filter(map_id=map_id)\
                        .select_related('parent_wormhole', 'system__region')\
                        .iterator()
        new_tips =  render_to_string('system_tooltip.html',
                {'map_systems': ms_list}, RequestContext(request))
        cache.set(cache_key, new_tips, 60)
        return HttpResponse(new_tips)
    else:
        return HttpResponse(cached_tips)

# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=1)
def wormhole_tooltips(request, map_id):
    """Takes a POST request from AJAX with a Wormhole ID and renders the
    wormhole tooltip for that ID to response.

    """
    if not request.is_ajax():
        raise PermissionDenied
    cache_key = 'map_%s_wh_tooltip' % map_id
    cached_tips = cache.get(cache_key)
    if not cached_tips:
        cur_map = get_object_or_404(Map, pk=map_id)
        ms_list = MapSystem.objects.filter(map=cur_map).all()
        whs = Wormhole.objects.filter(top__in=ms_list).all()
        new_tips = render_to_string('wormhole_tooltip.html',
                {'wormholes': whs}, RequestContext(request))
        cache.set(cache_key, new_tips, 60)
        return HttpResponse(new_tips)
    else:
        return HttpResponse(cached_tips)


# noinspection PyUnusedLocal
@login_required()
@require_map_permission(permission=2)
def collapse_system(request, map_id, ms_id):
    """
    Mark the system as collapsed.
    """
    if not request.is_ajax():
        raise PermissionDenied

    map_sys = get_object_or_404(MapSystem, pk=ms_id)
    parent_wh = map_sys.parent_wormhole
    parent_wh.collapsed = True
    parent_wh.save()
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required()
@require_map_permission(permission=2)
def resurrect_system(request, map_id, ms_id):
    """
    Unmark the system as collapsed.
    """
    if not request.is_ajax():
        raise PermissionDenied

    map_sys = get_object_or_404(MapSystem, pk=ms_id)
    parent_wh = map_sys.parent_wormhole
    parent_wh.collapsed = False
    parent_wh.save()
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required()
@require_map_permission(permission=2)
def mark_scanned(request, map_id, ms_id):
    """Takes a POST request from AJAX with a system ID and marks that system
    as scanned.

    """
    if request.is_ajax():
        map_system = get_object_or_404(MapSystem, pk=ms_id)
        map_system.system.lastscanned = datetime.now(pytz.utc)
        map_system.system.save()
        return HttpResponse()
    else:
        raise PermissionDenied

# noinspection PyUnusedLocal
@login_required()
@require_map_permission(permission=2)
def set_importance(request,map_id, ms_id):
    """Takes a POST request from AJAX with a system ID and marks that system
    's importance

    """
    if request.is_ajax():
        map_system = get_object_or_404(MapSystem, pk=ms_id)
        imp = request.REQUEST.get('importance',0)
        if imp >= 0 and imp <= 2:
            map_system.system.importance = imp
            map_system.system.save()
            if imp == 1:
                map_system.map.add_log(request.user, "Danger in %s (%s)"
                                    % (map_system.system.name,
                                        map_system.friendlyname))
        return HttpResponse()
    else:
        raise PermissionDenied

# noinspection PyUnusedLocal
@login_required()
def manual_location(request, map_id, ms_id):
    """Takes a POST request form AJAX with a System ID and marks the user as
    being active in that system.

    """
    if not request.is_ajax():
        raise PermissionDenied
    user_locations = cache.get('user_%s_locations' % request.user.pk)
    if user_locations:
        old_location = user_locations.pop(request.user.pk, None)
        if old_location:
            old_sys = get_object_or_404(System, pk=old_location[0])
            old_sys.remove_active_pilot(request.user.pk)
    map_sys = get_object_or_404(MapSystem, pk=ms_id)
    map_sys.system.add_active_pilot(request.user.username, request.user.pk,
            'OOG Browser', 'Unknown', 'Unknown')
    request.user.update_location(map_sys.system.pk, request.user.pk,
            'OOG Browser', 'Unknown', 'Unknown')
    map_sys.map.clear_caches()
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required()
@require_map_permission(permission=2)
def set_interest(request, map_id, ms_id):
    """Takes a POST request from AJAX with an action and marks that system
    as having either utcnow or None as interesttime. The action can be either
    "set" or "remove".

    """
    if request.is_ajax():
        action = request.POST.get("action", "none")
        if action == "none":
            raise Http404
        system = get_object_or_404(MapSystem, pk=ms_id)
        if action == "set":
            system.interesttime = datetime.now(pytz.utc)
            system.save()
            return HttpResponse()
        if action == "remove":
            system.interesttime = None
            system.save()
            return HttpResponse()
        system.map.clear_caches()
        return HttpResponse(status=418)
    else:
        raise PermissionDenied


def _translate_client_string(client_text):
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
            '\xd0\x98\xd1\x81\xd1\x82\xd0\xbe\xd1\x87\xd0\xbd\xd0\xb8\xd0\xba\xd0\xb8 \xd1\x81\xd0\xb8\xd0\xb3\xd0\xbd\xd0\xb0\xd0\xbb\xd0\xbe\xd0\xb2': 'Cosmic Signature',
            '\xd0\x9a\xd0\xbe\xd1\x81\xd0\xbc\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd0\xb0\xd0\xbd\xd0\xbe\xd0\xbc\xd0\xb0\xd0\xbb\xd0\xb8\xd1\x8f': 'Cosmic Anomaly',
            '\xd0\xa0\xd0\xa3\xd0\x94\xd0\x90: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe\xd0\xbd \xd0\xb4\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x87\xd0\xb8 \xd1\x80\xd1\x83\xd0\xb4\xd1\x8b': 'Ore Site',
            '\xd0\x93\xd0\x90\xd0\x97: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe\xd0\xbd \xd0\xb4\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x87\xd0\xb8 \xd0\xb3\xd0\xb0\xd0\xb7\xd0\xb0': 'Gas Site',
            '\xd0\x94\xd0\x90\xd0\x9d\xd0\x9d\xd0\xab\xd0\x95: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe\xd0\xbd \xd1\x81\xd0\xb1\xd0\xbe\xd1\x80\xd0\xb0 \xd0\xb4\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd1\x85': 'Data Site',
            '\xd0\x90\xd0\xa0\xd0\xa2\xd0\x95\xd0\xa4\xd0\x90\xd0\x9a\xd0\xa2\xd0\xab: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe\xd0\xbd \xd0\xbf\xd0\xbe\xd0\xb8\xd1\x81\xd0\xba\xd0\xb0 \xd0\xb0\xd1\x80\xd1\x82\xd0\xb5\xd1\x84\xd0\xb0\xd0\xba\xd1\x82\xd0\xbe\xd0\xb2': 'Relic Site',
            '\xd0\xa7\xd0\xb5\xd1\x80\xd0\xb2\xd0\xbe\xd1\x82\xd0\xbe\xd1\x87\xd0\xb8\xd0\xbd\xd0\xb0': 'Wormhole',
            '\xd0\x9e\xd0\x9f\xd0\x90\xd0\xa1\xd0\x9d\xd0\x9e: \xd1\x80\xd0\xb0\xd0\xb9\xd0\xbe\xd0\xbd \xd0\xbf\xd0\xbe\xd0\xb2\xd1\x8b\xd1\x88\xd0\xb5\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xbe\xd0\xbf\xd0\xb0\xd1\x81\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd0\xb8': 'Combat Site',
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
            '\xe5\xae\x87\xe5\xae\x99\xe3\x81\xae\xe3\x82\xb7\xe3\x82\xb0\xe3\x83\x8d\xe3\x83\x81\xe3\x83\xa3': 'Cosmic Signature',
            '\xe5\xae\x87\xe5\xae\x99\xe3\x81\xae\xe7\x89\xb9\xe7\x95\xb0\xe7\x82\xb9': 'Cosmic Anomaly',
            '\xe9\x89\xb1\xe7\x9f\xb3\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88': 'Ore Site',
            '\xe3\x82\xac\xe3\x82\xb9\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88': 'Gas Site',
            '\xe3\x83\x87\xe3\x83\xbc\xe3\x82\xbf\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88': 'Data Site',
            '\xe9\x81\xba\xe7\x89\xa9\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88': 'Relic Site',
            '\xe3\x83\xaf\xe3\x83\xbc\xe3\x83\xa0\xe3\x83\x9b\xe3\x83\xbc\xe3\x83\xab': 'Wormhole',
            '\xe6\x88\xa6\xe9\x97\x98\xe3\x82\xb5\xe3\x82\xa4\xe3\x83\x88': 'Combat Site'
            }
    try:
        text = TRANSLATE_DICT[client_text]
        return text
    except KeyError:
        return None


def _update_sig_from_tsv(signature, row):
    COL_SIG = 0
    COL_SIG_TYPE = 3
    COL_SIG_GROUP = 2
    COL_SIG_SCAN_GROUP = 1
    COL_SIG_STRENGTH = 4
    COL_DISTANCE = 5
    info = row[COL_SIG_TYPE]
    updated = False
    sig_type = None
    debug_text = row[COL_SIG_SCAN_GROUP]
    scan_group = _translate_client_string(row[COL_SIG_SCAN_GROUP])
    if (scan_group == "Cosmic Signature"
        or scan_group == "Cosmic Anomaly"
       ):
        try:
            sig_type_name = _translate_client_string(row[COL_SIG_GROUP])
            sig_type = SignatureType.objects.get(
                    longname=sig_type_name)
        except:
            sig_type = None
    else:
        sig_type = None

    if sig_type:
        updated = True

    if sig_type:
        signature.sigtype = sig_type
    signature.updated = updated or signature.updated
    if info:
        signature.info = info
    if signature.info == None:
        signature.info = ''

    return signature


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def bulk_sig_import(request, map_id, ms_id):
    """
    GET gets a bulk signature import form. POST processes it, creating sigs
    with blank info and type for each sig ID detected.
    """


    if not request.is_ajax():
        raise PermissionDenied
    map_system = get_object_or_404(MapSystem, pk=ms_id)
    k = 0
    if request.method == 'POST':
        reader = csv.reader(request.POST.get('paste', '').decode(
            ).splitlines(), delimiter="\t")
        COL_SIG = 0
        COL_STRENGTH = 4
        for row in reader:
            # To prevent pasting of POSes into the sig importer, make sure
            # the strength column is present
            try:
                test_var = row[COL_STRENGTH]
            except IndexError:
                return HttpResponse('A valid signature paste was not found',
                        status=400)
            if k < 75:
                sig_id = utils.convert_signature_id(row[COL_SIG])
                sig = Signature.objects.get_or_create(sigid=sig_id,
                        system=map_system.system)[0]
                sig = _update_sig_from_tsv(sig, row)
                sig.modified_by = request.user
                sig.save()
                signals.signature_update.send_robust(sig, user=request.user,
                                                 map=map_system.map,
                                                 signal_strength=row[COL_STRENGTH])

                k += 1
        map_system.map.add_log(request.user,
                              "Imported %s signatures for %s(%s)."
                              % (k, map_system.system.name,
                                 map_system.friendlyname), True)
        map_system.system.lastscanned = datetime.now(pytz.utc)
        map_system.system.save()
        return HttpResponse()
    else:
        return TemplateResponse(request, "bulk_sig_form.html",
                                {'mapsys': map_system})


@login_required
@require_map_permission(permission=2)
def toggle_sig_owner(request, map_id, ms_id, sig_id=None):
    if not request.is_ajax():
        raise PermissionDenied
    sig = get_object_or_404(Signature, pk=sig_id)
    sig.toggle_ownership(request.user)
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=1)
def edit_signature(request, map_id, ms_id, sig_id=None):
    """
    GET gets a pre-filled edit signature form.
    POST updates the signature with the new information and returns a
    blank add form.
    """
    if not request.is_ajax():
        raise PermissionDenied
    map_system = get_object_or_404(MapSystem, pk=ms_id)
    # If the user can't edit signatures, return a blank response
    if map_system.map.get_permission(request.user) != 2:
        return HttpResponse()
    action = None
    if sig_id != None:
        signature = get_object_or_404(Signature, pk=sig_id)
        created = False
        if not signature.owned_by:
            signature.toggle_ownership(request.user)
    if request.method == 'POST':
        form = SignatureForm(request.POST)
        if form.is_valid():
            ingame_id = utils.convert_signature_id(form.cleaned_data['sigid'])
            if sig_id == None:
                signature, created = Signature.objects.get_or_create(
                            system=map_system.system, sigid=ingame_id)

            signature.sigid = ingame_id
            signature.updated = True
            signature.info = form.cleaned_data['info']
            if request.POST['sigtype'] != '':
                sigtype = form.cleaned_data['sigtype']
            else:
                sigtype = None
            signature.sigtype = sigtype
            signature.modified_by = request.user
            signature.save()
            map_system.system.lastscanned = datetime.now(pytz.utc)
            map_system.system.save()
            if created:
                action = 'Created'
            else:
                action = 'Updated'
            if signature.owned_by:
                signature.toggle_ownership(request.user)
            map_system.map.add_log(request.user,
                                   "%s signature %s in %s (%s)" %
                                   (action, signature.sigid, map_system.system.name,
                                    map_system.friendlyname))
            signals.signature_update.send_robust(signature, user=request.user,
                                                 map=map_system.map)
        else:
            return TemplateResponse(request, "edit_sig_form.html",
                                    {'form': form,
                                    'system': map_system, 'sig': signature})
    form = SignatureForm()
    if sig_id == None or action == 'Updated':
        return TemplateResponse(request, "add_sig_form.html",
                        {'form': form, 'system': map_system})
    else:
        return TemplateResponse(request, "edit_sig_form.html",
                                {'form': SignatureForm(instance=signature),
                                'system': map_system, 'sig': signature})


# noinspection PyUnusedLocal
@login_required()
@require_map_permission(permission=1)
@cache_page(1)
def get_signature_list(request, map_id, ms_id):
    """
    Determines the proper escalationThreshold time and renders
    system_signatures.html
    """
    if not request.is_ajax():
        raise PermissionDenied
    system = get_object_or_404(MapSystem, pk=ms_id)
    escalation_downtimes = int(get_config("MAP_ESCALATION_BURN",
                                          request.user).value)
    return TemplateResponse(request, "system_signatures.html",
                            {'system': system,
                            'downtimes': escalation_downtimes})


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def mark_signature_cleared(request, map_id, ms_id, sig_id):
    """
    Marks a signature as having its NPCs cleared.
    """
    if not request.is_ajax():
        raise PermissionDenied
    sig = get_object_or_404(Signature, pk=sig_id)
    sig.clear_rats()
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def escalate_site(request, map_id, ms_id, sig_id):
    """
    Marks a site as having been escalated.
    """
    if not request.is_ajax():
        raise PermissionDenied
    sig = get_object_or_404(Signature, pk=sig_id)
    sig.escalate()
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def activate_signature(request, map_id, ms_id, sig_id):
    """
    Marks a site activated.
    """
    if not request.is_ajax():
        raise PermissionDenied
    sig = get_object_or_404(Signature, pk=sig_id)
    sig.activate()
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def delete_signature(request, map_id, ms_id, sig_id):
    """
    Deletes a signature.
    """
    if not request.is_ajax():
        raise PermissionDenied
    map_system = get_object_or_404(MapSystem, pk=ms_id)
    sig = get_object_or_404(Signature, pk=sig_id)
    sig.delete()
    map_system.map.add_log(request.user, "Deleted signature %s in %s (%s)."
                           % (sig.sigid, map_system.system.name,
                              map_system.friendlyname))
    return HttpResponse()


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def manual_add_system(request, map_id, ms_id):
    """
    A GET request gets a blank add system form with the provided MapSystem
    as top system. The form is then POSTed to the add_system view.
    """
    if request.is_igb_trusted:
        current_system = System.objects.get(name=request.eve_systemname)
    else:
        current_system = ""
    top_map_system = get_object_or_404(MapSystem, pk=ms_id)
    systems = System.objects.all()
    wormholes = WormholeType.objects.all()
    return render(request, 'add_system_box.html',
                  {'topMs': top_map_system, 'sysList': systems,
                   'whList': wormholes,'newsystem': current_system})


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def edit_system(request, map_id, ms_id):
    """
    A GET request gets the edit system dialog pre-filled with current
    information.
    A POST request saves the posted data as the new information.
        POST values are friendlyName, info, and occupied.
    """
    if not request.is_ajax():
        raise PermissionDenied
    map_system = get_object_or_404(MapSystem, pk=ms_id)
    if request.method == 'GET':
        occupied = map_system.system.occupied.replace("<br />", "\n")
        info = map_system.system.info.replace("<br />", "\n")
        return TemplateResponse(request, 'edit_system.html',
                                {'mapsys': map_system,
                                'occupied': occupied, 'info': info}
                                )
    if request.method == 'POST':
        map_system.friendlyname = request.POST.get('friendlyName', '')
        map_system.system.info = request.POST.get('info', '')
        map_system.system.occupied = request.POST.get('occupied', '')
        map_system.system.importance = request.POST.get('importance', '0')
        map_system.system.save()
        map_system.save()
        map_system.map.add_log(request.user, "Edited System: %s (%s)"
                               % (map_system.system.name,
                                  map_system.friendlyname))
        return HttpResponse()
    raise PermissionDenied


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=2)
def edit_wormhole(request, map_id, wh_id):
    """
    A GET request gets the edit wormhole dialog pre-filled with current info.
    A POST request saves the posted data as the new info.
    POST values are topType, bottomType, massStatus, timeStatus, topBubbled,
    and bottomBubbled.
    """
    if not request.is_ajax():
        raise PermissionDenied
    wormhole = get_object_or_404(Wormhole, pk=wh_id)
    if request.method == 'GET':
        return TemplateResponse(request, 'edit_wormhole.html',
                                {'wormhole': wormhole}
                                )
    if request.method == 'POST':
        wormhole.mass_status = int(request.POST.get('massStatus', 0))
        wormhole.time_status = int(request.POST.get('timeStatus', 0))
        wormhole.top_type = get_object_or_404(
            WormholeType,
            name=request.POST.get('topType', 'K162')
        )
        wormhole.bottom_type = get_object_or_404(
            WormholeType,
            name=request.POST.get('bottomType', 'K162')
        )
        wormhole.top_bubbled = request.POST.get('topBubbled', '1') == '1'
        wormhole.bottom_bubbled = request.POST.get('bottomBubbled', '1') == '1'
        wormhole.save()
        wormhole.map.add_log(request.user,
                            ("Updated the wormhole between %s(%s) and %s(%s)."
                             % (wormhole.top.system.name,
                                wormhole.top.friendlyname,
                                wormhole.bottom.system.name,
                                wormhole.bottom.friendlyname)))
        return HttpResponse()

    raise PermissiondDenied


@permission_required('Map.add_map')
def create_map(request):
    """
    This function creates a map and then redirects to the new map.
    """
    if request.method == 'POST':
        form = MapForm(request.POST)
        if form.is_valid():
            new_map = form.save()
            new_map.add_log(request.user, "Created the %s map." % new_map.name)
            new_map.add_system(request.user, new_map.root, "Root", None)
            return HttpResponseRedirect(reverse('Map.views.get_map',
                                                kwargs={'map_id': new_map.pk}))
        else:
            return TemplateResponse(request, 'new_map.html', {'form': form})
    else:
        form = MapForm
        return TemplateResponse(request, 'new_map.html', {'form': form, })

@permission_required('Map.add_map')
def import_map(request):
    """
    Import a map from a YAML export.
    """
    if request.method == 'POST':
        yaml_string = request.POST.get('yaml_string', None)
        if not yaml_string:
            return TemplateResponse(request, 'import_map.html',
                    {'error': 'Import text cannot be blank!'})
        try:
            new_map = Map.yaml_import(request.user, yaml_string)
        except Exception as ex:
            return TemplateResponse(request, 'import_map.html',
                    {'error': 'The map failed to import: %s' % repr(ex)})
        return HttpResponseRedirect(reverse('Map.views.get_map',
            kwargs={'map_id': new_map.pk}))
    else:
        return TemplateResponse(request, 'import_map.html')

@login_required
@require_map_permission(permission=1)
def export_map(request, map_id):
    """
    Exports a map as YAML.
    """
    map_obj = get_object_or_404(Map, pk=map_id)
    map_obj.add_log(user=request.user, action='Exported the map to YAML.',
            visible=True)
    return TemplateResponse(request, 'export_map_dialog.html',
            {'yaml_string': map_obj.as_yaml()})

def _sort_destinations(destinations):
    """
    Takes a list of destination tuples and returns the same list, sorted in order of the jumps.
    """
    results = []
    onVal = 0

    for dest in destinations:
        if len(results) == 0:
            results.append(dest)
        else:
            while onVal <= len(results):
                if onVal == len(results):
                    results.append(dest)
                    onVal = 0
                    break
                else:
                    if dest[1] > results[onVal][1]:
                        onVal += 1
                    else:
                        results.insert(onVal, dest)
                        onVal = 0
                        break
    return results

# noinspection PyUnusedLocal
@require_map_permission(permission=1)
def destination_list(request, map_id, ms_id):
    """
    Returns the destinations of interest tuple for K-space systems and
    a blank response for w-space systems.
    """
    if not request.is_ajax():
        raise PermissionDenied
    destinations = Destination.objects.filter(Q(user=None) |
                                              Q(user=request.user))
    map_system = get_object_or_404(MapSystem, pk=ms_id)
    try:
        system = KSystem.objects.get(pk=map_system.system.pk)
        rf = utils.RouteFinder()
        result = []
        for destination in destinations:
            result.append((destination.system,
                           rf.route_length(system,
                                           destination.system) - 1,
                           round(rf.ly_distance(system,
                                        destination.system), 3)
                           ))
    except ObjectDoesNotExist:
        return HttpResponse()
    return render(request, 'system_destinations.html',
                  {'system': system, 'destinations': _sort_destinations(result)})


# noinspection PyUnusedLocal
def site_spawns(request, map_id, ms_id, sig_id):
    """
    Returns the spawns for a given signature and system.
    """
    sig = get_object_or_404(Signature, pk=sig_id)
    spawns = SiteSpawn.objects.filter(sigtype=sig.sigtype).all()
    if spawns[0].sysclass != 0:
        spawns = SiteSpawn.objects.filter(sigtype=sig.sigtype,
                                          sysclass=sig.system.sysclass).all()
    return render(request, 'site_spawns.html', {'spawns': spawns})


#########################
#Settings Views         #
#########################
@permission_required('Map.map_admin')
def general_settings(request):
    """
    Returns and processes the general settings section.
    """
    npc_threshold = get_config("MAP_NPC_THRESHOLD", None)
    pvp_threshold = get_config("MAP_PVP_THRESHOLD", None)
    scan_threshold = get_config("MAP_SCAN_WARNING", None)
    interest_time = get_config("MAP_INTEREST_TIME", None)
    escalation_burn = get_config("MAP_ESCALATION_BURN", None)
    if request.method == "POST":
        scan_threshold.value = int(request.POST['scanwarn'])
        interest_time.value = int(request.POST['interesttimeout'])
        pvp_threshold.value = int(request.POST['pvpthreshold'])
        npc_threshold.value = int(request.POST['npcthreshold'])
        escalation_burn.value = int(request.POST['escdowntimes'])
        scan_threshold.save()
        interest_time.save()
        pvp_threshold.save()
        npc_threshold.save()
        escalation_burn.save()
        return HttpResponse()
    return TemplateResponse(
        request, 'general_settings.html',
        {'npcthreshold': npc_threshold.value,
         'pvpthreshold': pvp_threshold.value,
         'scanwarn': scan_threshold.value,
         'interesttimeout': interest_time.value,
         'escdowntimes': escalation_burn.value}
    )


@permission_required('Map.map_admin')
def sites_settings(request):
    """
    Returns the site spawns section.
    """
    return TemplateResponse(request, 'spawns_settings.html',
                            {'spawns': SiteSpawn.objects.all()})


@permission_required('Map.map_admin')
def add_spawns(request):
    """
    Adds a site spawn.
    """
    return HttpResponse()


# noinspection PyUnusedLocal
@permission_required('Map.map_admin')
def delete_spawns(request, spawn_id):
    """
    Deletes a site spawn.
    """
    return HttpResponse()


# noinspection PyUnusedLocal
@permission_required('Map.map_admin')
def edit_spawns(request, spawn_id):
    """
    Alters a site spawn.
    """
    return HttpResponse()


def destination_settings(request, user=None):
    """
    Returns the destinations section.
    """
    if not user:
        dest_list = Destination.objects.filter(user=None)
    else:
        dest_list = Destination.objects.filter(Q(user=None) |
                                               Q(user=request.user))
    return TemplateResponse(request, 'dest_settings.html',
                            {'destinations': dest_list,
                             'user_context': user})


def add_destination(request, dest_user=None):
    """
    Add a destination.
    """
    if not dest_user and not request.user.has_perm('Map.map_admin'):
        raise PermissionDenied

    system = get_object_or_404(KSystem, name=request.POST['systemName'])
    Destination(system=system, user=dest_user).save()
    return HttpResponse()

def add_personal_destination(request):
    """
    Add a personal destination.
    """
    return add_destination(request, dest_user=request.user)


def delete_destination(request, dest_id):
    """
    Deletes a destination.
    """
    destination = get_object_or_404(Destination, pk=dest_id)
    if not request.user.has_perm('Map.map_admin') and not destination.user:
        raise PermissionDenied
    if destination.user and not request.user == destination.user:
        raise PermissionDenied
    destination.delete()
    return HttpResponse()


@permission_required('Map.map_admin')
def sigtype_settings(request):
    """
    Returns the signature types section.
    """
    return TemplateResponse(request, 'sigtype_settings.html',
                            {'sigtypes': SignatureType.objects.all()})


# noinspection PyUnusedLocal
@permission_required('Map.map_admin')
def edit_sigtype(request, sigtype_id):
    """
    Alters a signature type.
    """
    return HttpResponse()


@permission_required('Map.map_admin')
def add_sigtype(request):
    """
    Adds a signature type.
    """
    return HttpResponse()


# noinspection PyUnusedLocal
@permission_required('Map.map_admin')
def delete_sigtype(request, sigtype_id):
    """
    Deletes a signature type.
    """
    return HttpResponse()


@permission_required('Map.map_admin')
def map_settings(request, map_id):
    """
    Returns and processes the settings section for a map.
    """
    saved = False
    subject = get_object_or_404(Map, pk=map_id)
    if request.method == 'POST':
        name = request.POST.get('name', None)
        explicit_perms = request.POST.get('explicitperms', False)
        truncate_allowed = request.POST.get('truncate_allowed', False)
        if not name:
            return HttpResponse('The map name cannot be blank', status=400)
        subject.truncate_allowed = truncate_allowed
        subject.name = name
        subject.explicitperms = explicit_perms
        for group in Group.objects.all():
            MapPermission.objects.filter(group=group, map=subject).delete()
            setting = request.POST.get('map-%s-group-%s-permission' % (
                subject.pk, group.pk), 0)
            if setting != 0:
                MapPermission(group=group, map=subject, access=setting).save()
        subject.save()
        saved = True
    groups = []
    for group in Group.objects.all():
        if MapPermission.objects.filter(map=subject, group=group).exists():
            perm = MapPermission.objects.get(map=subject, group=group).access
        else:
            perm = 0
        groups.append((group,perm))

    return TemplateResponse(request, 'map_settings_single.html',
            {'map': subject, 'groups': groups, 'saved': saved})



@permission_required('Map.map_admin')
def delete_map(request, map_id):
    """
    Deletes a map.
    """
    subject = get_object_or_404(Map, pk=map_id)
    subject.delete()
    return HttpResponse()


# noinspection PyUnusedLocal
@permission_required('Map.map_admin')
def edit_map(request, map_id):
    """
    Alters a map.
    """
    return HttpResponse('[]')


@permission_required('Map.map_admin')
def global_permissions(request):
    """
    Returns and processes the global permissions section.
    """
    if not request.is_ajax():
        raise PermissionDenied
    group_list = []
    admin_perm = Permission.objects.get(codename="map_admin")
    unrestricted_perm = Permission.objects.get(codename="map_unrestricted")
    add_map_perm = Permission.objects.get(codename="add_map")

    if request.method == "POST":
        for group in Group.objects.all():
            if request.POST.get('%s_unrestricted' % group.pk, None):
                if unrestricted_perm not in group.permissions.all():
                    group.permissions.add(unrestricted_perm)
            else:
                if unrestricted_perm in group.permissions.all():
                    group.permissions.remove(unrestricted_perm)

            if request.POST.get('%s_add' % group.pk, None):
                if add_map_perm not in group.permissions.all():
                    group.permissions.add(add_map_perm)
            else:
                if add_map_perm in group.permissions.all():
                    group.permissions.remove(add_map_perm)

            if request.POST.get('%s_admin' % group.pk, None):
                if admin_perm not in group.permissions.all():
                    group.permissions.add(admin_perm)
            else:
                if admin_perm in group.permissions.all():
                    group.permissions.remove(admin_perm)

        return HttpResponse()
    for group in Group.objects.all():
        entry = {
            'group': group, 'admin': admin_perm in group.permissions.all(),
            'unrestricted': unrestricted_perm in group.permissions.all(),
            'add_map': add_map_perm in group.permissions.all()
        }
        group_list.append(entry)

    return TemplateResponse(request, 'global_perms.html',
                            {'groups': group_list})


@require_map_permission(permission=2)
def purge_signatures(request, map_id, ms_id):
    if not request.is_ajax():
        raise PermissionDenied
    mapsys = get_object_or_404(MapSystem, pk=ms_id)
    if request.method == "POST":
        mapsys.system.signatures.all().delete()
        return HttpResponse()
    else:
        return HttpResponse(status=400)
