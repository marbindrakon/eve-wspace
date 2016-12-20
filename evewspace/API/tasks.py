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

from celery import task
from datetime import datetime
from API.models import APIKey, MemberAPIKey, SSORefreshToken
from Map.models import System
from core.models import Type
from API.utils import sso_refresh_access_token, crest_access_data, esi_access_data
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import get_object_or_404

import urllib2
import json
import base64
import sys
import pytz

reload(sys)
sys.setdefaultencoding("utf-8")

User = get_user_model()

@task()
def update_char_data():
    #Get all users
    user_list = User.objects.all()
    for user in user_list:
        #Get all API keys of a user and validate them
        for key in user.api_keys.all():
            key.validate()

@task()
def update_char_location():
    for token in SSORefreshToken.objects.all():
        url = 'characters/%s/location/' % token.char_id
        response = esi_access_data(token,url)
        
        url2 = 'characters/%s/ship/' % token.char_id
        response2 = esi_access_data(token,url2)
        
        if response: 
            system_pk = response["solar_system_id"]
        else:
            url3 = 'characters/%s/location/' % token.char_id
            response3 = crest_access_data(token,url3)
            if response3:
                system_pk = response3["solarSystem"]["id"]
                    
        
        if response2:
            ship_type_id = response2["ship_type_id"]
            
        if system_pk:
            char_cache_key = 'char_%s_location' % token.char_id
            old_location = cache.get(char_cache_key)
            current_system = get_object_or_404(System, pk=system_pk)
            
            if response2:
                current_ship = get_object_or_404(Type, pk=ship_type_id)
                ship_type = current_ship.name
                ship_name = response2["ship_name"]
            else:
                ship_type = 'Unknown'
                ship_name = 'Unknown'
                
                
                
            if old_location != current_system:
                if old_location:
                    old_system = get_object_or_404(System, name=old_location)
                    old_system.remove_active_pilot(token.char_id)
                token.user.update_location(
                    current_system.pk,
                    token.char_id, token.char_name,
                    ship_name, ship_type)
            
            cache.set(char_cache_key, current_system, 60 * 5)
            # Use add_active_pilot to refresh the user's record in the global
            # location cache
            current_system.add_active_pilot(
                token.user, token.char_id, token.char_name,
                ship_name, ship_type 
            )
        
