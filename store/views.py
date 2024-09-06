from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Store
from smart_garden_backend import utils  # Assuming you have a utils module for token handling

class GetStores(APIView):
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
              store
            LIMIT %(limit)s
            OFFSET %(offset)s
            """
            params = {"limit": limit, "offset": (page - 1) * limit}
            sqlResult = Store.objects.raw(sql, params)
            
            stores_data = [
                {
                    'id': store.id,
                    'name': store.name,
                    'address': store.address,
                    'phone_number': store.phone_number,
                    'latitude': store.latitude,
                    'longitude': store.longitude
                }
                for store in sqlResult
            ]
            return Response({
                'data': stores_data
            }, status=status.HTTP_200_OK)
        except EmptyPage:
            return Response({
            'data': []
        }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': e
            }, status=status.HTTP_400_BAD_REQUEST)