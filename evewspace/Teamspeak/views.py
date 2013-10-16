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
# Create your views here.

from django.template.response import TemplateResponse
from django.shortcuts import redirect
import PyTS3
from Teamspeak.models import TeamspeakServer
from core.utils import get_config

def show_online(request):
    serversettings = TeamspeakServer.objects.get(id=1)

    server = PyTS3.ServerQuery(serversettings.host, serversettings.queryport)
    server.connect()
    server.command('login', {'client_login_name': serversettings.queryuser, 'client_login_password': serversettings.querypass})
    server.command('use', {'port': str(serversettings.voiceport)})
    server.command('clientupdate', {'client_nickname': 'evewspace'})

    clientlist = server.command('clientlist -away')
    return TemplateResponse(request, 'ts_userlist.html',{'clientlist': clientlist})

#@permission_required('Map.map_admin')
def general_settings(request):
    """
    Returns and processes the general settings section.
    """
    serversettings = TeamspeakServer.objects.get(id=1)

    if request.method == "POST":
        serversettings.host = request.POST['ts3hostname']
        serversettings.voiceport = int(request.POST['Port'])
        serversettings.queryuser = request.POST['QueryLoginUsername']
        serversettings.querypass = request.POST['QueryLoginPasswort']
        serversettings.queryport = int(request.POST['QueryPort'])
        serversettings.save()
        return redirect('/settings/')

    return TemplateResponse(
        request, 'teamspeak_settings.html',
        {'ts3hostname': serversettings.host,
         'Port': serversettings.voiceport,
         'QueryLoginUsername': serversettings.queryuser,
         'QueryLoginPasswort': serversettings.querypass,
         'QueryPort': serversettings.queryport}
    )