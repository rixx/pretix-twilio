from django_scopes import scope, scopes_disabled
from pretix.base.models import Event
from pretix.celery_app import app
from twilio.rest import Client


@app.task()
def twilio_send_task(text: str, to: str, event: int):
    if not (text and to and event):
        return

    with scopes_disabled():
        event = Event.objects.get(id=event)

    with scope(organizer=event.organizer):
        client = Client(
            event.settings.twilio_account_sid, event.settings.twilio_auth_token
        )
        sender = event.settings.twilio_sender_number
        sender = sender.replace(" ", "")
        to = to.replace(" ", "")

        if event.settings.twilio_text_signature:
            text = f"{text}\n\n{event.settings.twilio_text_signature}"

        client.messages.create(to=to, from_=sender, body=text)  # returns the message


def twilio_send(*args, **kwargs):
    twilio_send_task.apply_async(args=args, kwargs=kwargs)
