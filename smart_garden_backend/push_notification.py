import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from . import settings

def send_fcm_notification(body):
    # FCM HTTP v1 API URL
    FCM_URL = 'https://fcm.googleapis.com/v1/projects/smart-garden-cd3b0/messages:send'
    
    # Scopes for the FCM API
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

    # Create credentials using the service account file
    credentials = service_account.Credentials.from_service_account_file(settings.SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Refresh the credentials to get a valid token
    credentials.refresh(Request())
    access_token = credentials.token
    
    # Prepare headers for HTTP v1 API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; UTF-8',
    }
    
    print('Access Token:', access_token)

    # Prepare your FCM message payload
    message = {
        "message": {
            "token": 'eBjrFCWGQPeLu7Myn0pZE2:APA91bFLAPHUfqoDjBGWZ38JJvd9k4mZ5Yv7HKNX8q0jgco_yzdousDwfkOLWVEcU3cRXKvZ7CKW33hSlI_Vd0WbAOvUmUICz8QbKTDp4_wuid-_RgrMRISv9q9iQZKipY6rmhCMZzdc',  # FCM token of the device
            "notification": {
                "title": "Smart Garden",
                "body": body
            }
        }
    }
    # Send the notification
    response = requests.post(FCM_URL, headers=headers, data=json.dumps(message))

    # Check for errors
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)

def get_user_tokens(user):
    return DeviceToken.objects.filter(user=user).values_list('token', flat=True)