import os
import boto3
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.utils import timezone
from common.models import GlassClass, Product, Review, User
from common.forms import ReviewForm
from common.serializers import ReviewSerializer
from .common import mask_username


# 리소스 누수를 방지하기 위한 전역적으로 boto3 클라이언트 생성
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

# Pagination Config
class PaginationConfig(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_total_pages(self):
        if self.page.paginator.count == 0 or self.page_size == 0:
            return 0
        page_size = int(self.page_size)
        return (self.page.paginator.count + page_size - 1) // page_size

class ReviewViewSets(viewsets.ViewSet):
    queryset = Review.objects.all()
    serializer_review = ReviewSerializer
    pagination = PaginationConfig

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_review(self, request, *args, **kwargs):
        # Create a review
        
        # Check if the user has enrolled in the class or purchased the product

        # Save the review
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.created_at = timezone.now()

            if 'glass_class_id' not in request.query_params and 'product_id' not in request.query_params:
                return Response({'error': 'glass_class_id 또는 product_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

            if 'glass_class_id' in request.query_params:
                glass_class = get_object_or_404(GlassClass, pk=request.query_params.get('glass_class_id'))
                review.glass_class = glass_class
                glass_class.reviews += 1
                glass_class.total_rating += review.rating
                glass_class.average_rating = round(glass_class.total_rating / glass_class.reviews, 1)
                glass_class.save()
            elif 'product_id' in request.query_params:
                product = get_object_or_404(Product, pk=request.query_params.get('product_id'))
                review.product = product
                product.reviews += 1
                product.total_rating += review.rating
                product.average_rating = round(product.total_rating / product.reviews, 1)
                product.save()

            # Check the image is vaild
            def is_valid_image_extension(file):
                vaild_extensions = ['jpg', 'jpeg', 'png']
                ext = os.path.splitext(file.name)[1][1:].lower()
                return ext in vaild_extensions
            
            # Upload review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']
                if not is_valid_image_extension(image):
                    return Response({'error': 'image는 jpg, jpeg, png 형식이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

                # Upload the new image
                s3_client.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'reviews/{review.id}/{image.name}')
                review.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/reviews/{review.id}/{image.name}'
                review.save()

            review.save()

            return Response({'message': '리뷰가 성공적으로 등록되었습니다.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def read_review(self, request, *args, **kwargs):
        # Read a review

        # Get reviews by glass_class_id or product_id
        glass_class_id = request.query_params.get('glass_class_id')
        product_id = request.query_params.get('product_id')
        if not glass_class_id and not product_id:
            return Response({'error': 'glass_class_id 또는 product_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sorted reviews
        page_order = request.query_params.get('page_order', '-created_at')
        valid_order = ['-created_at', 'rating', '-rating']
        if page_order not in valid_order:
            page_order = '-created_at'

        if glass_class_id:
            glass_class = get_object_or_404(GlassClass, pk=glass_class_id)
            reviews = self.queryset.filter(glass_class=glass_class).order_by(page_order, '-created_at')
            average_rating = glass_class.average_rating
        elif product_id:
            product = get_object_or_404(Product, pk=product_id)
            reviews = self.queryset.filter(product=product).order_by(page_order, '-created_at')
            average_rating = product.average_rating

        # Pagination
        paginator = self.pagination()
        page = paginator.paginate_queryset(reviews, request, view=self)
        if page is not None:
            review_data = self.serializer_review(page, many=True).data
            pagenated_review = paginator.get_paginated_response(review_data)
            pagenated_review.data['total_pages'] = paginator.get_total_pages()

            # Mask the username
            for review in pagenated_review.data['results']:
                author = User.objects.get(pk=review['author'])
                review['author'] = mask_username(author.name)
                review['author_id'] = author.email

            return Response({'reviews': pagenated_review.data, 'average_rating': average_rating}, status=status.HTTP_200_OK)
            
        return Response({'message': '리뷰가 존재하지 않습니다.'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_review(self, request, *args, **kwargs):
        # Update a review

        review_id = request.query_params.get('review_id')
        if not review_id:
            return Response({'error': 'review_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        review = get_object_or_404(self.queryset, pk=review_id)
        
        # Author check
        if request.user != review.author:
            return Response({'error': '이 글의 작성자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            original_review = self.queryset.get(pk=review_id)

            glass_class = original_review.glass_class
            product = original_review.product

            if glass_class:
                glass_class.total_rating -= original_review.rating
                glass_class.save()
            elif product:
                product.total_rating -= original_review.rating
                product.save()

            review = form.save(commit=False)
            
            # Check the image is vaild
            def is_valid_image_extension(file):
                vaild_extensions = ['jpg', 'jpeg', 'png']
                ext = os.path.splitext(file.name)[1][1:].lower()
                return ext in vaild_extensions

            # Update review image to S3
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                if not is_valid_image_extension(image_file):
                    return Response({'error': 'image는 jpg, jpeg, png 형식이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

                # Delete the previous image
                if original_review.image:
                    existing_image_key = original_review.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

                # Upload the new image
                s3_client.upload_fileobj(image_file, settings.AWS_STORAGE_BUCKET_NAME, f'reviews/{review.id}/{image_file.name}')
                review.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/reviews/{review.id}/{image_file.name}'
            
            review.modified_at = timezone.now()
            review.save()

            # Update glass_class or product rating
            if glass_class:
                glass_class.total_rating += review.rating
                glass_class.average_rating = round(glass_class.total_rating / glass_class.reviews, 1)
                glass_class.save()
            elif product:
                product.total_rating += review.rating
                product.average_rating = round(product.total_rating / product.reviews, 1)
                product.save()
            
            return Response({'message': '리뷰가 성공적으로 수정되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_review(self, request, *args, **kwargs):
        # Delete a review

        review_id = request.query_params.get('review_id')
        if not review_id:
            return Response({'error': 'review_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        review = get_object_or_404(Review, pk=review_id)

        # Author check
        if request.user != review.author and request.user != User.objects.get(is_superuser=True):
            return Response({'error': '이 글의 작성자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Delete review image from S3
        if review.image:
            existing_image_key = review.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

        # Update glass_class or product rating
        glass_class = review.glass_class
        product = review.product

        if glass_class:
            glass_class.reviews -= 1
            glass_class.total_rating -= review.rating
            glass_class.average_rating = round(glass_class.total_rating / glass_class.reviews, 1) if glass_class.reviews != 0 else 0
            glass_class.save()
        elif product:
            product.reviews -= 1
            product.total_rating -= review.rating
            product.average_rating = round(product.total_rating / product.reviews, 1) if product.reviews != 0 else 0
            product.save()
        
        review.delete()

        return Response({'message': '리뷰가 성공적으로 삭제되었습니다.'}, status=status.HTTP_200_OK)