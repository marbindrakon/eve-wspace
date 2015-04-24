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
from django import template
from django.shortcuts import get_object_or_404
from POS.models import POS
from Map.models import System, MapSystem

register=template.Library()

@register.inclusion_tag('poslist.html', takes_context=True)
def poslist(context, mapsystem):
	mapsystem = get_object_or_404(MapSystem, pk=mapsystem)
	system = get_object_or_404(System, pk=mapsystem.system.pk)
	poses = POS.objects.filter(system=system)
	return {'poses': poses, 'mapsystem': mapsystem, 'request': context['request']}


@register.inclusion_tag('posdetails_small.html', takes_context=True)
def posdetails(context, mapsystem, pos):
	return {'pos' : pos, 'mapsystem': mapsystem, 'perms': context['perms']}
