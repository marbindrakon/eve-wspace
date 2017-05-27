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
import re
import pytz

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404

from POS.models import *
from Map.models import System, MapSystem
from core.models import Type
from API import cache_handler as handler
from core import tasks as core_tasks


@login_required
def test_fit(request, posID):
    """
    Temporary test method for filling a POS fit from DScan.
    """
    pos = get_object_or_404(POS, pk=posID)
    if request.method == "POST":
        data = request.POST['fit'].encode('utf-8')
        pos.fit_from_dscan(data)
        return HttpResponse()
    else:
        return TemplateResponse(request, 'testfitter.html', {'pos': pos})


@permission_required('POS.delete_pos', raise_exception=True)
def remove_pos(request, msID, posID):
    """
    Removes the POS. Raises PermissionDenied if it is a CorpPOS.
    """
    if not request.is_ajax():
        raise PermissionDenied
    mapsystem = get_object_or_404(MapSystem, pk=msID)
    pos = get_object_or_404(POS, pk=posID)
    if CorpPOS.objects.filter(pk=posID).count():
        raise PermissionDenied

    pos.delete()
    pos.log(request.user, "Deleted", mapsystem)

    return HttpResponse()


@login_required
def get_pos_list(request, msID):    
    if not request.is_ajax():
        raise PermissionDenied
    mapsystem = get_object_or_404(MapSystem, pk=msID)
    system = get_object_or_404(System, pk=mapsystem.system.pk)
    poses = POS.objects.filter(system=system).all()    

    return TemplateResponse(request, 'poslist.html', {'mapsystem': mapsystem,
        'poses': poses})


@permission_required('POS.change_pos', raise_exception=True)
def edit_pos(request, msID, posID):
    """
    GET gets the edit POS dialog, POST processes it.
    """
    if not request.is_ajax():
        raise PermissionDenied
    mapsystem = get_object_or_404(MapSystem, pk=msID)
    system = get_object_or_404(System, pk=mapsystem.system.pk)
    pos = get_object_or_404(POS, pk=posID)
    if request.method == 'POST':
        tower = get_object_or_404(Type, name=request.POST['tower'])
        try:
            corp = Corporation.objects.get(name=request.POST['corp'])
        except Corporation.DoesNotExist:
            api = eveapi.EVEAPIConnection(cacheHandler=handler)
            corp_id = api.eve.CharacterID(
                names=request.POST['corp']).characters[0].characterID
            if corp_id == 0:
                return HttpResponse('Corp does not exist!', status=404)
            corp = core_tasks.update_corporation(corp_id)
        pos.corporation = corp
        pos.towertype = tower
        pos.posname = request.POST['name']
        pos.planet = int(request.POST['planet'])
        pos.moon = int(request.POST['moon'])
        pos.status = int(request.POST['status'])
        pos.fitting = request.POST['fitting']

        # Have the async worker update the corp just so that it is up to date
        core_tasks.update_corporation.delay(corp.id)
        if pos.status == 3:
            if request.POST['rfdays'] == '':
                rf_days = 0
            else:
                rf_days = int(request.POST['rfdays'])
            if request.POST['rfhours'] == '':
                rf_hours = 0
            else:
                rf_hours = int(request.POST['rfhours'])
            if request.POST['rfminutes'] == '':
                rf_minutes = 0
            else:
                rf_minutes = int(request.POST['rfminutes'])
            delta = timedelta(days=rf_days,
                              hours=rf_hours,
                              minutes=rf_minutes)
            pos.rftime = datetime.now(pytz.utc) + delta
        pos.save()
        if request.POST.get('dscan', None) == "1":
            pos.fit_from_dscan(request.POST['fitting'].encode('utf-8'))
        return HttpResponse()
    else:
        fitting = pos.fitting
        if fitting is not None:
            fitting = fitting.replace("<br />", "\n")
        return TemplateResponse(request, 'edit_pos.html', {'system': system,
                                                           'mapsystem': mapsystem,
                                                           'pos': pos,
                                                           'fitting': fitting})


@login_required
def add_pos(request, msID):
    """
    GET gets the add POS dialog, POST processes it.
    """

    if not request.is_ajax():
        raise PermissionDenied
    mapsystem = get_object_or_404(MapSystem, pk=msID)
    system = get_object_or_404(System, pk=mapsystem.system.pk)
    if request.method == 'POST':
        corp_name = request.POST.get('corp', None)
        if not corp_name:
            return HttpResponse('Corp cannot be blank!', status=400)

        try:
            corp = Corporation.objects.get(name=corp_name)
        except Corporation.DoesNotExist:
            # Corp isn't in our DB, get its ID and add it
            try:
                api = eveapi.EVEAPIConnection(cacheHandler=handler)
                corp_id = (api.eve.CharacterID(names=corp_name)
                           .characters[0].characterID)
                if corp_id == 0:
                    return HttpResponse('Corp does not exist!', status=404)
                corp = core_tasks.update_corporation(corp_id, True)
            except:
                # Error while talking to the EVE API
                return HttpResponse('Could not verify Corp name. Please try again later.', status=404)                
        else:
            # Have the async worker update the corp so that it is up to date
            core_tasks.update_corporation.delay(corp.id)

        if request.POST['auto'] == '1':
            fittings = []
            moon_distance = 150000000
            for i in request.POST['fitting'].splitlines():
                cols = i.split('\t')
                # ignore offgrid stuff
                if cols[2] != '-':
                    fittings.append(cols)
                    if cols[1] == 'Moon' and cols[2].endswith('km'):
                        # found a moon close by
                        distance = int(cols[2][:-3].replace(',', '')
                                       .replace('.', '').replace('\xa0', ''))
                        if distance < moon_distance:
                            # closest moon so far
                            moon_distance = distance
                            moon_name = cols[0]
            if moon_distance == 150000000:
                # No moon found
                return HttpResponse('No moon found in d-scan!', status=404)

            # parse POS location
            regex = '^%s ([IVX]+) - Moon ([0-9]+)$' % (system.name,)
            re_result = re.match(regex, moon_name)
            if not re_result:
                return HttpResponse(
                    'Invalid D-Scan! Do you have the right system?',
                    status=400)
            else:
                result = re_result.groups()
            NUMERALS = {'X': 10, 'V': 5, 'I': 1}
            planet = 0
            for i in range(len(result[0])):
                value = NUMERALS[result[0][i]]
                try:
                    next_value = NUMERALS[result[0][i+1]]
                except IndexError:
                    next_value = 0
                if value < next_value:
                    planet -= value
                else:
                    planet += value
            moon = int(result[1])

            pos = POS(system=system, planet=planet,
                      moon=moon, status=int(request.POST['status']),
                      corporation=corp)
            try:
                pos.fit_from_iterable(fittings)
            except AttributeError as e:
                return HttpResponse(e, status=404)

        else:
            tower = get_object_or_404(Type, name=request.POST['tower'], marketgroup__isnull=False)
            pos = POS(system=system, planet=int(request.POST['planet']),
                      moon=int(request.POST['moon']),
                      towertype=tower,
                      posname=request.POST['name'],
                      fitting=request.POST['fitting'],
                      status=int(request.POST['status']),
                      corporation=corp)
            if request.POST.get('dscan', None) == "1":
                pos.fit_from_dscan(request.POST['fitting'].encode('utf-8'))

        if pos.status == 3:
            if request.POST['rfdays'] == '':
                rf_days = 0
            else:
                rf_days = int(request.POST['rfdays'])
            if request.POST['rfhours'] == '':
                rf_hours = 0
            else:
                rf_hours = int(request.POST['rfhours'])
            if request.POST['rfminutes'] == '':
                rf_minutes = 0
            else:
                rf_minutes = int(request.POST['rfminutes'])
            delta = timedelta(days=rf_days,
                              hours=rf_hours,
                              minutes=rf_minutes)
            pos.rftime = datetime.now(pytz.utc) + delta
        pos.log(request.user, "Added", mapsystem)
        pos.save()

        return HttpResponse()
    else:
        return TemplateResponse(request, 'add_pos.html', {'system': system, 'mapsystem': mapsystem})
