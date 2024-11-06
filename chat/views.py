from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from smart_garden_backend import utils 
from rest_framework import status
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection

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
            last_id = request.query_params.get('last_id')
            user_id = request.query_params.get('user_id')
            if user.is_admin and user_id is None:
                return Response({'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'message': 'Parameters `limit` and `page` must be integers'}, status=status.HTTP_400_BAD_REQUEST)
        if limit <= 0:
            return Response({'message': '`limit` and `page` must be positive integers'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sql = ""
            user_id_for_sql = user_id if user.is_admin else user.id
            if last_id is None:
                # If last_id is None, fetch the most recent messages
                sql = """
                SELECT *
                FROM chat
                WHERE user_id = %(user_id)s
                ORDER BY time DESC
                LIMIT %(limit)s
                """
                params = {"user_id": user_id_for_sql, "limit": limit}
            else:
                # Fetch messages with id less than last_id for subsequent pages
                sql = """
                SELECT *
                FROM chat
                WHERE user_id = %(user_id)s
                AND id < %(last_id)s
                ORDER BY time DESC
                LIMIT %(limit)s
                """
                params = {"user_id": user_id_for_sql, "last_id": last_id, "limit": limit}
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
            
class GetChatList(APIView):
    def get(self, request):
        # Get query parameters for pagination and search
        page = int(request.query_params.get('page', 1))  # Default to 0 if not provided
        limit = int(request.query_params.get('limit', 10))   # Default to 10 if not provided
        search_key = request.query_params.get('search_key', '')
        
        if limit <= 0 or page <= 0:
            return Response({'message': '`limit` and `page` must be positive integers'}, status=status.HTTP_400_BAD_REQUEST)

        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or not user.is_admin:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        try:
            # Build the SQL query with pagination and optional search by username
            query = '''
                SELECT 
                    u.id AS user_id,
                    u.avatar AS avatar,
                    u.name AS username,
                    c_last.message AS last_message,
                    c_last.time AS last_message_time,
                    c_last.sender AS sender,
                    COUNT(CASE WHEN c.is_admin_read = 0 THEN 1 END) AS unreadMessageCount
                FROM 
                    User u
                LEFT JOIN 
                    Chat c_last ON u.id = c_last.user_id
                    AND c_last.time = (
                        SELECT MAX(c2.time)
                        FROM Chat c2
                        WHERE c2.user_id = u.id
                    )
                LEFT JOIN 
                    Chat c ON u.id = c.user_id
                WHERE 
                    u.is_admin = 0  -- Exclude admin users
            '''
            
            # Add search condition if searchKey is provided
            if search_key:
                query += " AND u.name LIKE %s"
                search_key = f"%{search_key}%"  # Use wildcard for partial matching

            # Group and order the results
            query += '''
                GROUP BY 
                    u.id, u.avatar, u.name, c_last.message, c_last.time, c_last.sender
                ORDER BY 
                    c_last.time DESC
                LIMIT %s OFFSET %s;
            '''

            params = [search_key, limit, (page - 1) * limit] if search_key else [limit, (page - 1) * limit]

            # Execute the query with the provided parameters
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                # Building a response with the fetched data
                chat_list = []
                for row in rows:
                    chat_list.append({
                        'user_id': row[0],
                        'avatar': row[1],
                        'username': row[2],
                        'last_message': row[3],
                        'last_message_time': row[4],
                        'sender': row[5],
                        'unreadMessageCount': row[6]
                    })
                
                return Response({
                    'data': chat_list
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)