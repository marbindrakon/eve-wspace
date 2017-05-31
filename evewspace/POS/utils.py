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
from .models import CorpPOS
import eveapi
from API import cache_handler as handler


def add_status_info(poses):
    """Accepts a list of corp poses and returns a list of POSes with
    status information attached.

    A posstatus object has the following attributes:
    itemid: the POS item id
    pos: POS object processed
    status: Status retrieved

    """
    class statusentry:
        def __init__(self, pos, status):
            self.itemid = pos.apiitemid
            self.pos = pos
            self.status = status
    api = eveapi.EVEAPIConnection(cacheHandler=handler)
    #Now that we have a corp authenticated API, let's play with some POSes
    statuslist = []
    for pos in poses:
        auth = api.auth(keyID=pos.apikey.keyid, vCode=pos.apikey.vcode)
        result = auth.corp.StarbaseDetail(itemID=pos.apiitemid)
        status = statusentry(pos, result)
        statuslist.append(status)

    return statuslist
