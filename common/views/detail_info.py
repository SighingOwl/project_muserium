import os
import boto3
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from common.models import GlassClass, Product, DetailInfo
from common.serializers import DetailInfoSerializer
from common.forms import DetailInfoForm

# 리소스 누수를 방지하기 위한 전역적으로 boto3 클라이언트 생성
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)# 리소스 누수를 방지하기 위한 전역적으로 boto3 클라이언트 생성
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

class DetailInfoViewSets(viewsets.ViewSet):
    # Class detail info view sets
    queryset = DetailInfo.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def get_detail_info(self, request, *args, **kwargs):
        # Get detail info

        class_id = request.query_params.get('class_id')
        product_id = request.query_params.get('product_id')
        if class_id is None and product_id is None:
            return Response({'error': 'content id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        filter_kwargs = {}
        if class_id:
            filter_kwargs['glass_class'] = class_id
        if product_id:
            filter_kwargs['product'] = product_id
        
        detail_info = self.queryset.filter(**filter_kwargs).first()
        
        if detail_info is None:
            return Response({'error': '상세정보가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DetailInfoSerializer(detail_info)
        return Response({'detail_info': serializer.data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_detail_info(self, request, *args, **kwargs):
        # Update detail info
    
        # Only admin can update detail info
        if not request.user.is_superuser:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if detail_info_id exists
        detail_info_id = request.query_params.get('detail_info_id', None)
        if detail_info_id is None:
            return Response({'error': 'detail_info_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        detail_info = get_object_or_404(DetailInfo, pk=detail_info_id)
    
        # Content Update
        form = DetailInfoForm(request.POST, request.FILES, instance=detail_info)
        if form.is_valid():
            detail_info = form.save(commit=False)

            # Function to handle S3 upload
            def upload_to_s3(file, path):
                s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, path)
                return f'{settings.AWS_S3_CUSTOM_DOMAIN}/{path}'
            
            # Function to check if file extension is valid
            def is_valid_image_extension(file):
                vaild_extensions = ['jpg', 'jpeg', 'png']
                ext = os.path.splitext(file.name)[1][1:].lower()
                return ext in vaild_extensions
    
            # Upload review image to S3
            if 'product_image' in request.FILES:
                image = request.FILES['product_image']
                if not is_valid_image_extension(image):
                    return Response({'error': 'product_image는 jpg, jpeg, png 형식이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

                detail_info.product_image = upload_to_s3(image, f'detail/{detail_info.id}/product/{image.name}')
            
            if 'notice_image' in request.FILES:
                image = request.FILES['notice_image']
                if not is_valid_image_extension(image):
                    return Response({'error': 'notice_image는 jpg, jpeg, png 형식이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

                detail_info.notice_image = upload_to_s3(image, f'detail/{detail_info.id}/notice/{image.name}')
            else:
                detail_info.notice_image = None
    
            if 'event_image' in request.FILES:
                image = request.FILES['event_image']
                if not is_valid_image_extension(image):
                    return Response({'error': 'event_image는 jpg, jpeg, png 형식이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

                detail_info.event_image = upload_to_s3(image, f'detail/{detail_info.id}/event/{image.name}')
            else:
                detail_info.event_image = None
    
            detail_info.modified_at = timezone.now()
            detail_info.save()
            
            return Response({'message': '상세정보가 성공적으로 수정되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)