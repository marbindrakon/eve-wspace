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
from django.db import models
from django.contrib.auth.models import Group, User

# Create your models here.

class TeamspeakServer(models.Model):
    """Stores teamspeak server configuration."""
    host = models.CharField(max_length=100)
    queryuser = models.CharField(max_length=100)
    querypass = models.CharField(max_length=100)
    queryport = models.IntegerField()
    voiceport = models.IntegerField()
    # If enforcegroups = True, any TS users who do not have a GroupMap entry will have no groups
    enforcegroups = models.BooleanField(default=False)
    # If enforceusers = True, any TS users without a Django user mapping will be removed
    enforeceusers = models.BooleanField(default=False)

    @classmethod
    def create(cls,host,queryuser,querypass,queryport,voiceport):
        ts3= cls(host=host,queryuser=queryuser,querypass=querypass,queryport=queryport,voiceport=voiceport)
        return ts3

    class Meta:
        permissions = (('ts_admin', 'Can administer Teamspeak settings'),
                       ('ts_see_online', 'Can see online TS users'),
                       )

class GroupMap(models.Model):
    """Maps Django user groups to Teamspeak groups."""
    tsserver = models.ForeignKey(TeamspeakServer, related_name="groupmaps")
    usergroup = models.ForeignKey(Group, related_name="teamspeakgroups")
    tsgroup = models.CharField(max_length=100)

    @classmethod
    def create(cls,tsserver,usergroup,tsgroup):
        group= cls(tsserver=tsserver,usergroup=usergroup,tsgroup=tsgroup)
        return group

class TeamspeakUserMap(models.Model):
    """Maps Django users to Teamspeak users."""
    tsserver = models.ForeignKey(TeamspeakServer, related_name="tsserver")
    user = models.ForeignKey(User, related_name="ewsuser")
    tsdbid = models.IntegerField(null=True)
    token = models.CharField(max_length=100, null=True)

    @classmethod
    def create(cls,tsserver,user):
        tsmap= cls(tsserver=tsserver,user=user)
        return tsmap
