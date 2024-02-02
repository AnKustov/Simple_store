from twilio.rest import Client
from django.conf import settings

def send_sms(phone_number, message):
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    twilio_client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER, 
        to=phone_number
    )
