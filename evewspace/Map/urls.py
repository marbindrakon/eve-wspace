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
from django.conf.urls.defaults import patterns, include, url

sigpatterns = patterns('Map.views',
        url(r'^activate/$', 'activate_signature'),
        url(r'^escalate/$', 'escalate_site'),
        url(r'^clear/$', 'mark_signature_cleared'),
        url(r'^remove/$', 'delete_signature'),
        url(r'^edit/$', 'edit_signature'),
        url(r'^spawns/$', 'site_spawns')
        )

syspatterns = patterns('Map.views',
        url(r'^$', 'system_details'),
        url(r'^menu/$', 'system_menu'),
        url(r'^interest/$','set_interest'),
        url(r'^location/$', 'manual_location'),
        url(r'^scanned/$', 'mark_scanned'),
        url(r'^remove/$', 'remove_system'),
        url(r'^edit/$', 'edit_system'),
        url(r'^destinations/$', 'destination_list'),
        url(r'^addchild/$', 'manual_add_system'),
        url(r'^signatures/$', 'get_signature_list'),
        url(r'^signatures/new/$', 'edit_signature'),
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
        url(r'^edit/$', 'edit_map'),
        url(r'^delete/$', 'delete_map'),
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
        url(r'^(?P<map_id>\d+)/', include(mappatterns)),
        url(r'^settings/', include(settingspatterns)),
        )
