from decimal import Decimal
from django.dispatch import receiver
from django.urls import resolve, reverse
from i18nfield.strings import LazyI18nString
from pretix.base.email import get_email_context
from pretix.base.i18n import language
from pretix.base.services.mail import render_mail
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import order_canceled, order_changed, order_paid, order_placed
from pretix.control.signals import nav_event_settings

TWILIO_TEMPLATES = [
    "twilio_text_signature",
    "twilio_text_order_placed",
    "twilio_text_order_free",
    "twilio_text_order_changed",
    "twilio_text_order_canceled",
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


def twilio_order_message(order, template_name):
    from .tasks import twilio_send

    recipient = order.phone
    if not order.phone:
        return

    context = get_email_context(event=order.event, order=order)
    for k, v in order.event.meta_data.items():
        context["meta_" + k] = v

    with language(order.locale, order.event.settings.region):
        template = order.event.settings.get(f"twilio_text_{template_name}")
        if not str(template):
            return

        try:
            content = render_mail(template, context)
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


@receiver(order_placed, dispatch_uid="twilio_order_placed")
def twilio_order_placed(order, sender, **kwargs):
    payment = order.payments.first()
    if (
        payment
        and payment.provider == "free"
        and order.pending_sum == Decimal("0.00")
        and not order.require_approval
    ):
        twilio_order_message(order, "order_free")
    else:
        twilio_order_message(order, "order_placed")


@receiver(order_paid, dispatch_uid="twilio_order_paid")
def twilio_order_paid(order, sender, **kwargs):
    twilio_order_message(order, "order_paid")


@receiver(order_canceled, dispatch_uid="twilio_order_canceled")
def twilio_order_canceled(order, sender, **kwargs):
    twilio_order_message(order, "order_canceled")


@receiver(order_changed, dispatch_uid="twilio_order_changed")
def twilio_order_changed(order, sender, **kwargs):
    twilio_order_message(order, "order_changed")
