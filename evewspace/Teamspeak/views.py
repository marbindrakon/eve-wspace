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
from django.contrib.auth.decorators import login_required, permission_required
import PyTS3
from Teamspeak.models import TeamspeakServer,GroupMap,TeamspeakUserMap
from core.utils import get_config
from django.http import HttpResponse
from django.contrib.auth.models import Group, User

# TODO: Change login_required to the appropriate permission_required when the permission UI is done

@login_required
def show_online(request):
    serversettings = TeamspeakServer.objects.get(id=1)
    try:
        server = PyTS3.ServerQuery(serversettings.host, serversettings.queryport)
        server.connect()
        server.command('login', {'client_login_name': serversettings.queryuser, 'client_login_password': serversettings.querypass})
        server.command('use', {'port': str(serversettings.voiceport)})
        server.command('clientupdate', {'client_nickname': 'evewspace'})
        clientlist = server.command('clientlist -away')
        return TemplateResponse(request, 'ts_userlist.html', {'clientlist': clientlist})
    except Exception as e:
        return HttpResponse('%s' % e, content_type="text/plain")


@login_required
def general_settings(request):
    """
    Returns and processes the general settings section.
    """
    serversettings = TeamspeakServer.objects.get(id=1)
    saved = False
    tsservers = TeamspeakServer.objects.all()
    djangogroups = Group.objects.all()
    if request.method == "POST":
        serversettings.host = request.POST['ts3hostname']
        serversettings.voiceport = int(request.POST['Port'])
        serversettings.queryuser = request.POST['QueryLoginUsername']
        if request.POST['QueryLoginPasswort'] != '':
            serversettings.querypass = request.POST['QueryLoginPasswort']
        serversettings.queryport = int(request.POST['QueryPort'])
        serversettings.save()
        saved = True

    return TemplateResponse(
        request, 'teamspeak_settings.html',
        {'ts3hostname': serversettings.host,
         'Port': serversettings.voiceport,
         'QueryLoginUsername': serversettings.queryuser,
         'QueryLoginPasswort': serversettings.querypass,
         'QueryPort': serversettings.queryport,
         'saved': saved,
         'tsservers': tsservers,
         'djangogroups': djangogroups}
    )

@login_required
def show_groupmapping(request):
    groups = GroupMap.objects.all()
    return TemplateResponse(request, 'groupmapping.html', {'groups': groups})

@login_required
def add_to_group(request):
    serversettings = TeamspeakServer.objects.get(id=1)
    aimedclient = TeamspeakUserMap.objects.get(user=request.user.id,tsserver=serversettings)
    for g in request.user.groups.all():
        try:
            aimedgroup = GroupMap.objects.get(usergroup=g.id)
        except Exception as e:
            return HttpResponse('%s' % str(e), content_type="text/plain")
        try:
            server = PyTS3.ServerQuery(serversettings.host, serversettings.queryport)
            server.connect()
            server.command('login', {'client_login_name': serversettings.queryuser, 'client_login_password': serversettings.querypass})
            server.command('use', {'port': str(serversettings.voiceport)})
            server.command('clientupdate', {'client_nickname': 'evewspace'})
            servergrouplist = server.command('servergrouplist')
            for group in servergrouplist:
                if group['name'] == aimedgroup.tsgroup and group['type'] != 0:
                    server.command('servergroupaddclient', {'sgid': group['sgid'], 'cldbid': aimedclient.tsdbid})

        except Exception as e:
            return HttpResponse('%s' % e, content_type="text/plain")
    return HttpResponse('Success', content_type="text/plain")

@login_required
def addgroupmap(request):
    tsserver = TeamspeakServer.objects.get(id=request.POST['ts3hostname'])
    usergroup = Group.objects.get(id=request.POST['djangogroup'])
    #prevent double entry
    if GroupMap.objects.filter(tsserver=tsserver,usergroup=usergroup,tsgroup=request.POST['tsgroup']).exists():
        return HttpResponse('Allready exist', content_type="text/plain")
    groupmap = GroupMap.create(tsserver, usergroup, request.POST['tsgroup'])
    groupmap.save()
    return HttpResponse('Success', content_type="text/plain")

@login_required
def delgroupmap(request):
    groupmap = GroupMap.objects.get(id=request.POST['groupmapid'])
    groupmap.delete()
    return HttpResponse('Success', content_type="text/plain")

@login_required
def remove_from_group(request):
    #not tested
    serversettings = TeamspeakServer.objects.get(id=1)
    aimedclient = TeamspeakUserMap.objects.get(user=request.user.id,tsserver=serversettings)
    for g in request.user.groups.all():
        try:
            aimedgroup = GroupMap.objects.get(usergroup=g.id)
        except Exception as e:
            return HttpResponse('%s' % str(e), content_type="text/plain")
        try:
            server = PyTS3.ServerQuery(serversettings.host, serversettings.queryport)
            server.connect()
            server.command('login', {'client_login_name': serversettings.queryuser, 'client_login_password': serversettings.querypass})
            server.command('use', {'port': str(serversettings.voiceport)})
            server.command('clientupdate', {'client_nickname': 'evewspace'})
            servergrouplist = server.command('servergrouplist')
            for group in servergrouplist:
                if group['name'] == aimedgroup.tsgroup and group['type'] != 0:
                    server.command('servergroupdelclient', {'sgid': group['sgid'], 'cldbid': aimedclient.tsdbid})

        except Exception as e:
            return HttpResponse('%s' % e, content_type="text/plain")
    return HttpResponse('Success', content_type="text/plain")

@login_required
def generate_token(request):
    serversettings = TeamspeakServer.objects.get(id=1)
    user = User.objects.get(id=request.user.id)
    #prevent generation of more than one token per server
    if TeamspeakUserMap.objects.filter(tsserver=serversettings, user=user).exists():
        usermap = TeamspeakUserMap.objects.get(tsserver=serversettings, user=user)
        return HttpResponse('%s' % usermap.token, content_type="text/plain")

    usermap = TeamspeakUserMap.create(serversettings, user)
    for g in request.user.groups.all():
        try:
            aimedgroup = GroupMap.objects.get(usergroup=g.id)
        except Exception as e:
            return HttpResponse('%s' % str(e), content_type="text/plain")
        try:
            server = PyTS3.ServerQuery(serversettings.host, serversettings.queryport)
            server.connect()
            server.command('login', {'client_login_name': serversettings.queryuser, 'client_login_password': serversettings.querypass})
            server.command('use', {'port': str(serversettings.voiceport)})
            server.command('clientupdate', {'client_nickname': 'evewspace'})
            servergrouplist = server.command('servergrouplist')
            for group in servergrouplist:
                if group['name'] == aimedgroup.tsgroup and group['type'] != 0:
                    customsetstring = "ident=ews_user\svalue=" + str(user.id)
                    token = server.command('tokenadd', {'tokentype': 0, 'tokenid1': group['sgid'], 'tokenid2': 0, 'tokendescription': 'ewstoken', 'tokencustomset': customsetstring})
                    usermap.token = token['token']
                    usermap.save()
                    return HttpResponse('Success %s' % usermap.token, content_type="text/plain")
        except Exception as e:
            return HttpResponse('%s' % e, content_type="text/plain")
    return HttpResponse('no groups assigned to the user', content_type="text/plain")

@login_required
def link_ews_users(request):
    serversettings = TeamspeakServer.objects.get(id=1)
    unlinked_users = TeamspeakUserMap.objects.filter(token__isnull=False)
    for unlinked_user in unlinked_users:
        server = PyTS3.ServerQuery(serversettings.host, serversettings.queryport)
        server.connect()
        server.command('login', {'client_login_name': serversettings.queryuser, 'client_login_password': serversettings.querypass})
        server.command('use', {'port': str(serversettings.voiceport)})
        server.command('clientupdate', {'client_nickname': 'evewspace'})
        ret=server.command('customsearch', {'ident': 'ews_user', 'pattern': str(unlinked_user.user.id)})
        unlinked_user.tsdbid = ret['cldbid']
        unlinked_user.token = None
        unlinked_user.save()
        return HttpResponse('%s' % ret['cldbid'], content_type="text/plain")
    return HttpResponse('Success', content_type="text/plain")

@login_required
def user_profile(request):
    tsregs = TeamspeakUserMap.objects.filter(user=request.user.id)
    return TemplateResponse(
        request, 'ts_registration_list.html',
        {'tsregs': tsregs}
    )