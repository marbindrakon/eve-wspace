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
                call_type = 'Corporation'
            elif call.call_type == 1:
                call_type = 'Character'

            if (call.call_mask, call_type) not in result.calls._items:
                print(call.name)
                call.delete()
