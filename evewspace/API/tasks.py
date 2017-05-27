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
from core.utils import get_config
from API.utils import sso_refresh_access_token, crest_access_data, esi_access_data, sso_access_list, api_current_corp
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q


import urllib.request, urllib.error, urllib.parse
import json
import base64
import sys
import pytz
import imp

imp.reload(sys)
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
    for token in SSORefreshToken.objects.exclude(refresh_token__isnull=True).exclude(refresh_token__exact='').all():
        key = str(token.user_id) + '_online'
        online = cache.get(key)
        if online == "Yes":
            url = 'characters/%s/location/' % token.char_id
            response = esi_access_data(token,url)
            
            url2 = 'characters/%s/ship/' % token.char_id
            response2 = esi_access_data(response["token"],url2)
            
            if response: 
                system_pk = response["solar_system_id"]
            else:
                url3 = 'characters/%s/location/' % token.char_id
                response3 = crest_access_data(token,url3)
                if response3:
                    system_pk = response3["solarSystem"]["id"]
                        
            
            if response2:
                ship_type_id = response2["ship_type_id"]
            
            #change "not 'structure_id' in response" when online check can be executed in ESI
            if system_pk and not 'structure_id' in response:
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
        

@task()
def update_account_status():
    if get_config("SSO_DEACTIVATE_ACCOUNTS", None).value:
        for account in User.objects.filter(is_active=True).exclude(Q(is_superuser=True) | Q(user_permissions__codename='change_ssoaccesslist') | Q(groups__permissions__codename='change_ssoaccesslist')).all():
            count = 0
            for token in account.crest_refresh_tokens.exclude(refresh_token__isnull=True).exclude(refresh_token__exact='').all():
                if count < 1:
                    corp_id = api_current_corp(token.char_id)
                    if sso_access_list(token.char_id, corp_id):
                        count = count+1
            if count == 0:
                account.is_active = False
                account.save()
            
            
