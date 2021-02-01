from django.dispatch import receiver
from django.urls import resolve, reverse
from i18nfield.strings import LazyI18nString
from pretix.base.settings import settings_hierarkey
from pretix.control.signals import nav_event_settings

TWILIO_TEMPLATES = [
    "twilio_text_signature",
    "twilio_text_order_placed",
    "twilio_text_order_free",
    "twilio_text_order_changed",
    "twilio_text_order_canceled",
    "twilio_text_order_custom_mail",
    "twilio_text_download_reminder",
    "twilio_text_order_paid",
]

for settings_name in TWILIO_TEMPLATES:
    settings_hierarkey.add_default(settings_name, "", LazyI18nString)


@receiver(nav_event_settings, dispatch_uid="twilio_nav_settings")
def navbar_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    return [
        {
            "label": "Twilio",
            "url": reverse(
                "plugins:pretix_twilio:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_twilio"
            and url.url_name == "settings",
        }
    ]
