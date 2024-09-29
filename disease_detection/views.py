from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from smart_garden_backend import utils
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import json
import os
from tensorflow.keras.preprocessing.image import load_img
from PIL import Image
from datetime import datetime
from firebase_admin import storage

model = load_model('model.h5')

# Create your views here.
class HistoryPredictDisease(APIView):
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
              predict_history
            WHERE user_id = %(user_id)s
            ORDER BY send_at desc
            LIMIT %(limit)s
            OFFSET %(offset)s
            """
            params = {"user_id": user.id, "limit": limit, "offset": (page - 1) * limit}
            sqlResult = PredictHistory.objects.raw(sql, params)
            
            predict_history_data = [
                {
                    'id': predict.id,
                    'image': predict.image,
                    'plant': predict.disease_id.tree_id.name,
                    'disease': predict.disease_id.disease_name,
                    'send_at': predict.send_at
                }
                for predict in sqlResult
            ]
            return Response({
                'data': predict_history_data
            }, status=status.HTTP_200_OK)
        except EmptyPage:
            return Response({
            'data': []
        }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DiseaseDetection(APIView):
    def post(self, request):
        header = request.headers.get('Authorization')
        if header is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        access_token = header.split(' ')[1]
        user = utils.getUserFromToken(access_token)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'message': 'Token không hợp lệ'})
        
        try:
            image = request.FILES['image']
            filename = image.name
            print("@@ Input posted = ", filename)
            
            image_name = f'{round(1000 * datetime.timestamp(datetime.now()))}_{filename}'
            
            # Upload the image to Firebase Storage
            bucket = storage.bucket()
            blob = bucket.blob(f'disease_detection/{image_name}')
            blob.upload_from_file(image, content_type=image.content_type)
            blob.make_public()  # Make the image publicly accessible
            image_url = blob.public_url  # Get the public URL of the image
            
            print("@@ Predicting class......")
            # Open the image directly from the uploaded file
            pil_image = Image.open(image).convert('RGB')
            pil_image = pil_image.resize((128, 128))  # Resize the image

            # Convert to numpy array and normalize
            print("@@ Got Image for prediction")
            test_image = img_to_array(pil_image) / 255.0
            test_image = np.expand_dims(test_image, axis=0)  # Add batch dimension

            result = model.predict(test_image)  # predict diseased plant or not
            print("@@ Raw result = ", result)

            pred = np.argmax(result, axis=1)[0]

            disease = Disease.objects.get(pk=pred)
            data = {
                'image': image_url,
                'plant': disease.tree_id.name,
                'disease': disease.disease_name,
                'treatment': disease.treatment,
                'reference': disease.reference,
            }
            
            PredictHistory.objects.create(
                user_id = user,
                image=image_url,
                disease_id=disease,
                send_at=datetime.now()
            )
            return Response(status=status.HTTP_200_OK, data={'data': data})
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)