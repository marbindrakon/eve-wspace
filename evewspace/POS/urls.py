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

pospatterns = patterns('POS.views',
    url(r'remove/$', 'remove_pos'),
    url(r'edit/$', 'edit_pos'),
    )

syspatterns = patterns('POS.views',
	url(r'(?P<posID>\d+)/', include(pospatterns)),
	url(r'add/$', 'add_pos'),
	url(r'$', 'get_pos_list'),
	)

urlpatterns = patterns('POS.views',
	url(r'(?P<msID>\d+)/', include(syspatterns)),
	)

