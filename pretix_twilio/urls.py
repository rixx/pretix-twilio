from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/settings/twilio$",
        views.TwilioSettings.as_view(),
        name="settings",
    ),
]
