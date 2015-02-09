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
from django.conf.urls import patterns, include, url

sigpatterns = patterns('Map.views',
        url(r'^activate/$', 'activate_signature'),
        url(r'^escalate/$', 'escalate_site'),
        url(r'^clear/$', 'mark_signature_cleared'),
        url(r'^remove/$', 'delete_signature'),
        url(r'^edit/$', 'edit_signature'),
        url(r'^spawns/$', 'site_spawns'),
        url(r'^own/$', 'toggle_sig_owner'),
        )

syspatterns = patterns('Map.views',
        url(r'^$', 'system_details'),
        url(r'^menu/$', 'system_menu'),
        url(r'^interest/$','set_interest'),
        url(r'^location/$', 'manual_location'),
        url(r'^scanned/$', 'mark_scanned'),
        url(r'^importance/$', 'set_importance'),
        url(r'^promote/$', 'promote_system'),
        url(r'^remove/$', 'remove_system'),
        url(r'^edit/$', 'edit_system'),
        url(r'^destinations/$', 'destination_list'),
        url(r'^addchild/$', 'manual_add_system'),
        url(r'^signatures/$', 'get_signature_list'),
        url(r'^signatures/new/$', 'edit_signature'),
        url(r'^signatures/purge/$', 'purge_signatures'),
        url(r'^signatures/bulkadd/$', 'bulk_sig_import'),
        url(r'^signatures/(?P<sig_id>\d+)/', include(sigpatterns)),
        url(r'^collapse/$', 'collapse_system'),
        url(r'^resurrect/$', 'resurrect_system'),
        )

wormholepatterns = patterns('Map.views',
        url(r'^edit/$$', 'edit_wormhole'),
        )

mappatterns = patterns('Map.views',
        url(r'^$', 'get_map'),
        url(r'^update/$', 'map_checkin'),
        url(r'^refresh/$', 'map_refresh'),
        url(r'^delete/$', 'delete_map'),
        url(r'^export/$', 'export_map'),
        url(r'^system/new/$', 'add_system'),
        url(r'^system/tooltips/$', 'system_tooltips'),
        url(r'^system/(?P<ms_id>\d+)/', include(syspatterns)),
        url(r'^wormhole/tooltips/$', 'wormhole_tooltips'),
        url(r'^wormhole/(?P<wh_id>\d+)/', include(wormholepatterns)),
        url(r'^settings/$', 'map_settings'),
        )

spawnspatterns = patterns('Map.views',
        url(r'^edit/$', 'edit_spawns'),
        url(r'^delete/$', 'delete_spawns'),
        )

sigtypepatterns = patterns('Map.views',
        url(r'^edit/$', 'edit_sigtype'),
        url(r'^delete/$', 'delete_sigtype'),
        )

settingspatterns = patterns('Map.views',
        url(r'^general/$', 'general_settings'),
        url(r'^sitespawns/$', 'sites_settings'),
        url(r'^permissions/$', 'global_permissions'),
        url(r'^sitespawns/add/$', 'add_spawns'),
        url(r'^sitespawns/(?P<spawn_id>\d+)/', include(spawnspatterns)),
        url(r'^destinations/$', 'destination_settings'),
        url(r'^user-destinations/$', 'destination_settings', {'user': True}),
        url(r'^user-destinations/new/$', 'add_personal_destination'),
        url(r'^destinations/new/$', 'add_destination'),
        url(r'^destinations/(?P<dest_id>\d+)/delete/$', 'delete_destination'),
        url(r'^sigtypes/$', 'sigtype_settings'),
        url(r'^sigtypes/(?P<sigtype_id>\d+)/', include(sigtypepatterns)),
        )

urlpatterns = patterns('Map.views',
        url(r'^new/$', 'create_map'),
        url(r'^import/$', 'import_map'),
        url(r'^(?P<map_id>\d+)/', include(mappatterns)),
        url(r'^settings/', include(settingspatterns)),
        )
