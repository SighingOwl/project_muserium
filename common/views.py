import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Image, Review, QnA, Comment
from glass_class.models import GlassClass
from .forms import ImageForm, ReviewForm, QnAForm, CommentForm


# Temporary function for development
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

def mask_username(username):
    if len(username) == 2:
        return username[0] + '*'
    elif len(username) == 3:
        return username[0:2] + '*'
    elif len(username) == 4:
        return username[0:3] + '*'
    else:
        return username[0:4] + '*' * (len(username) - 4)

def upload_image(request):
    if request.method() == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'upload_image.html', {'form': form})

#@login_required(login_url='#')
@require_POST
@csrf_exempt
def create_class_review(request, glass_class_id):
    # Create a review

    if request.method == 'POST':
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
                    'author': review.author.username,
                    'content': review.content,
                    'rating': review.rating,
                    'teacher_rating': review.teacher_rating,
                    'readiness_rating': review.readiness_rating,
                    'content_rating': review.content_rating,
                    'glass_class': review.glass_class.title if review.glass_class else None,
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

def read_class_review(request, glass_class_id):
    # Read a review

    if request.method == 'GET':
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
                'modified_at': review.modified_at if review.modified_at else None
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
            'paginator': page_attrs
        }, status=200)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


#@login_required(login_url='#')
@require_POST
@csrf_exempt
def update_class_review(request, review_id):
    # update a review
    
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
                    'author': review.author.username,
                    'content': review.content,
                    'rating': review.rating,
                    'teacher_rating': review.teacher_rating,
                    'readiness_rating': review.readiness_rating,
                    'content_rating': review.content_rating,
                    'glass_class': review.glass_class.title,
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

def delete_class_review(request, review_id):
    # Delete a review
    
    review = get_object_or_404(Review, pk=review_id)
    

    if request.user != review.author:
        return JsonResponse({
            'status': 'error',
            'message': 'You are not the author of this review'
        }, status=403)
    else:
        review.delete()

# Glass class QnA
def create_class_qna(request, glass_class_id):
    # Create a QnA
    pass

def read_class_qna(request, glass_class_id):
    # Read a QnA
    pass

def update_class_qna(request, glass_class_id):
    # update a QnA
    pass

def delete_class_qna(request, glass_class_id):
    # Delete a QnA
    pass


# Glass class Comment
def create_class_comment(request):
    # Create a comment
    pass

def read_class_comment(request):
    # Read a comment
    pass

def update_class_comment(request):
    # update a comment
    pass

def delete_class_comment(request):
    # Delete a comment

    pass


