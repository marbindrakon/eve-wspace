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
    current_location = (request.eve_systemid, request.eve_charname,
            request.eve_shipname, request.eve_shiptypename)
    char_cache_key = 'char_%s_location' % request.eve_charid
    old_location = cache.get(char_cache_key)
    result = None
    print old_location

    if old_location != current_location:
        if old_location:
            old_system = get_object_or_404(System, pk=old_location[0])
            old_system.remove_active_pilot(request.eve_charid)
        current_system = get_object_or_404(System, pk=current_location[0])
        current_system.add_active_pilot(request.user.username,
                request.eve_charid, request.eve_charname, request.eve_shipname,
                request.eve_shiptypename)
        request.user.get_profile().update_location(current_system.pk,
                request.eve_charid, request.eve_charname, request.eve_shipname,
                request.eve_shiptypename)
        cache.set(char_cache_key, current_location, 60 * 5)
    #Conditions for the system to be automagically added to the map.
        if (old_location and
            old_system in current_map
            and current_system not in current_map
            and not _is_moving_from_kspace_to_kspace(old_system, current_system)
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

    return result


def _is_moving_from_kspace_to_kspace(old_system, current_system):
    """
    returns whether we are moving through kspace
    :param old_system:
    :param current_system:
    :return:
    """
    return old_system.is_kspace() and current_system.is_kspace()


def get_system_context(ms_id):
    map_system = get_object_or_404(MapSystem, pk=ms_id)

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
            'stfleets': st_fleets, 'locations': locations}


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

    return render(request, 'system_details.html', get_system_context(ms_id))


# noinspection PyUnusedLocal
@login_required
@require_map_permission(permission=1)
def system_menu(request, map_id, ms_id):
    """
    Returns the html for system menu
    """
    if not request.is_ajax():
        raise PermissionDenied

    return render(request, 'system_menu.html', get_system_context(ms_id))


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
    request.user.get_profile().update_location(map_sys.system.pk, request.user.pk,
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
    if (row[COL_SIG_SCAN_GROUP] == "Cosmic Signature"
        or row[COL_SIG_SCAN_GROUP] == "Cosmic Anomaly"
       ):
        try:
            sig_type = SignatureType.objects.get(
                    longname=row[COL_SIG_GROUP])
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
                'utf-8').splitlines(), delimiter="\t")
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
@require_map_permission(permission=2)
def edit_signature(request, map_id, ms_id, sig_id=None):
    """
    GET gets a pre-filled edit signature form.
    POST updates the signature with the new information and returns a
    blank add form.
    """
    if not request.is_ajax():
        raise PermissionDenied
    map_system = get_object_or_404(MapSystem, pk=ms_id)
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
        if (
                (map_system.system.info != request.POST.get('info', '')) or
                (map_system.system.occupied !=
                 request.POST.get('occupied', ''))
        ):
            map_system.system.info = request.POST.get('info', '')
            map_system.system.occupied = request.POST.get('occupied', '')
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
    subject = get_object_or_404(Map, pk=map_id)
    return TemplateResponse(request, 'map_settings_single.html',
                            {'map': subject})


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
