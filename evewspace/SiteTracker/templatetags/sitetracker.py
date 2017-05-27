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

from django import template
from SiteTracker.models import Fleet, SiteType, UserSite

register = template.Library()

def get_st_context(user):
    """
    Returns a dict of myfleets, availfleets, and fleetcount.
    """
    myfleets = user.sitetrackerlogs.filter(leavetime=None).all()
    availfleets = []
    for fleet in Fleet.objects.filter(ended=None):
        if fleet.members.filter(user=user, leavetime=None).count() ==  0:
            availfleets.append(fleet)
    fleetcount = Fleet.objects.filter(ended=None).count()
    return {'myfleets': myfleets, 'availfleets': availfleets,
            'fleetcount': fleetcount, 'user': user}

@register.inclusion_tag("st_scripts.html")
def sitetracker_scripts():
    """
    Includes sitetracker scripts.

    Useful for creating sitetracker fleets from other modules for example.
    """
    return {}

@register.inclusion_tag("st_status_bar.html", takes_context=True)
def st_status_bar(context, refresh=False):
    """
    Displays the SiteTracker status bar.
    """
    dict_values = get_st_context(context['user'])
    dict_values.update({'refresh': refresh})
    return dict_values

@register.inclusion_tag("st_status.html")
def st_status(user):
    """
    Displays the status text.
    """
    return get_st_context(user)

@register.inclusion_tag("st_boss_member.html")
def st_boss_member(member):
    """
    Displays the details for a fleet member in the boss panel.
    """
    return {'member': member}

@register.inclusion_tag("st_my_fleets.html")
def st_my_fleets(user):
    """
    List of fleets which user is a member.
    """
    return get_st_context(user)

@register.inclusion_tag("st_fleet_details.html")
def st_fleet_details(fleet, user):
    """
    Details of a sitetracker fleet.
    """
    return {'fleet': fleet, 'user': user}

@register.inclusion_tag("st_member_sitelist.html")
def st_member_site_list(fleet, user):
    """
    List of sites for a user in a fleet.
    """
    pending_sites = []
    for log in UserSite.objects.filter(user=user, pending=True).all():
        pending_sites.append(log.site)
    return {'fleet': fleet, 'pending_sites': pending_sites, 'user': user}

@register.inclusion_tag("st_avail_fleets.html")
def st_avail_fleets(user):
    """
    List of available fleets.
    """
    return get_st_context(user)

@register.inclusion_tag("st_fleet_details_boss.html")
def st_fleet_details_boss(fleet, user):
    """
    Details of a sitetracker fleet when we are the boss.
    """
    return {'fleet': fleet, 'site_types': SiteType.objects.all(), 'user': user}

@register.filter("st_fleets_available")
def st_fleets_available(user):
    st_context = get_st_context(user)
    return st_context['fleetcount'] > 0

