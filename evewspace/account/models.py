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
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.core.cache import cache
from Map.models import Map, System
from django.db.models.signals import post_save
import pytz
import datetime
import time
# Create your models here.

class PlayTime(models.Model):
    """PlayTime represents a choice of play times for use in several forms."""
    fromtime = models.TimeField()
    totime = models.TimeField()


class UserProfile(models.Model):
    """UserProfile defines custom fields tied to each User record in the Django auth DB."""
    user = models.ForeignKey(User, unique=True)
    jabberid = models.EmailField(blank=True, null=True)
    defaultmap = models.ForeignKey(Map, related_name = "defaultusers", blank=True, null=True)
    playtimes = models.ManyToManyField(PlayTime)
    currentsystem = models.ForeignKey(System, related_name="activepilots", blank=True, null=True)
    lastactive = models.DateTimeField()

    class Meta:
        permissions = (('account_admin', 'Administer users and groups'),)

    def update_location(self, sys_id, charid, charname, shipname, shiptype):
        """
        Updates the cached locations dict for this user.
        """
        current_time = time.time()
        user_cache_key = 'user_%s_locations' % self.user.pk
        user_locations_dict = cache.get(user_cache_key)
        time_threshold = current_time - (60 * 15)
        location_tuple = (sys_id, charname, shipname, shiptype, current_time)
        if user_locations_dict:
            user_locations_dict.pop(charid, None)
            user_locations_dict[charid] = location_tuple
        else:
            user_locations_dict = {charid: location_tuple}
        # Prune dict to ensure we're not carrying over stale entries
        for charid, location in user_locations_dict.items():
            if location[4] < time_threshold:
                user_locations_dict.pop(charid, None)

        cache.set(user_cache_key, user_locations_dict, 60 * 15)
        return user_locations_dict

class GroupProfile(models.Model):
    """GroupProfile defines custom fields tied to each Group record."""
    group = models.OneToOneField(Group, related_name='profile')
    description = models.CharField(max_length=200, blank=True, null=True)
    regcode = models.CharField(max_length=64, blank=True, null=True)
    visible = models.BooleanField(default=True)

def create_user_profile(sender, instance, created, **kwargs):
    """Handle user creation event and create a new profile to match the new user"""
    if created:
        UserProfile.objects.create(user=instance, lastactive=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))

post_save.connect(create_user_profile, sender=User)


def create_group_profile(sender, instance, created, **kwargs):
    """Handle group creation event and create a new group profile."""
    if created:
        GroupProfile.objects.create(group=instance)

post_save.connect(create_group_profile, sender=Group)


class RegistrationForm(UserCreationForm):
    """Extends the django registration form to add fields."""
    username = forms.CharField(max_length=30, label="Username")
    email = forms.EmailField(required=False, label="E-Mail Address (Optional)")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password:")
    regcode = forms.CharField(max_length=64, label="Registration Code")

