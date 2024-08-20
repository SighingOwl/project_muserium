import boto3
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.html import escape
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Question, Answer
from glass_class.models import GlassClass
from ..forms import QuestionForm, AnswerForm
from .common import mask_username

# Glass class Question

#@login_required(login_url='#')
@require_POST
@csrf_protect
def create_class_question(request):
    # Create a Question
    
    if request.method == 'POST':

        glass_class_id = request.GET.get('glass_class_id')
        if not glass_class_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)

        glass_class = get_object_or_404(GlassClass, pk=glass_class_id) 

        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = User.objects.get(username='admin')  # 로그인 기능 추가 후 수정 필요
            question.created_at = timezone.now()
            question.glass_class = glass_class
            question.save()

            # Upload review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME   
                )

                # Upload the new image
                s3.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/questions/{question.id}/{image.name}')
                question.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/questions/{question.id}/{image.name}'

            question.save()

            return JsonResponse({
                'status': 'success',
                'message': 'question created successfully',
                'question': {
                    'id': question.id,
                    'title': escape(question.title),
                    'author': escape(question.author.username),
                    'content': escape(question.content),
                    'image': escape(question.image),
                    'is_secret': escape(question.is_secret),
                    'glass_class': escape(question.glass_class.title) if question.glass_class else None,
                    'created_at': escape(question.created_at),
                    'modified_at': escape(question.modified_at) if question.modified_at else None
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to create question',
                'errors': form.errors
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
        }, stauts=405)

def read_class_question(request):
    # Read a Question

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
        vaild_order_fields = ['-created_at', '-view_count']
        if page_order not in vaild_order_fields:
            page_order = '-created_at'

        questions = Question.objects.filter(glass_class = target_glass_class).order_by(page_order, '-created_at')
        
        paginator = Paginator(questions, page_size)

        try:
            question_list = paginator.page(page)
        except PageNotAnInteger:
            question_list = paginator.page(1)
        except EmptyPage:
            question_list = paginator.page(paginator.num_pages)
        
        question_data = []
        for question in question_list:
            answer_data = {}
            if Answer.objects.filter(question=question).exists():
                answer = Answer.objects.filter(question=question).first()
                answer_data ={
                    'id': answer.id,
                    'answered_at': answer.created_at,
                    'is_answered': True
                }

            question_data.append({
                'id': question.id,
                'title': question.title,
                'author': mask_username(question.author.username),
                'is_secret': question.is_secret,
                'view_count': question.view_count,
                'created_at': question.created_at,
                'modified_at': question.modified_at if question.modified_at else None,
                'answer': answer_data
            })

        page_attrs = {
            'count': paginator.count,
            'per_page': page_size,
            'page_range': list(paginator.page_range),
            'current_page': question_list.number,
            'previous_page': question_list.previous_page_number() if question_list.has_previous() else None,
            'next_page': question_list.next_page_number() if question_list.has_next() else None,
            'start_index': question_list.start_index(),
            'end_index': question_list.end_index(),
        }
        return JsonResponse({
            'status': 'success',
            'questions': question_data,
            'paginator': page_attrs
        }, status=200)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def get_question_content(request):
    # Get a Question content

    if request.method == 'GET':
        question_id = request.GET.get('question_id')
        if not question_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)

        question = get_object_or_404(Question, pk=question_id)
        answer = Answer.objects.filter(question=question).first()

        return JsonResponse({
            'status': 'success',
            'question': {
                'id': question.id,
                'content': question.content,
                'image': question.image,
                'answer_id': answer.id if answer else None,
                'answer_content': answer.content if answer else '',
                'answer_image': answer.image if answer else None
            }
        }, status=200)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)

#@login_required(login_url='#')
@require_POST
@csrf_protect
def update_class_question(request):
    # update a Question

    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data'
        }, status=400)

    question = get_object_or_404(Question, pk=question_id)

    '''
    로그인 기능 추가 후 실행 예정
    if request.user != question.author:
        return JsonResponse({
            'status': 'error',
            'message': 'You are not the author of this question'
        }, status=403)
    '''
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modified_at = timezone.now()

            # Update review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME   
                )

                # Delete the previous image
                if question.image:
                    existing_image_key = question.image.split(f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{settings.AWS_STORAGE_BUCKET_NAME}/')[1]
                    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

                # Upload the new image
                s3.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/questions/{question.id}/{image.name}')
                question.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/questions/{question.id}/{image.name}'

            question.save()

            return JsonResponse({
                'status': 'success',
                'message': 'question updated successfully',
                'question': {
                    'id': escape(question.id),
                    'title': escape(question.title),
                    'author': escape(question.author.username),
                    'content': escape(question.content),
                    'image': escape(question.image),
                    'is_secret': escape(question.is_secret),
                    'glass_class': escape(question.glass_class.title),
                    'created_at': escape(question.created_at),
                    'modified_at': escape(question.modified_at)
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to update question',
                'errors': form.errors
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)

#@login_required(login_url='#')
@csrf_protect
def delete_class_question(request):
    # Delete a Question

    if request.method == 'DELETE':

        question_id = request.GET.get('question_id')
        if not question_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)

        question = get_object_or_404(Question, pk=question_id)
        
        if request.user != question.author and request.user != User.objects.get(username='admin'):
            return JsonResponse({
                'status': 'error',
                'message': 'You are not the author of this question'
            }, status=403)
        else:
            # Delete review image from S3
            if question.image:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                existing_image_key = question.image.split(f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{settings.AWS_STORAGE_BUCKET_NAME}/')[1]
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

            question.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'question deleted successfully'
            }, status=200)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)

@require_POST
@csrf_protect
def increase_question_view_count(request):
    # Increase Question view count

    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data'
        }, status=400)
    
    question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        try:
            question.view_count += 1
            question.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'view count increased successfully',
                'view_count': question.view_count
            }, status=200)
        except:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to increase view count'
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
            }, status=405)

# Glass class Answer for Question

#@login_required(login_url='#')
@require_POST
@csrf_protect
def create_class_answer(request):
    # Create an answer

    '''
    로그인 기능 추가 후 실행 예정
    # Only admin can create an answer

    if request.user != User.objects.get(username='admin'):
        return JsonResponse({
            'status': 'error',
            'message': 'You are not allowed to create an answer'
        }, status=403)
    '''
    
    if request.method == 'POST':
        
        question_id = request.GET.get('question_id')
        if not question_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)

        question = get_object_or_404(Question, pk=question_id)

        if Answer.objects.filter(question=question).exists():
            return JsonResponse({
                'status': 'error',
                'message': '이미 답변된 질문입니다.'
            }, status = 400)

        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = User.objects.get(username='admin')
            answer.created_at = timezone.now()
            answer.question = question
            answer.save()

            # Upload review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME   
                )

                try:
                    # Upload the new image
                    s3.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/answers/{question.id}/{answer.id}/{image.name}')
                    answer.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/answers/{question.id}/{answer.id}/{image.name}'
                except:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Failed to upload image to S3'
                    }, status=400)

            answer.save()

            return JsonResponse({
                'status': 'success',
                'message': 'answer created successfully',
                'answer': {
                    'id': answer.id,
                    'author': escape(answer.author.username),
                    'content': escape(answer.content),
                    'question': escape(answer.question.title),
                    'created_at': escape(answer.created_at),
                    'modified_at': escape(answer.modified_at) if answer.modified_at else None
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to create answer',
                'errors': form.errors
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)

#@login_required(login_url='#')
@require_POST
@csrf_protect
def update_class_answer(request):
    # Update an answer

    '''
    로그인 기능 추가 후 실행 예정
    # Only admin can update an answer

    if request.user != User.objects.get(username='admin'):
        return JsonResponse({
            'status': 'error',
            'message': 'You are not allowed to update an answer'
        }, status=403)
    '''

    if request.method == 'POST':

        answer_id = request.GET.get('answer_id')
        if not answer_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)
        
        answer = get_object_or_404(Answer, pk=answer_id)

        form = AnswerForm(request.POST, request.FILES, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.modified_at = timezone.now()

            # Update review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME   
                )

                # Delete the previous image
                if answer.image:
                    existing_image_key = answer.image.split(f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{settings.AWS_STORAGE_BUCKET_NAME}/')[1]
                    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

                # Upload the new image
                s3.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/answers/{answer.question.id}/{answer.id}/{image.name}')
                answer.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/answers/{answer.question.id}/{answer.id}/{image.name}'

            answer.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'answer updated successfully',
                'answer': {
                    'id': escape(answer.id),
                    'author': escape(answer.author.username),
                    'content': escape(answer.content),
                    'image' : escape(answer.image),
                    'question': escape(answer.question.title),
                    'created_at': escape(answer.created_at),
                    'modified_at': escape(answer.modified_at)
                }
            }, status=200)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to update answer',
                'errors': form.errors
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)
    
#@login_required(login_url='#')
@csrf_protect
def delete_class_answer(request):
    # Delete an answer

    '''
    로그인 기능 추가 후 실행 예정
    # Only admin can delete an answer

    if request.user != User.objects.get(username='admin'):
        return JsonResponse({
            'status': 'error',
            'message': 'You are not allowed to delete an answer'
        }, status=403)
    '''

    if request.method == 'DELETE':
        answer_id = request.GET.get('answer_id')
        if not answer_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data'
            }, status=400)

        answer = get_object_or_404(Answer, pk=answer_id)

        # Delete review image to S3
        if 'image' in request.FILES:
            image = request.FILES['image']
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME   
            )

            # Delete the previous image
            if answer.image:
                existing_image_key = answer.image.split(f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{settings.AWS_STORAGE_BUCKET_NAME}/')[1]
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

        answer.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Answer deleted successfully'
        }, status=200)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)