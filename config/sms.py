import requests
from django.conf import settings

def parse_number(number: str):
    if len(number) > 10:
        if number.startswith("+2330"):
            number = number.replace("+2330", "0", 1)
        elif number.startswith("+"):
            number = number.replace("+233", "0", 1)
        elif number.startswith("233"):
            number = number.replace('233', '0', 1)
    return number

api_key = settings.SMS_API_KEY
def send_sms(message, recipients =[]):
    url = "https://apps.mnotify.net/smsapi?"
    
    data = {
        'key': api_key,
        'to': parse_number(recipients[0]),
        'msg': message,
        'sender_id': "VIBE",
    }
    response = requests.post(url, data=data) 
    print(response.json())
    return response.json()