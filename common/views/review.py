import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
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
                'message': 'Invalid request data'
            }, status=400)

        glass_class = get_object_or_404(GlassClass, pk=glass_class_id)

        # Check if the user has enrolled in the class
        # 클래스 수강생 관리 모델이 필요... if not glass_class.reservation        

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)

        form = ReviewForm(data)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = User.objects.get(username='admin')  # 로그인 기능 추가 후 수정 필요
            review.created_at = timezone.now()
            review.glass_class = glass_class
            review.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Review created successfully',
                'review': {
                    'id': review.id,
                    'author': escape(review.author.username),
                    'content': escape(review.content),
                    'rating': review.rating,
                    'teacher_rating': review.teacher_rating,
                    'readiness_rating': review.readiness_rating,
                    'content_rating': review.content_rating,
                    'glass_class': escape(review.glass_class.title) if review.glass_class else None,
                    'created_at': review.created_at,
                    'modified_at': review.modified_at if review.modified_at else None
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to create review',
                'errors': form.errors
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
        }, stauts=400)

def read_class_review(request):
    # Read a review

    if request.method == 'GET':

        glass_class_id = request.GET.get('glass_class_id')
        if not glass_class_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)

        target_glass_class = get_object_or_404(GlassClass, pk=glass_class_id)
        

        # Pagination
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)

        # Order by created_at by default
        page_order = request.GET.get('page_order', '-created_at')
        vaild_order_fields = ['-created_at', '-rating', 'rating']
        if page_order not in vaild_order_fields:
            page_order = '-created_at'

        reviews = Review.objects.filter(glass_class = target_glass_class).order_by(page_order, '-created_at')
        average_rating = sum([review.rating for review in reviews]) / len(reviews) if reviews else 0
        
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
            'average_rating': average_rating,
            'paginator': page_attrs
        }, status=200)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


#@login_required(login_url='#')
@require_POST
@csrf_protect
def update_class_review(request):
    # update a review

    review_id = request.GET.get('review_id')
    if not review_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data'
        }, status=400)

    review = get_object_or_404(Review, pk=review_id)

    '''
    로그인 기능 추가 후 실행 예정
    if request.user != review.author:
        return JsonResponse({
            'status': 'error',
            'message': 'You are not the author of this review'
        }, status=403)
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)
        
        form = ReviewForm(data, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.modified_at = timezone.now()
            review.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Review updated successfully',
                'review': {
                    'id': review.id,
                    'author': escape(review.author.username),
                    'content': escape(review.content),
                    'rating': review.rating,
                    'teacher_rating': review.teacher_rating,
                    'readiness_rating': review.readiness_rating,
                    'content_rating': review.content_rating,
                    'glass_class': escape(review.glass_class.title),
                    'created_at': review.created_at,
                    'modified_at': review.modified_at
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to update review',
                'errors': form.errors
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=400)

#@login_required(login_url='#')
@csrf_protect
def delete_class_review(request):
    # Delete a review
    
    review_id = request.GET.get('review_id')
    if not review_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data'
        }, status=400)

    review = get_object_or_404(Review, pk=review_id)
    
    if request.user != review.author:
        return JsonResponse({
            'status': 'error',
            'message': 'You are not the author of this review'
        }, status=403)
    else:
        review.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Review deleted successfully'
        }, status=200)