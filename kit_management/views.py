from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from smart_garden_backend import utils 
from math import ceil
from django.db.models import Q
from kit.models import Kit
from authentication.models import User

class GetKits(APIView):
    def get(self, request):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or user.is_admin == False:
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
            total_count = Kit.objects.filter(
                Q(name__icontains=searchKey)
            ).count()

            # Calculate total number of pages
            total_pages = ceil(total_count / limit)

            # Step 2: Fetch the paginated results using ORM with ordering
            kits = Kit.objects.filter(
                Q(name__icontains=searchKey)
            ).order_by(order_by)[((page - 1) * limit):page * limit]
            
            kits_data = [
                {
                    'id': kit.id,
                    'name': kit.name,
                    'password': kit.password,
                    'is_auto_pump': kit.is_auto_pump,
                    'is_auto_light': kit.is_auto_light,
                    'light_threshold': kit.light_threshold,
                    'pump_threshold': kit.pump_threshold,
                    'number_of_connections': User.objects.filter(kit_id=kit.id).count()
                }
                for kit in kits
            ]
            
            return Response({
                'data': kits_data,
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
        
class UserInKit(APIView):
    def get(self, request, kit_id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or user.is_admin == False:
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
              user
            WHERE user.kit_id = %(kit_id)s
            LIMIT %(limit)s
            OFFSET %(offset)s
            """
            params = {"limit": limit, "offset": (page - 1) * limit, "kit_id": kit_id}
            sqlResult = User.objects.raw(sql, params)
            
            users_data = [
                {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                }
                for user in sqlResult
            ]
            return Response({
                'data': users_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Internal server error'})
        
    def delete(self, request, kit_id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or user.is_admin == False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(kit_id=kit_id, id=user_id)
            user.kit_id = None
            user.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Xóa thành công'})
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Không tìm thấy user'})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Internal server error'})

class AddUser(APIView):
    def post(self, request, kit_id):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or user.is_admin == False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
            user.kit_id = Kit.objects.get(id=kit_id)
            user.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Thêm thành công'})
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Không tìm thấy user'})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Internal server error'})
        
class SearchUser(APIView):
    def get(self, request):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None or user.is_admin == False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        try:
            searchKey = request.query_params.get('search_key', '')
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
              user
            WHERE (user.name LIKE %(searchKey)s OR user.email LIKE %(searchKey)s)
            and user.kit_id is null and user.is_admin = 0
            LIMIT %(limit)s
            OFFSET %(offset)s
            """
            params = {"limit": limit, "offset": (page - 1) * limit, "searchKey": f'%{searchKey}%'}
            sqlResult = User.objects.raw(sql, params)
            
            users_data = [
                {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                }
                for user in sqlResult
            ]
            return Response({
                'data': users_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Internal server error'})