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
from Alerts.method_base import AlertMethodBase
from .models import JabberAccount, JabberSubscription
from django.template.loader import render_to_string
from core.utils import get_config
from .jabber_client import JabberClient
from datetime import datetime
import pytz

class JabberAlertMethod(AlertMethodBase):
    """
    Alert method class for handling alerts via XMPP.
    """
    def send_alert(self, to_users, subject, message, from_user, sub_group):
        jid_list = []
        from_jid = get_config("JABBER_FROM_JID", None).value
        from_password = get_config("JABBER_FROM_PASSWORD", None).value
        jid_space_char = get_config("JABBER_LOCAL_SPACE_CHAR", None).value
        jabber_domain = get_config("JABBER_LOCAL_DOMAIN", None).value
        local_jabber = get_config("JABBER_LOCAL_ENABLED", None).value == "1"
        full_message = render_to_string("jabber_message.txt", {'subject': subject,
            'message': message, 'sub_group': sub_group.name,
            'from_user': from_user.username, 'time': datetime.now(pytz.utc)})
        for user in to_users:
            if self.is_registered(user, sub_group):
                if local_jabber:
                    jid_list.append(("%s@%s" % (user.username.replace(" ",
                        jid_space_char), jabber_domain)).encode('utf-8'))
                for jid in user.jabber_accounts.all():
                    jid_list.append(jid.jid.encode('utf-8'))
        if jid_list:
            client = JabberClient(jid=from_jid.encode('utf-8'),
                    password=from_password.encode('utf-8'),
                    to_list=jid_list,
                    message=full_message.encode('utf-8'))
            if client.connect():
                client.process()

    def is_registered(self, user, group):
        """
        Returns True if there is a JabberSubscription for the given user/group.
        """
        if JabberSubscription.objects.filter(user=user, group=group).count():
            return True
        else:
            return False

    def register(self, user, group):
        """
        Register the given user/group combo.
        """
        if self.is_registered(user, group):
            return True
        else:
            JabberSubscription(user=user, group=group).save()
            return True

    def unregister(self, user, group):
        """
        Remove any existing registration for the user/group combo.
        """
        if self.is_registered(user, group):
            JabberSubscription.objects.filter(user=user, group=group).all().delete()
        return True

    def description(self):
        """
        Return a one-liner to describe the method.
        """
        return "Recieve alerts via Jabber (XMPP)."

