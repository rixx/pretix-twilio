from django import forms
from django.utils.translation import gettext_lazy as _
from i18nfield.forms import I18nFormField, I18nTextarea
from pretix.base.email import get_available_placeholders
from pretix.base.forms import PlaceholderValidator, SettingsForm


class TwilioSettingsForm(SettingsForm):
    twilio_account_sid = forms.CharField(
        label=_("Account SID"),
        help_text=_("You can find your SID here: https://www.twilio.com/console"),
    )
    twilio_auth_token = forms.CharField(
        label=_("Auth token"),
        help_text=_(
            "You can find your auth token here: https://www.twilio.com/console"
        ),
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password"  # see https://bugs.chromium.org/p/chromium/issues/detail?id=370363#c7
            }
        ),
    )
    twilio_sender_number = forms.CharField(
        label=_("Sender number"),
        help_text=_(
            "Please enter the number to be used as sender. It must be one of your Twilio numbers. "
            "You can find your numbers here: https://www.twilio.com/console"
        ),
    )

    twilio_text_signature = I18nFormField(
        label=_("Signature"),
        required=False,
        widget=I18nTextarea,
        help_text=_(
            "This will be attached to every SMS. Available placeholders: {event}"
        ),
        validators=[PlaceholderValidator(["{event}"])],
        widget_kwargs={
            "attrs": {"rows": "4", "placeholder": _("e.g. your contact details")}
        },
    )
    twilio_text_order_placed = I18nFormField(
        label=_("Text sent to order contact address"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_order_paid = I18nFormField(
        label=_("Text sent to order contact address"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_order_free = I18nFormField(
        label=_("Text sent to order contact address"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_order_changed = I18nFormField(
        label=_("Text"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_waiting_list = I18nFormField(
        label=_("Text"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_order_canceled = I18nFormField(
        label=_("Text"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_order_custom_mail = I18nFormField(
        label=_("Text"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_download_reminder = I18nFormField(
        label=_("Text sent to order contact address"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_order_placed_require_approval = I18nFormField(
        label=_("Received order"),
        required=False,
        widget=I18nTextarea,
    )
    twilio_text_order_approved = I18nFormField(
        label=_("Approved order"),
        required=False,
        widget=I18nTextarea,
        help_text=_(
            "This will only be sent out for non-free orders. Free orders will receive the free order "
            "template from below instead."
        ),
    )
    twilio_text_order_approved_free = I18nFormField(
        label=_("Approved free order"),
        required=False,
        widget=I18nTextarea,
        help_text=_(
            "This will only be sent out for free orders. Non-free orders will receive the non-free order "
            "template from above instead."
        ),
    )
    twilio_text_order_denied = I18nFormField(
        label=_("Denied order"),
        required=False,
        widget=I18nTextarea,
    )
    base_context = {
        "twilio_text_order_placed": ["event", "order", "payment"],
        "twilio_text_order_free": ["event", "order"],
        "twilio_text_order_changed": ["event", "order"],
        "twilio_text_waiting_list": ["event", "waiting_list_entry"],
        "twilio_text_order_canceled": ["event", "order"],
        "twilio_text_order_custom_mail": ["event", "order"],
        "twilio_text_download_reminder": ["event", "order"],
        "twilio_text_order_placed_require_approval": ["event", "order"],
        "twilio_text_order_approved": ["event", "order"],
        "twilio_text_order_approved_free": ["event", "order"],
        "twilio_text_order_denied": ["event", "order", "comment"],
        "twilio_text_order_paid": ["event", "order", "payment_info"],
    }

    def _set_field_placeholders(self, fn, base_parameters):
        phs = [
            "{%s}" % p
            for p in sorted(
                get_available_placeholders(self.event, base_parameters).keys()
            )
        ]
        ht = _("Available placeholders: {list}").format(list=", ".join(phs))
        if self.fields[fn].help_text:
            self.fields[fn].help_text += " " + str(ht)
        else:
            self.fields[fn].help_text = ht
        self.fields[fn].validators.append(PlaceholderValidator(phs))

    def __init__(self, *args, **kwargs):
        self.event = kwargs.get("obj")
        super().__init__(*args, **kwargs)
        for k, v in self.base_context.items():
            self._set_field_placeholders(k, v)