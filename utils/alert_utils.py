from twilio.rest import Client
import os

def send_sms_alert(message):
    try:
        # Load environment variables
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        to_phone_number = os.getenv("TO_PHONE_NUMBER")

        # Print credentials for debugging (Do not share this in production!)
        print("Twilio Account SID:", account_sid)
        print("Twilio Auth Token:", auth_token)
        print("Twilio Phone Number:", twilio_phone_number)

        # Twilio Client
        client = Client(account_sid, auth_token)

        # Send SMS
        client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to_phone_number
        )
        print("📩 SMS Sent!")
    except Exception as e:
        print(f"⚠ Error sending SMS: {e}")
