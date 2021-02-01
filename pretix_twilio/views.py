from django.urls import reverse
from pretix.base.models.event import Event
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin

from .forms import TwilioSettingsForm


class TwilioSettings(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    permission = "can_change_settings"
    form_class = TwilioSettingsForm
    template_name = "pretix_twilio/settings.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["order_phone_asked"] = self.request.event.settings.order_phone_asked
        result[
            "order_phone_required"
        ] = self.request.event.settings.order_phone_required
        return result

    def get_success_url(self, **kwargs):
        return reverse(
            "plugins:pretix_twilio:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )
