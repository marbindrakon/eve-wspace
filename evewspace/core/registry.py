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
"""
A registry subsystem to register content under different containers
"""

import copy
import inspect
from importlib import import_module
from collections import namedtuple
from django.db import models
from django.template.loader import get_template
from django.conf import settings
from django.utils.module_loading import module_has_submodule



RegistryEntry = namedtuple('RegistryEntry', ['prio', 'idx', 'name', 'value'])


class RegistryMeta(type):
    _ALL_REGISTRIES = {}

    def __call__(cls, name, **kwargs):
        if name in cls._ALL_REGISTRIES:
            obj = cls._ALL_REGISTRIES[name]
            if 'baseclass' in kwargs:
                # if there was init call that was missing baseclass before second,
                # then add this missing information
                baseclass = kwargs['baseclass']
                if baseclass and not obj._baseclass:
                    obj._baseclass = baseclass
            return obj
        else:
            obj = super(RegistryMeta, cls).__call__(name, **kwargs)
            cls._ALL_REGISTRIES[name] = obj
            return obj

    def get_registry(cls, name):
        registry = cls._ALL_REGISTRIES.get(name, None)
        if not registry:
            raise ValueError("Registry '%s' is not known" % (name,))
        return registry

    def _autodiscover_all(cls):
        for app in settings.INSTALLED_APPS:
            if app.startswith('django.'):
                # skip django library
                continue
            for registry_name, registry in cls._ALL_REGISTRIES.items():
                if settings.DEBUG: print(" .... checking %s.%s" % (app, registry_name))
                mod = import_module(app)
                before_import_registry = copy.copy(registry._data)
                try:
                    import_module('%s.%s' % (app, registry_name))
                    if settings.DEBUG: print(" .... -------- %s.%s discovered" % (app, registry_name))
                except:
                    registry._data = before_import_registry
                    if module_has_submodule(mod, registry_name):
                        raise

    def _deebug_print_registry(cls, force=False):
        if force or settings.DEBUG:
            for name, reg in Registry._ALL_REGISTRIES.items():
                print(" == registry: %s" % (name,))
                for row in reg._data:
                    print("  \\- %s" % (row,))


class Registry(object, metaclass=RegistryMeta):
    """
    Dict with methods for handling content registration.
    """

    def __init__(self, name, baseclass=None):
        if name in self.__class__._ALL_REGISTRIES:
            raise ValueError("Registry by name %s initialized twice" % (name,))
        self._name = name
        self._baseclass = baseclass
        self._lookup = {}
        self._data = []

    @property
    def name(self):
        return self._name

    def __contains__(self, key):
        entry = self._lookup.get(key)
        return bool(entry and entry.value)

    def __getitem__(self, key):
        return self._lookup[key].value

    def items(self):
        return ((entry.name, entry.value) for entry in self._data)

    def keys(self):
        return (entry.name for entry in self._data)

    def values(self):
        return (entry.value for entry in self._data)

    def pop(self, name, default=None):
        entry = self._lookup.pop(name, None)
        return entry.value if entry else default

    def unregister(self, name):
        """
        Unregisters name from registry
        """
        return self.pop(name)

    def register(self, name, value, priority=0):
        """
        Register item object
        """
        test = issubclass if inspect.isclass(value) else isinstance
        if self._baseclass and not test(value, self._baseclass):
            raise ValueError("Module %r is not subclass/instance of %r" % (module, self._baseclass))
        if not name:
            raise ValueError("name is not something")
        entry = RegistryEntry(priority, len(self._data), name, value)
        self._lookup[name] = entry
        self._data.append(entry)
        self._data.sort()


class TemplateRegistryItem(object):
    def __init__(self, name, template, permission):
        self.name = name
        self.filename = template
        self.template = get_template(template)
        self.permission = permission

    def permission_check_ok(self, user):
        return not self.permission or user.has_perm(self.permission)

    def __repr__(self):
        return "<%s(%s)>" % (self.__class__.__name__, self.filename)


class TemplateRegistry(Registry):
    def __init__(self, name):
        super(TemplateRegistry, self).__init__(name, baseclass=TemplateRegistryItem)

    def register(self, name, template=None, permission=None, priority=0):
        if not template:
            template = name
            name = template.split('.', 1)[0]
        item = TemplateRegistryItem(name, template, permission)
        super(TemplateRegistry, self).register(name, item, priority=priority)

    def get_visible(self, user):
        for name, template in self.items():
            if template.permission_check_ok(user):
                yield (name, template.filename)
