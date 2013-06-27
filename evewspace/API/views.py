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

import pytz

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404

from API.models import CorpAPIKey, MemberAPIKey, APIKey, APIShipLog, APICharacter
import API.cache_handler as handler

def api_key_dialog(request):
    if not request.is_ajax():
        raise PermissionDenied
    api_keys = request.user.api_keys.all()
    return TemplateResponse(request, "manage_keys.html",
            {'api_keys': api_keys})

def edit_keys(request, key_id=None):
    if not request.is_ajax():
        raise PermissionDenied
    if key_id:
        api_key = get_object_or_404(MemberAPIKey, keyid=key_id)
    else:
        api_key = None
    if request.method == 'POST':
        key_id = int(request.POST.get('key_id', None).replace(' ',''))
        vcode = request.POST.get('vcode', None).replace(' ', '')
        if api_key:
            api_key.keyid = key_id
            api_key.vcode = vcode
            api_key.user = request.user
            api_key.validate()
        else:
            api_key = MemberAPIKey(user=request.user,
                            keyid=key_id,
                            vcode=vcode)
            api_key.validate()

    return TemplateResponse(request, "api_key_form.html", {'key': api_key})

def delete_key(request, key_id, purge=False):
    if not request.is_ajax():
        raise PermissionDenied
    if purge and not request.user.has_perm('API.purge_keys'):
        raise PermissionDenied
    api_key = get_object_or_404(MemberAPIKey, keyid=key_id)
    if not api_key in request.user.api_keys.all():
        if not request.user.has_perm('API.delete_keys'):
            raise PermissionDenied
    if purge:
        for character in api_key.characters.all():
            APIShipLog.objects.filter(charname=character.name).delete()
            character.delete()
    api_key.delete()
    return HttpResponse()
