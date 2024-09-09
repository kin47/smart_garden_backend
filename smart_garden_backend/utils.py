from authentication.models import *
import re
from . import settings
import jwt
from datetime import datetime
from django.utils import timezone
import pytz
from device_token.models import *

regexEmail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
regexPassword = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$%^&+=!])(?=.*[0-9]).{8,}$'
regexPhone = r'^0\d{9,9}$'

def valid(regex: str, sample: str) -> bool:
    if sample == None:
        return False
    
    result = re.findall(regex, sample)
    if len(result) != 1:
        return False
    
    return result[0] == sample

def getUserFromToken(accessToken: str) -> User:
    try:
        # Decode the JWT
        decoded_token = jwt.decode(accessToken, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        expired_at_timestamp = decoded_token.get('expired_at')
        expired_at = datetime.fromtimestamp(expired_at_timestamp, pytz.timezone('Asia/Ho_Chi_Minh'))
        now_local = timezone.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
        if now_local > expired_at:
            # Delete the device token that associated with this access token
            DeviceToken.objects.filter(access_token=accessToken).delete()
            return None
    except jwt.ExpiredSignatureError:
        # Delete the device token that associated with this access token
        DeviceToken.objects.filter(access_token=accessToken).delete()
        return None  # The token signature has expired
    except jwt.InvalidTokenError:
        return None  # The token is invalid
    
    user_session = UserSession.objects.filter(access_token=accessToken)
    if len(user_session) == 0:
        return None
    session = user_session[0]
    if session.deleted_at is not None:
        # Delete the device token that associated with this access token
        DeviceToken.objects.filter(access_token=accessToken).delete()
        return None
    
    return session.user_id
