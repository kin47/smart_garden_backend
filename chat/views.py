from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from smart_garden_backend import utils 
from rest_framework import status
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
class GetChatMessages(APIView):
    def get(self, request):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        try:
            limit = int(request.query_params.get('limit', 10))
            page = int(request.query_params.get('page', 1))
        except ValueError:
            return Response({'message': 'Parameters `limit` and `page` must be integers'}, status=status.HTTP_400_BAD_REQUEST)
        if limit <= 0 or page <= 0:
            return Response({'message': '`limit` and `page` must be positive integers'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sql = """
            SELECT 
              *
            FROM
              chat
            WHERE user_id = %(user_id)s
            ORDER BY time desc
            LIMIT %(limit)s
            OFFSET %(offset)s
            """
            params = {"user_id": user.id, "limit": limit, "offset": (page - 1) * limit}
            sqlResult = Chat.objects.raw(sql, params)
            
            chat_message_data = [
                {
                    'id': data.id,
                    'message': data.message,
                    'time': data.time,
                    'sender': 1 if data.sender else 0,
                    'is_user_read': data.is_user_read,
                    'is_admin_read': data.is_admin_read
                }
                for data in sqlResult
            ]
            return Response({
                'data': chat_message_data
            }, status=status.HTTP_200_OK)
        except EmptyPage:
            return Response({
            'data': []
        }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
class SendMessage(APIView):
    def post(self, request):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        try:
            message = request.data.get('message')
            sender = request.data.get('sender')
            time = request.data.get('time')
            if sender == 0:
                chat = Chat.objects.create(user=user, message=message, time=time, sender=sender, is_user_read=True, is_admin_read=False)
                return Response({'data': {
                    'id': chat.id,
                    'message': chat.message,
                    'time': chat.time,
                    'sender': sender,
                    'is_user_read': chat.is_user_read,
                    'is_admin_read': chat.is_admin_read
                }}, status=status.HTTP_201_CREATED)
            elif sender == 1:
                user_id = request.data.get('user_id')
                if user_id is None:
                    return Response({'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.get(id=user_id)
                if user is None:
                    return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
                chat = Chat.objects.create(user=user, message=message, time=time, sender=sender, is_user_read=False, is_admin_read=True)
                return Response({'data': {
                    'id': chat.id,
                    'message': chat.message,
                    'time': chat.time,
                    'sender': sender,
                    'is_user_read': chat.is_user_read,
                    'is_admin_read': chat.is_admin_read
                }}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)