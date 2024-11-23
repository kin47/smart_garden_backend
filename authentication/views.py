from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
import jwt
from datetime import datetime, timedelta
from smart_garden_backend import utils, settings
from .security import Bcrypt
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from .tokens import account_activation_token
from django.template.loader import render_to_string
from device_token.models import DeviceToken
from firebase_admin import storage

# Create your views here
class Login(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            is_admin = request.data.get('is_admin')
            if is_admin == None:
                is_admin = False
            user = User.objects.filter(email=email)
            if len(user) == 0:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Email hoặc mật khẩu không đúng'})
            else:
                user = user[0]
                if Bcrypt.checkpw(password, user.password) == False:
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Email hoặc mật khẩu không đúng'})
                if user.is_admin != is_admin:
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Email hoặc mật khẩu không đúng'})
                if user.is_verified == False:
                    AccountVerification.activateEmail(request, user, user.email)
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Tài khoản chưa được xác thực, hãy kiểm tra email để xác thực tài khoản'})
                else:
                    payload = {
                        'user_id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'phone_number': user.phone_number,
                        'is_admin': user.is_admin,
                        'expired_at': (datetime.now() + timedelta(seconds=settings.JWT_EXPIRES)).timestamp()
                    }
                    if not user.is_admin: 
                        kit_id = None
                        if user.kit_id is not None:
                            kit_id = user.kit_id.id
                        payload = {
                            'user_id': user.id,
                            'email': user.email,
                            'name': user.name,
                            'phone_number': user.phone_number,
                            'is_admin': user.is_admin,
                            'kit_id': kit_id,
                            'expired_at': (datetime.now() + timedelta(seconds=settings.JWT_EXPIRES)).timestamp()
                        }
                    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
                    # Delete all user's session and it's old device token
                    UserSession.objects.filter(user_id=user, deleted_at=None).update(deleted_at=datetime.now())
                    # Create new session
                    print('Token Length: ', len(token)),
                    UserSession.objects.create(user_id=user, access_token=token, created_at=datetime.now())
                    return Response(status=status.HTTP_200_OK, data={'access_token': token})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': str(e)})
 
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
        
        AccountVerification.activateEmail(request, user, user.email)
        
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
                'cover_image': user.cover_image,
                'is_admin': user.is_admin,
                'can_predict_disease': user.can_predict_disease,
                'can_receive_noti': user.can_receive_noti,
                'kit_id': user.kit_id.id if user.kit_id else None,
                'is_verified': user.is_verified
            }
            return Response(status=status.HTTP_200_OK, data={'data': user_json})

class UpdateInfo(APIView):
    def put(self, request):
        header = request.headers.get('Authorization')
        if header == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        try:
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            new_name = request.data.get('new_name')
            new_avatar = request.FILES.get('new_avatar', None)  
            new_cover_image = request.FILES.get('new_cover_image', None)
            if new_avatar == None and new_cover_image == None and new_name == None and current_password == None and new_password == None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Không có thông tin nào được cập nhật'})
            if current_password == None and new_password != None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Để cập nhật mật khâu mới, bạn cần nhập cả mật khẩu hiện tại và mật khẩu mới'})
            if current_password != None and new_password == None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Để cập nhật mật khẩu mới, bạn cần nhập cả mật khẩu hiện tại và mật khẩu mới'})
            if new_name != None:
                user.name = new_name         
            if current_password != None and new_password != None:
                if Bcrypt.checkpw(current_password, user.password) == False:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Mật khẩu hiện tại không đúng'})
                if utils.valid(utils.regexPassword, new_password) == False:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Mật khẩu mới không đúng định dạng'})
                user.password = Bcrypt.hashpw(new_password)
            # Upload the image to Firebase Storage
            if new_avatar != None:
                bucket = storage.bucket()
                blob = bucket.blob(f'avatar/{user.id}_{new_avatar}_{round(1000 * datetime.timestamp(datetime.now()))}')
                blob.upload_from_file(new_avatar, content_type=new_avatar.content_type)
                blob.make_public()
                user.avatar = blob.public_url
            if new_cover_image != None:
                bucket = storage.bucket()
                blob = bucket.blob(f'cover_image/{user.id}_{new_avatar}_{round(1000 * datetime.timestamp(datetime.now()))}')
                blob.upload_from_file(new_cover_image, content_type=new_cover_image.content_type)
                blob.make_public()
                user.cover_image = blob.public_url
            user.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Cập nhật thông tin thành công'})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': str(e)})

class AccountVerification(APIView):
    def activate(request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_verified = True
            user.save()
            return render(request, 'verify_success.html')
        else:
            return render(request, 'verify_fail.html')

    def activateEmail(request, user, to_email):
        mail_subject = "Kích hoạt tài khoản Smart Garden."
        message = render_to_string("template_activate_account.html", {
            'user': user.name,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            "protocol": 'http'
        })
        email = EmailMessage(mail_subject, message, to=[to_email])
        if email.send():
            print(f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                    received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
        else:
            print(f'Problem sending email to {to_email}, check if you typed it correctly.')
            
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email)
        if len(user) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Email không tồn tại'})
        else:
            user = user[0]
            if user.is_verified == True:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Tài khoản đã được xác thực'})
            else:
                AccountVerification.activateEmail(request, user, user.email)
                return Response(status=status.HTTP_200_OK, data={'message': 'Gửi lại email xác thực thành công'})