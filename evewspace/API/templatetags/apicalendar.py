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
from django import template
import eveapi
from API import cache_handler as handler
from API.utils import timestamp_to_datetime
from API.models import *
register = template.Library()


@register.inclusion_tag("apicalendar.html")
def upcomingevents(user):
    #Get api character that corresponds with user's name, otherwise default to first
    subject = None
    for key in user.api_keys.all():
        for char in key.characters.all():
            if char.name.lower() == user.username.lower():
                subject = char
    if not subject:
        try:
            subject = user.api_keys.all()[0].characters.all()[0]
        except:
            return {'error': 'No API Key was found.'}

    #Retrieve calendar events. If unable, return error context.
    api = eveapi.EVEAPIConnection(cacheHandler=handler)
    auth = api.auth(keyID=char.apikey.keyid, vCode=char.apikey.vcode)
    try:
        result = auth.char.UpcomingCalendarEvents(characterID=subject.charid)
        result.upcomingEvents.SortBy('eventDate')
        return {'events': result.upcomingEvents}
    except eveapi.Error:
        return {'error': 'Your API Key does not allow calendar access.'}


@register.inclusion_tag("apicalendar_detail.html")
def eventdetail(event):
    return {'event': event}


@register.simple_tag()
def timestamp(timestamp):
    return timestamp_to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S")
