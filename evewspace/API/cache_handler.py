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
from django.core.cache import cache
from datetime import datetime

import cPickle as pickle
import time
import zlib
import pytz

def store(host, path, params, doc, obj):
    """Store an API document in our cache."""
    #First remove any outdated versions of the document.
    cacheKey = "%s%s%s" %(host, path, params)
    cacheTimer = obj.cachedUntil - int(time.time())
    # If cacheTimer is negative or 0 (due to server clock inaccuracy)
    # We will set a default cache timer of 60 seconds
    if cacheTimer <= 0:
        cacheTimer = 60
    cache.set(hash(cacheKey), zlib.compress(pickle.dumps(obj)), cacheTimer)


def retrieve(host, path, params):
    """Get an API document from our cache."""
    cacheKey = "%s%s%s" % (host, path, params)
    if cache.get(hash(cacheKey)):
        return pickle.loads(zlib.decompress(cache.get(hash(cacheKey))))
    else:
        return None

