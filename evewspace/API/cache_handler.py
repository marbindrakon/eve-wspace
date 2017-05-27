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
from django.core.cache import cache
from datetime import datetime

import pickle as pickle
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
    cache.set(hash(cacheKey), zlib.compress(str(doc)), cacheTimer)


def retrieve(host, path, params):
    """Get an API document from our cache."""
    cacheKey = "%s%s%s" % (host, path, params)
    if cache.get(hash(cacheKey)):
        return zlib.decompress(cache.get(hash(cacheKey)))
    else:
        return None

