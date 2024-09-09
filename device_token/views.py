from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from smart_garden_backend import utils
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

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
        
        token = request.data.get('device_token')
        if not token:
            return Response({'message': 'Chưa có device token'}, status=status.HTTP_400_BAD_REQUEST)
        device_token = DeviceToken.objects.filter(device_token=token).first()
        if not device_token:
            DeviceToken.objects.create(device_token=token, access_token=access_token, created_at=datetime.now())
        else:
            device_token.access_token = access_token
            device_token.save()
        return Response({'message': 'Device token registered'}, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        header = request.headers.get('Authorization')
        if header == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Auth token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Auth token không hợp lệ'})  
        token = request.data.get('device_token')
        if not token:
            return Response({'message': 'Chưa có device token'}, status=status.HTTP_400_BAD_REQUEST)
        device_token = DeviceToken.objects.filter(device_token=token)
        if device_token:
            device_token.delete()
        return Response({'message': 'Device token unregistered'}, status=status.HTTP_200_OK)