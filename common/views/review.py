import boto3
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils.html import escape
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Review
from glass_class.models import GlassClass
from ..forms import ReviewForm
from .common import mask_username


# 리소스 누수를 방지하기 위한 전역적으로 boto3 클라이언트 생성
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

# Glass class Review

#@login_required(login_url='#')
@require_POST
@csrf_protect
def create_class_review(request):
    # Create a review

    if request.method == 'POST':

        glass_class_id = request.GET.get('glass_class_id')
        if not glass_class_id:
            return JsonResponse({
                'status': 'error',
                'message': 'glass_class_id가 필요합니다.'
            }, status=400)

        glass_class = get_object_or_404(GlassClass, pk=glass_class_id)

        # Check if the user has enrolled in the class
        # 클래스 수강생 관리 모델이 필요... if not glass_class.reservation        


        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = User.objects.get(username='admin')  # 로그인 기능 추가 후 수정 필요
            review.created_at = timezone.now()
            review.glass_class = glass_class

            review.save()
            
            # Upload review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']

                # Upload the new image
                s3_client.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'reviews/{review.id}/{image.name}')
                review.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/reviews/{review.id}/{image.name}'

            review.save()

            glass_class.reviews += 1
            glass_class.total_rating += review.rating
            glass_class.average_rating = round(glass_class.total_rating / glass_class.reviews, 1)

            glass_class.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Review created successfully',
                'review': {
                    'id': review.id,
                    'author': escape(review.author.username),
                    'content': escape(review.content),
                    'image': escape(review.image),
                    'rating': escape(review.rating),
                    'teacher_rating': escape(review.teacher_rating),
                    'readiness_rating': escape(review.readiness_rating),
                    'content_rating': escape(review.content_rating),
                    'glass_class': escape(review.glass_class.title) if review.glass_class else None,
                    'created_at': escape(review.created_at),
                    'modified_at': escape(review.modified_at) if review.modified_at else None
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.',
                'errors': form.errors
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': '부적절한 요청 메소드입니다.'
        }, stauts=405)

def read_class_review(request):
    # Read a review

    if request.method == 'GET':

        glass_class_id = request.GET.get('glass_class_id')
        if not glass_class_id:
            return JsonResponse({
                'status': 'error',
                'message': 'glass_class_id가 필요합니다.'
            }, status=400)

        glass_class = get_object_or_404(GlassClass, pk=glass_class_id)
        

        # Pagination
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)

        # Order by created_at by default
        page_order = request.GET.get('page_order', '-created_at')
        vaild_order_fields = ['-created_at', '-rating', 'rating']
        if page_order not in vaild_order_fields:
            page_order = '-created_at'

        reviews = Review.objects.filter(glass_class = glass_class).order_by(page_order, '-created_at')
        
        paginator = Paginator(reviews, page_size)

        try:
            review_list = paginator.page(page)
        except PageNotAnInteger:
            review_list = paginator.page(1)
        except EmptyPage:
            review_list = paginator.page(paginator.num_pages)
        
        review_data = []
        for review in review_list:
            review_data.append({
                'id': review.id,
                'author': mask_username(review.author.username),
                'content': review.content,
                'image': review.image,
                'rating': review.rating,
                'teacher_rating': review.teacher_rating,
                'readiness_rating': review.readiness_rating,
                'content_rating': review.content_rating,
                'glass_class': review.glass_class.title,
                'created_at': review.created_at,
                'modified_at': review.modified_at if review.modified_at else None,
            })

        page_attrs = {
            'count': paginator.count,
            'per_page': page_size,
            'page_range': list(paginator.page_range),
            'current_page': review_list.number,
            'previous_page': review_list.previous_page_number() if review_list.has_previous() else None,
            'next_page': review_list.next_page_number() if review_list.has_next() else None,
            'start_index': review_list.start_index(),
            'end_index': review_list.end_index(),
        }
        return JsonResponse({
            'status': 'success',
            'reviews': review_data,
            'average_rating': glass_class.average_rating,
            'paginator': page_attrs
        }, status=200)
    
    return JsonResponse({
        'status': 'error',
        'message': '부적절한 요청 메소드입니다.'
    }, status=405)


#@login_required(login_url='#')
@require_POST
@csrf_protect
def update_class_review(request):
    # update a review

    review_id = request.GET.get('review_id')
    if not review_id:
        return JsonResponse({
            'status': 'error',
            'message': 'review_id가 필요합니다.'
        }, status=400)

    review = get_object_or_404(Review, pk=review_id)

    '''
    로그인 기능 추가 후 실행 예정
    if request.user != review.author:
        return JsonResponse({
            'status': 'error',
            'message': '이 글의 작성자가 아닙니다.'
        }, status=403)
    '''
    if request.method == 'POST':

        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            original_review = Review.objects.get(pk=review_id)

            # Get existing glass_class rating before updating
            glass_class = original_review.glass_class
            glass_class.total_rating -= original_review.rating
            glass_class.save()

            review = form.save(commit=False)
            review.modified_at = timezone.now()

            # Update review image to S3
            if 'image' in request.FILES:
                image_file = request.FILES['image']

                # Delete the previous image
                if original_review.image:
                    existing_image_key = original_review.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

                # Upload the new image
                s3_client.upload_fileobj(image_file, settings.AWS_STORAGE_BUCKET_NAME, f'reviews/{review.id}/{image_file.name}')
                review.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/reviews/{review.id}/{image_file.name}'

            review.save()

            # Update glass_class rating
            glass_class.total_rating += review.rating
            glass_class.average_rating = round(glass_class.total_rating / glass_class.reviews, 1)
            glass_class.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Review updated successfully',
                'review': {
                    'id': escape(review.id),
                    'author': escape(review.author.username),
                    'content': escape(review.content),
                    'image': escape(review.image),
                    'rating': escape(review.rating),
                    'teacher_rating': escape(review.teacher_rating),
                    'readiness_rating': escape(review.readiness_rating),
                    'content_rating': escape(review.content_rating),
                    'glass_class': escape(review.glass_class.title),
                    'created_at': escape(review.created_at),
                    'modified_at': escape(review.modified_at)
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.',
                'errors': form.errors
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': '부적절한 요청 메소드입니다.'
        }, status=405)

#@login_required(login_url='#')
@csrf_protect
def delete_class_review(request):
    # Delete a review
    
    if request.method == 'DELETE':
        review_id = request.GET.get('review_id')
        if not review_id:
            return JsonResponse({
                'status': 'error',
                'message': 'review_id가 필요합니다.'
            }, status=400)
        
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({
                'status': 'error',
                'message': 'user_id가 필요합니다.'
            }, status=400)

        review = get_object_or_404(Review, pk=review_id)
        user = get_object_or_404(User, pk=user_id)
        
        if user == review.author or user == User.objects.get(username='admin'):
            # Delete review image from S3
            if review.image:
                existing_image_key = review.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
                s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

            # Update glass_class rating
            glass_class = review.glass_class
            glass_class.reviews -= 1
            glass_class.total_rating -= review.rating
            glass_class.average_rating = round(glass_class.total_rating / glass_class.reviews, 1)
            glass_class.save()

            review.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Review deleted successfully'
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': '이 글의 작성자가 아닙니다.'
            }, status=403)
    else:
        return JsonResponse({
            'status': 'error',
            'message': '부적절한 요청 메소드입니다.'
        }, status=405)
    