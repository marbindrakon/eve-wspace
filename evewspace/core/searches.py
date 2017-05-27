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
from search import registry
from .models import Type, Corporation, Alliance

registry.register(Corporation, 'corp', 'name')
registry.register(Alliance, 'alliance', 'name')
registry.register(Type, 'item', 'name',
        Type.objects.filter(published=1).all())
registry.register(Type, 'tower', 'name',
        Type.objects.filter(published=1, marketgroup__pk=478).all())
