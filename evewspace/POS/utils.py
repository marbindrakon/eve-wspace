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
from models import CorpPOS
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
