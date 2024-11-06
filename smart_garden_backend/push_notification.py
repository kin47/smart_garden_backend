import json
import requests
from google.oauth2 import service_account
from django.utils.timezone import now
from google.auth.transport.requests import Request
from . import settings
from device_token.models import DeviceToken
from authentication.models import User
from notification.models import Notification

def send_fcm_notification(user_id, title, body):
    # FCM HTTP v1 API URL
    FCM_URL = 'https://fcm.googleapis.com/v1/projects/smart-garden-cd3b0/messages:send'
    
    # Scopes for the FCM API
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

    # Create credentials using the service account file
    credentials = service_account.Credentials.from_service_account_file(settings.SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Refresh the credentials to get a valid token
    credentials.refresh(Request())
    credential_token = credentials.token
    
    # Prepare headers for HTTP v1 API
    headers = {
        'Authorization': f'Bearer {credential_token}',
        'Content-Type': 'application/json; UTF-8',
    }
    
    print('Credential Token:', credential_token)
    
    device_tokens = get_device_tokens(user_id)

    for token in device_tokens:
        message = {
            "message": {
                "token": token,  # FCM token of the device
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }
        # Send the notification
        response = requests.post(FCM_URL, headers=headers, data=json.dumps(message))
        # Check for errors
        if response.status_code == 200:
            print(response.json())
            Notification.objects.create(user=User.objects.get(id=user_id), message=body, time=now(), is_read=False)
        else:
            print(response.text)

def get_device_tokens(user_id):
    try:
        sql = """
        SELECT DISTINCT d.id, d.device_token 
        FROM user_session as u, device_token as d
        WHERE u.user_id = %(user_id)s AND u.access_token = d.access_token
        """
        
        # Execute the raw SQL query with a dictionary of parameters
        sqlResult = DeviceToken.objects.raw(sql, {"user_id": user_id})
        
        # Extract device tokens from the result
        device_tokens = [token.device_token for token in sqlResult]
        print('Device Tokens:', device_tokens)
        return device_tokens

    except Exception as e:
        print('Error getting User Tokens:', str(e))
        return []
