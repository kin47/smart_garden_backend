from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from authentication.models import User
from smart_garden_backend import utils 
from math import ceil
from django.db.models import Q

class UserManagement(APIView):
    def get(self, request):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        try:
            searchKey = request.query_params.get('search_key', '')
            limit = int(request.query_params.get('limit', 10))
            page = int(request.query_params.get('page', 1))
            order_by = request.query_params.get('order_by', 'id') 
            order_type = int(request.query_params.get('order_type', 1))
        except ValueError:
            return Response({'message': 'Parameters `limit`, `page`, `order_by`, and `order_type` must be valid'}, status=status.HTTP_400_BAD_REQUEST)
        
        if limit <= 0 or page <= 0:
            return Response({'message': '`limit` and `page` must be positive integers'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle ascending or descending order
        if order_type == 0:
            order_by = f'-{order_by}'  # Prepend '-' to the order_by field for descending order
        
        try:
            # Step 1: Count total number of users matching the search query using ORM
            total_count = User.objects.filter(
                is_admin=0
            ).filter(
                Q(name__icontains=searchKey) | Q(email__icontains=searchKey) | Q(phone_number__icontains=searchKey)
            ).count()

            # Calculate total number of pages
            total_pages = ceil(total_count / limit)

            # Step 2: Fetch the paginated results using ORM with ordering
            users = User.objects.filter(
                is_admin=0
            ).filter(
                Q(name__icontains=searchKey) | Q(email__icontains=searchKey) | Q(phone_number__icontains=searchKey)
            ).order_by(order_by)[((page - 1) * limit):page * limit]
            
            users_data = [
                {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'can_predict_disease': user.can_predict_disease,
                    'can_receive_noti': user.can_receive_noti,
                    'can_auto_control': user.can_auto_control,
                }
                for user in users
            ]
            
            return Response({
                'data': users_data,
                'total_pages': total_pages,
                'current_page': page,
                'total_count': total_count
            }, status=status.HTTP_200_OK)
        
        except EmptyPage:
            return Response({
                'data': [],
                'total_pages': 0,
                'current_page': page,
                'total_count': 0
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Internal server error'})      
class UpdateUserInformation(APIView):
    def put(self, request, id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or user.is_admin == False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        if id is None:
            return Response({'message': 'Thiếu trường `id`'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            can_predict_disease = request.data.get('can_predict_disease')
            can_receive_noti = request.data.get('can_receive_noti')
            can_auto_control = request.data.get('can_auto_control')
            modify_user = User.objects.get(id=id)
            if can_predict_disease is not None:
                modify_user.can_predict_disease = can_predict_disease
            if can_receive_noti is not None:
                modify_user.can_receive_noti = can_receive_noti
            if can_auto_control is not None:
                modify_user.can_auto_control = can_auto_control
            modify_user.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Cập nhật thành công'})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Internal server error'})
        
class GetUserInfo(APIView):
    def get(self, request, id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or user.is_admin == False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        if id is None:
            return Response({'message': 'Thiếu trường `id`'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=id)
            return Response({'data': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone_number': user.phone_number,
                'avatar': user.avatar,
                'can_predict_disease': user.can_predict_disease,
                'can_receive_noti': user.can_receive_noti,
                'can_auto_control': user.can_auto_control,
            }}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Không tìm thấy người dùng'})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Internal server error'})