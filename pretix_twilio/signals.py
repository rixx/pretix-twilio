from django.dispatch import receiver
from django.urls import resolve, reverse
from i18nfield.strings import LazyI18nString
from pretix.base.email import get_email_context
from pretix.base.i18n import language
from pretix.base.services.mail import render_mail
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import order_placed
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


@receiver(order_placed, dispatch_uid="twilio_order_placed")
def twilio_order_placed(order, sender, **kwargs):
    from .tasks import twilio_send

    recipient = order.phone
    if not order.phone:
        return

    context = get_email_context(event=order.event, order=order)
    for k, v in order.event.meta_data.items():
        context["meta_" + k] = v

    with language(order.locale, order.event.settings.region):
        try:
            content = render_mail(
                order.event.settings.twilio_text_order_placed, context
            )
            twilio_send(text=content, to=str(recipient), event=order.event_id)
        except Exception:
            raise
        else:
            order.log_action(
                "pretix_twilio.message.sent",
                data={
                    "message": content,
                    "recipient": str(recipient),
                },
            )
