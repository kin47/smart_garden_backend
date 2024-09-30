from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from smart_garden_backend import utils 
from math import ceil
from django.db.models import Q
        
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
        