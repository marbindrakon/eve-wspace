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
from celery import task
import PyTS3
from Teamspeak.models import TeamspeakServer,GroupMap,TeamspeakUserMap


@task()
def link_ews_users():
    """
    Link the Teamspeakusers back to EWS
    """
    #serversettings = TeamspeakServer.objects.get(id=1)
    unlinked_users = TeamspeakUserMap.objects.filter(token__isnull=False)
    for unlinked_user in unlinked_users:
        serversettings = unlinked_user.tsserver
        server = PyTS3.ServerQuery(serversettings.host, serversettings.queryport)
        server.connect()
        server.command('login', {'client_login_name': serversettings.queryuser, 'client_login_password': serversettings.querypass})
        server.command('use', {'port': str(serversettings.voiceport)})
        server.command('clientupdate', {'client_nickname': 'evewspace'})
        ret=server.command('customsearch', {'ident': 'ews_user', 'pattern': str(unlinked_user.user.id)})
        unlinked_user.tsdbid = ret['cldbid']
        unlinked_user.token = None
        unlinked_user.save()

