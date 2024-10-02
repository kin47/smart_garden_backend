from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from smart_garden_backend import utils 
from math import ceil
from django.db.models import Q
from .mqtt_handler import *
        
class ControlKit(APIView):
    def post(self, request, kit_id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        if id is None:
            return Response({'message': 'Thiếu trường `id`'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Initialize MQTT client
            client = mqtt.Client()
            client.on_connect = on_connect
            client.connect(MQTT_SERVER, MQTT_PORT, 60)
        
            kit = Kit.objects.get(id=kit_id)
            turn_on_pump = request.data.get('turn_on_pump')
            turn_on_light = request.data.get('turn_on_light')
            is_auto_pump = request.data.get('is_auto_pump')
            is_auto_light = request.data.get('is_auto_light')
            light_threshold = request.data.get('light_threshold')
            pump_threshold = request.data.get('pump_threshold')
            
            if turn_on_pump is not None:
                control_pump_manual(client, turn_on_pump)
            if turn_on_light is not None:
                control_light_manual(client, turn_on_light)
            if is_auto_pump is not None:
                if user.can_auto_control:
                    kit.is_auto_pump = is_auto_pump
                    control_pump_mode(client, is_auto_pump)
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Không có quyền điều khiển tự động'})
            if is_auto_light is not None:
                if user.can_auto_control:
                    kit.is_auto_light = is_auto_light
                    control_light_mode(client, is_auto_light)
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Không có quyền điều khiển tự động'})
            if light_threshold is not None:
                if user.can_auto_control:
                    kit.light_threshold = light_threshold
                    set_light_threshold(client, light_threshold)
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Không có quyền điều khiển tự động'})
            if pump_threshold is not None:
                if user.can_auto_control:
                    kit.pump_threshold = pump_threshold
                    set_pump_threshold(client, pump_threshold)
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Không có quyền điều khiển tự động'})
            kit.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Điều khiển thành công'})
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': str(e)})
        
class KitDetail(APIView):
    def get(self, request, kit_id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        if kit_id is None:
            return Response({'message': 'Thiếu trường `kit_id`'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            kit = Kit.objects.get(id=kit_id)
            kit_data = {
                'kit_id': kit.id,
                'name': kit.name,
                'is_auto_pump': kit.is_auto_pump,
                'is_auto_light': kit.is_auto_light,
                'light_threshold': kit.light_threshold,
                'pump_threshold': kit.pump_threshold,
            }
            return Response(status=status.HTTP_200_OK, data={'data': kit_data})
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': str(e)})