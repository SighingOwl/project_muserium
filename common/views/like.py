from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..models import GlassClass, Like
from django.utils import timezone

class LikeViewSets(viewsets.ViewSet):
    queryset = Like.objects.all()

    @action(detail=False, methods=['post'])
    def like_class(self, request):
        # Like or Unlike a class

        if request.method == 'POST':
            class_id = request.data.get('class_id')
            if not class_id:
                print('class_id가 필요합니다.')
                return Response({'error': 'class_id가 필요합니다.'}, status=400)

            user_id = request.data.get('user_id')
            if user_id == None:
                print('user_id가 필요합니다.')
                return Response({'error': 'user_id가 필요합니다.'}, status=400)

            is_like = request.data.get('is_like', False)

            user = get_object_or_404(User, pk=user_id)
            glass_class = get_object_or_404(GlassClass, pk=class_id)

            if is_like:
                like = Like(
                    user=user,
                    glass_class=glass_class,
                    created_at=timezone.now()
                )
                like.save()

                glass_class.likes += 1
                glass_class.save()
            else:
                like = self.filter_queryset(self.get_queryset()).filter(
                    user=user,
                    glass_class=glass_class
                )
                like.delete()

                glass_class.likes -= 1
                glass_class.save()

            return Response({'success': 'success'})
        else:
            return Response({'error': 'POST method를 사용해주세요.'}, status=405)
    
    @action(detail=False, methods=['get'])
    def is_like_class(self, request):
        # Check if the user liked a class

        if request.method == 'GET':
            class_id = request.query_params.get('class_id')
            if not class_id:
                return Response({'error': 'class_id가 필요합니다.'}, status=400)
            
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'error': 'user_id가 필요합니다.'}, status=400)
            
            user = get_object_or_404(User, pk=user_id)
            glass_class = get_object_or_404(GlassClass, pk=class_id)
            is_like = Like.objects.filter(user=user, glass_class=glass_class).exists()

            return Response({'is_like': is_like})
        else:
            return Response({'error': 'GET method를 사용해주세요.'}, status=405)