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
from __future__ import absolute_import
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
