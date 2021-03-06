from django.utils.translation import gettext_lazy

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

__version__ = "0.9.0"


class PluginApp(PluginConfig):
    name = "pretix_twilio"
    verbose_name = "Send SMS with Twilio"

    class PretixPluginMeta:
        name = gettext_lazy("Send SMS with Twilio")
        author = "Tobias Kunze"
        description = gettext_lazy(
            "Additionally to sending emails with pretix, send SMS to your customers with Twilio! Uses the built-in phone number field."
        )
        visible = True
        version = __version__
        category = "FEATURE"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA
        from . import tasks  # NOQA


default_app_config = "pretix_twilio.PluginApp"
