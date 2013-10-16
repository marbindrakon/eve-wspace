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
from django.conf.urls import patterns, include, url

# Run the autodiscovers for various registries to fill them
from search import registry as search_registry
from Alerts import method_registry
from core import admin_page_registry, nav_registry

method_registry.autodiscover()
search_registry.autodiscover()
admin_page_registry.autodiscover()
nav_registry.autodiscover()

# Actual URL definitions
urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'eve-space.views.home', name='home'),
        # url(r'^WormholeSpace2/', include('eve-space.foo.urls')),

        # Uncomment the admin/doc line below to enable admin documentation:
        # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        url(r'^$', 'core.views.home_view', name='index'),
        url(r'^settings/$', 'core.views.config_view', name='settings'),
        url(r'^account/', include('account.urls')),
        url(r'^map/', include('Map.urls')),
        url(r'^search/', include('search.urls')),
        url(r'^pos/', include('POS.urls')),
        url(r'^sitetracker/', include('SiteTracker.urls')),
        url(r'^alerts/', include('Alerts.urls')),
        url(r'^api/', include('API.urls')),
        url(r'^teamspeak/', include('Teamspeak.urls')),
)
