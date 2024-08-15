from .models import *
import re

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
        user_session = UserSession.objects.filter(access_token=accessToken)
        if len(user_session) == 0:
            return None
        
        return user_session[0].user_id