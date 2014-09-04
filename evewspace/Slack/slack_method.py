from Alerts.method_base import AlertMethodBase
from core.utils import get_config
from models import SlackChannel
import json
import requests

class SlackAlertMethod(AlertMethodBase):
    def per_user_method(self):
        # Slack is mapped on a channel basis, so per-user registration is
        # silly for this method
        return False

    def send_alert(self, to_users, subject, message, from_user, sub_group):
        subdomain = get_config("SLACK_SUBDOMAIN", None).value

        if self.exists(sub_group):
            header = '%s - %s' % (from_user.username, subject)
            channel = SlackChannel.objects.get(group=sub_group)
            destination = "https://%s.slack.com/services/hooks/incoming-webhook?token=%s" % (subdomain, channel.token)
            payload = {'payload':json.dumps({'channel': channel.channel,
                'username': "PingBOT",
                'attachments':[{'fallback': "New alert!",
                    'fields':[{'title': header, 'value': message}]}]})}
            requests.post(destination, data=payload)

    def exists(self, group):
        """
        Returns True if there is a SlackChannel for the given group.
        """
        bool(SlackChannel.objects.filter(group=group).count())

    def description(self):
        """
        Return a one-liner to describe the method.
        """
        return u"Recieve alerts via Slack."
