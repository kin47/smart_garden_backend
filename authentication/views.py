from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpRequest, HttpResponse
from .models import *
import jwt
from datetime import datetime, timedelta
from smart_garden_backend import utils, settings
from .security import Bcrypt

# Create your views here.
class Login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email)
        if len(user) == 0:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Email hoặc mật khẩu không đúng'})
        else:
            user = user[0]
            if Bcrypt.checkpw(password, user.password) == False:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Email hoặc mật khẩu không đúng'})
            else:
                payload = {
                    'user_id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'phone_number': user.phone_number,
                    'avatar': user.avatar,
                    'is_admin': user.is_admin,
                    'can_predict_disease': user.can_predict_disease,
                    'can_receive_noti': user.can_receive_noti,
                    'expired_at': (datetime.now() + timedelta(seconds=settings.JWT_EXPIRES)).timestamp()
                }
                token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
                # Delete all user's session
                UserSession.objects.filter(user_id=user, deleted_at=None).update(deleted_at=datetime.now())
                # Create new session
                UserSession.objects.create(user_id=user, access_token=token, created_at=datetime.now())
                return Response(status=status.HTTP_200_OK, data={'access_token': token})
 
    
class Register(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        
        if utils.valid(utils.regexEmail, email) == False:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Email không hợp lệ'})
        if utils.valid(utils.regexPassword, password) == False:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Mật khẩu không đúng định dạng'})
        if utils.valid(utils.regexPhone, phone_number) == False:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Số điện thoại không hợp lệ'})
        
        user_with_this_email =  User.objects.filter(email=email)
        if len(user_with_this_email) > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Email đã tồn tại'})
        
        user_with_this_phone_number = User.objects.filter(phone_number=phone_number)
        if len(user_with_this_phone_number) > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Số điện thoại đã tồn tại'})
        
        user = User(email=email, password=Bcrypt.hashpw(password=password), name=name, phone_number=phone_number)
        user.save()
        
        return Response(status=status.HTTP_201_CREATED, data={'message': 'Đăng ký thành công, hãy kiểm tra email để xác thực tài khoản'})
    
    
class Logout(APIView):
    def post(self, request):
        access_token = request.headers.get('Authorization').split(' ')[1]
        user_session = UserSession.objects.filter(access_token=access_token)
        if len(user_session) == 0:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        if user_session[0].deleted_at is not None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        user_session.update(deleted_at=datetime.now())
        return Response(status=status.HTTP_200_OK, data={'message': 'Đăng xuất thành công'})
    
class Me(APIView):
    def get(self, request):
        header = request.headers.get('Authorization')
        if header == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        else:
            user_json = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'phone_number': user.phone_number,
                'avatar': user.avatar,
                'is_admin': user.is_admin,
                'can_predict_disease': user.can_predict_disease,
                'can_receive_noti': user.can_receive_noti,
                'is_verified': user.is_verified
            }
            return Response(status=status.HTTP_200_OK, data={'data': user_json})