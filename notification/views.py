from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from smart_garden_backend import utils 
from rest_framework import status
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class GetNotification(APIView):
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
              notification
            WHERE user_id = %(user_id)s
            ORDER BY time desc
            LIMIT %(limit)s
            OFFSET %(offset)s
            """
            params = {"user_id": user.id, "limit": limit, "offset": (page - 1) * limit}
            sqlResult = Notification.objects.raw(sql, params)
            
            notifications_data = [
                {
                    'id': notification.id,
                    'message': notification.message,
                    'time': notification.time,
                    'is_read': notification.is_read
                }
                for notification in sqlResult
            ]
            return Response({
                'data': notifications_data
            }, status=status.HTTP_200_OK)
        except EmptyPage:
            return Response({
            'data': []
        }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
class MarkAsRead(APIView):
    def put(self, request, id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
    
        if id is None:
            return Response({'message': 'Thiếu trường `id`'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                notification = Notification.objects.get(id=id)
                notification.is_read = True
                notification.save()
                return Response(status=status.HTTP_200_OK, data={'message': 'Đã đọc'})
            except Notification.DoesNotExist:
                return Response({'message': 'Không tìm thấy thông báo với id trên'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)