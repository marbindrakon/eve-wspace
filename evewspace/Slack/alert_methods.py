from Alerts.method_registry import registry
from .slack_method import SlackAlertMethod
registry.register("Slack", SlackAlertMethod)
