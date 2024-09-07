from django.shortcuts import render
from rest_framework.views import APIView
from .models import *

# Create your views here.
class RegisterDeviceToken(APIView):
    def post(self, request):
        header = request.headers.get('Authorization')
        if header == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Auth token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Auth token không hợp lệ'})
        
        token = request.data.get('token')
        if not token:
            return Response({'message': 'Chưa có device token'}, status=status.HTTP_400_BAD_REQUEST)
        device_token = DeviceToken.objects.filter(token=token).first()
        if not device_token:
            DeviceToken.objects.create(token=token)
        return Response({'message': 'Device token registered'}, status=status.HTTP_201_CREATED)