import os
import boto3
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from common.models import GlassClass, Product, Question, Answer, User
from common.forms import QuestionForm, AnswerForm
from common.serializers import QuestionListSerializer, QuestionSerializer, AnswerSerializer
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

# Question ViewSets
class QuestionViewSets(viewsets.ViewSet):
    queryset = Question.objects.all()
    serializer_list_question = QuestionListSerializer
    serializer_question = QuestionSerializer
    serializer_answer = AnswerSerializer

    pagination_class = PaginationConfig

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_question(self, request, *args, **kwargs):
        # Create a Question

        # Get the class_id or product_id
        class_id = request.query_params.get('class_id')
        product_id = request.query_params.get('product_id')
        if not class_id and not product_id:
            return Response({'error': 'class_id 또는 product_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.created_at = timezone.now()

            # Increase the question count of the class or product
            if class_id:
                question.glass_class = get_object_or_404(GlassClass, pk=class_id)
                question.glass_class.questions += 1
                question.glass_class.save()
            elif product_id:
                question.product = get_object_or_404(Product, pk=product_id)
                question.product.questions += 1
                question.product.save()

            question.save()

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
                s3_client.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/questions/{question.id}/{image.name}')
                question.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/questions/{question.id}/{image.name}'
            
                question.save()

            return Response({'message': '질문이 성공적으로 등록되었습니다.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def read_question(self, request, *args, **kwargs):
        # Read the Questions

        # Order by created_at by default
        page_order = request.query_params.get('page_order', '-created_at')
        vaild_order_fields = ['-created_at', '-view_count']
        if page_order not in vaild_order_fields:
            page_order = '-created_at'

        # Get questions by class_id or product_id
        class_id = request.query_params.get('class_id')
        product_id = request.query_params.get('product_id')
        if not class_id and not product_id:
            return Response({'error': 'class_id 또는 product_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get sorted questions
        if class_id:
            questions = self.queryset.filter(glass_class=class_id).order_by(page_order, '-created_at')
        elif product_id:
            questions = self.queryset.filter(product=product_id).order_by(page_order, '-created_at')

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(questions, request, view=self)
        if page is not None:
            question_data = self.serializer_list_question(page, many=True).data
            paginated_questions = paginator.get_paginated_response(question_data)
            paginated_questions.data['total_pages'] = paginator.get_total_pages()

            # Mask the username
            for question in paginated_questions.data['results']:
                author = User.objects.get(pk=question['author'])
                question['author'] = mask_username(author.name)
            
            # Get the answer status
            for question in paginated_questions.data['results']:
                question['is_answered'] = True if Answer.objects.filter(question=question['id']).exists() else False

            return Response({'questions': paginated_questions.data}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '질문이 존재하지 않습니다.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def get_question_content(self, request, *args, **kwargs):
        # Get a Question content

        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response({'error': 'question_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        question = get_object_or_404(Question, pk=question_id)
        answer = Answer.objects.filter(question=question).first()

        # data serialization
        question_data = self.serializer_question(question).data
        answer_data = self.serializer_answer(answer).data if answer else None

        # Mask the username
        author = User.objects.get(pk=question_data['author'])
        question_data['author'] = mask_username(author.name)

        return Response({'question': question_data, 'answer': answer_data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_question(self, request, *args, **kwargs):
        # Update a Question

        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response({'error': 'question_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        question = get_object_or_404(Question, pk=question_id)

        # Author check
        if request.user != question.author:
            return Response({'error': '이 글의 작성자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Content Update
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            original_question = Question.objects.get(pk=question_id)

            question = form.save(commit=False)
            question.modified_at = timezone.now()

            # Check the image is vaild
            def is_valid_image_extension(file):
                vaild_extensions = ['jpg', 'jpeg', 'png']
                ext = os.path.splitext(file.name)[1][1:].lower()
                return ext in vaild_extensions

            # Update review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']
                if not is_valid_image_extension(image):
                    return Response({'error': 'image는 jpg, jpeg, png 형식이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

                # Delete the previous image
                if original_question.image:
                    existing_image_key = original_question.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

                # Upload the new image
                s3_client.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/questions/{question.id}/{image.name}')
                question.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/questions/{question.id}/{image.name}'
            
            question.save()

            return Response({'message': '질문이 성공적으로 수정되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_question(self, request, *args, **kwargs):
        # Delete a Question

        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response({'error': 'question_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        question = get_object_or_404(Question, pk=question_id)
        target_content = question.glass_class if question.glass_class else question.product

        # Author check
        if request.user == question.author or request.user == User.objects.get(is_superuser=True):
            # Delete answer image from S3 before deleting the question
            if Answer.objects.filter(question=question).exists():
                answer = Answer.objects.get(question=question)
                if answer.image:
                    existing_image_key = answer.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

            # Delete question image from S3
            if question.image:
                existing_image_key = question.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
                s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

            question.delete()

            target_content.questions -= 1
            target_content.save()

            return Response({'message': '질문이 성공적으로 삭제되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': '이 글의 작성자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def increase_question_view_count(self, request, *args, **kwargs):
        # Increase Question view count

        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response({'error': 'question_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        question = get_object_or_404(Question, pk=question_id)

        question.view_count += 1
        question.save()

        return Response({'message': '조회수가 성공적으로 증가되었습니다.', 'view_count': question.view_count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def is_author(self, request, *args, **kwargs):
        # Check if the user is the author of the question

        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response({'error': 'question_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        question = get_object_or_404(Question, pk=question_id)
        author = question.author

        if request.user == author:
            return Response({'is_author': True}, status=status.HTTP_200_OK)
        elif request.user == User.objects.get(is_superuser=True):
            return Response({'is_author': 'Super'}, status=status.HTTP_200_OK)
        else:
            return Response({'is_author': False}, status=status.HTTP_200_OK)

# Answer ViewSets
class AnswerViewSets(viewsets.ViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_answer(self, request, *args, **kwargs):
        # Create An Answer

        # Only admin can create an answer
        if request.user != User.objects.get(is_superuser=True):
            return Response({'error': '관리자 권한이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response({'error': 'question_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        question = get_object_or_404(Question, pk=question_id)

        # Check if the question is already answered
        if question.answered_at:
            return Response({'error': '이미 답변된 질문입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = User.objects.get(is_superuser=True)
            answer.created_at = timezone.now()
            answer.question = question
            answer.save()

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
                s3_client.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/answers/{question.id}/{answer.id}/{image.name}')
                answer.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/answers/{question.id}/{answer.id}/{image.name}'
            
            answer.save()

            question.answered_at = timezone.now()
            question.save()

            return Response({'message': '답변이 성공적으로 등록되었습니다.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_answer(self, request, *args, **kwargs):
        # Update an Answer

        # Only admin can update an answer
        if request.user != User.objects.get(is_superuser=True):
            return Response({'error': '관리자 권한이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        answer_id = request.query_params.get('answer_id')
        if not answer_id:
            return Response({'error': 'answer_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Content Update
        answer = get_object_or_404(Answer, pk=answer_id)
        form = AnswerForm(request.POST, request.FILES, instance=answer)
        if form.is_valid():
            original_answer = Answer.objects.get(pk=answer_id)

            answer = form.save(commit=False)
            answer.modified_at = timezone.now()
            
            # Check the image is vaild
            def is_valid_image_extension(file):
                vaild_extensions = ['jpg', 'jpeg', 'png']
                ext = os.path.splitext(file.name)[1][1:].lower()
                return ext in vaild_extensions

            # Update review image to S3
            if 'image' in request.FILES:
                image = request.FILES['image']
                if not is_valid_image_extension(image):
                    return Response({'error': 'image는 jpg, jpeg, png 형식이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

                # Delete the previous image
                if original_answer.image:
                    existing_image_key = original_answer.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

                # Upload the new image
                s3_client.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, f'qnas/answers/{answer.question.id}/{answer.id}/{image.name}')
                answer.image = f'{settings.AWS_S3_CUSTOM_DOMAIN}/qnas/answers/{answer.question.id}/{answer.id}/{image.name}'
            
            answer.save()

            return Response({'message': '답변이 성공적으로 수정되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': '입력 항목에 부적절한 값이나 누락된 값이 있습니다.', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_answer(self, request, *args, **kwargs):
        # Delete an Answer

        # Only admin can delete an answer
        if request.user != User.objects.get(is_superuser=True):
            return Response({'error': '관리자 권한이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        answer_id = request.query_params.get('answer_id')
        if not answer_id:
            return Response({'error': 'answer_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        answer = get_object_or_404(Answer, pk=answer_id)

        # Update question's answered_at field
        question = answer.question
        question.answered_at = None
        question.save()

        # Delete review image to S3
        if answer.image:
            existing_image_key = answer.image.split(f'{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]
            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_image_key)

        answer.delete()

        return Response({'message': '답변이 성공적으로 삭제되었습니다.'}, status=status.HTTP_200_OK)