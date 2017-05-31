from Alerts.method_registry import registry
from .jabber_method import JabberAlertMethod
registry.register("Jabber", JabberAlertMethod)
