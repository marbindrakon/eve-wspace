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
from API.models import APIAccessType, APIAccessGroup
from API import cache_handler as handler

from django.core.management.base import NoArgsCommand

import eveapi
import pdb

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        api = eveapi.EVEAPIConnection(cacheHandler=handler)
        result = api.api.CallList()

        for group in result.callGroups:
            api_group = APIAccessGroup.objects.get_or_create(group_id=group.groupID)[0]
            api_group.group_name = group.name
            api_group.group_description = group.description
            api_group.save()

        for call in result.calls:
            if call.type == 'Corporation':
                call_type = 2
            else:
                call_type = 1

            api_call = APIAccessType.objects.get_or_create(
                    call_type=call_type, call_name=call.name,
                    call_group=APIAccessGroup.objects.get(
                        pk=call.groupID),
                    defaults={
                        'call_mask': call.accessMask,
                        'call_description': call.description
                             })[0]
            api_call.call_mask = call.accessMask
            api_call.call_description = call.description
            api_call.call_group = APIAccessGroup.objects.get(pk=call.groupID)
            api_call.save()

        for group in APIAccessGroup.objects.all():
            if group.group_id not in result.callGroups._items:
                group.delete()

        for call in APIAccessType.objects.all():
            if call.call_type == 2:
                call_type = u'Corporation'
            elif call.call_type == 1:
                call_type = u'Character'

            if (call.call_mask, call_type) not in result.calls._items:
                print call.name
                call.delete()
