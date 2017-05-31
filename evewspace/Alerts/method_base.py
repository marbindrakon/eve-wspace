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
"""
Base class for alert method interface.
"""

class AlertMethodBase(object):
    """
    This is a skeleton AlertMethod. It should handle the following:
        send_alert(to_users, message, from_user, sub_group)
            -Send alert to given to_users. Should handle an unregistered user
             gracefully.
        per_user_method()
            -Return True if this method requires per-user signup (i.e. Jabber)
             Return False if no per-user registration is required (i.e. Slack)
        register_user(user, sub_group)
            -Register the provided user and subscription group as being handled
             by this method.
        unregister_user(user, sub_group)
            -Unregister the given user and subscription group combo
        is_registered(user, sub_group)
            -Return True if the user and subscripiton group are registered
        description()
            -Return a text description of the method
    """
    def send_alert(self, to_users, message, from_user, sub_group):
        """
        Send a message to the given user with the message text, from
        and group.
        """
        # The meat of your method goes here, checking if the user
        # is registered and actually sending the alert.
        if self.is_registered(user, sub_group):
            message = "%s \n \n FROM: %s  TO: %s" % (message,
                    from_user.username, sub_group.name)
        raise NotImplementedError(message)

    def per_user_method(self):
        """
        Does this alert method require per-user registration?
        """
        return True

    def register_user(self, user, sub_group):
        """
        Register a user / subscription group combo to recieve alerts.
        """
        # You could use a model for this
        # return True if successful
        return False

    def unregister_user(self, user, sub_group):
        """
        Unregister a user / subscription group combo.
        """
        # Undo whatever you did in register_user
        # return True if successful
        return False

    def is_registered(self, user, sub_group):
        """
        Return True if the user / group combo is registered.
        """
        return False


    def description(self, user, sub_group):
        """
        Return a one-sentence descritpion of the method for the user to see.
        """
        return "A base alert method that hasn't been implemented"

    def is_bob_great(self):
        """
        Hail Bob.
        """
        return True
