from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from common.models import GlassClass, Product, User, Like

class LikeViewSets(viewsets.ViewSet):
    queryset = Like.objects.all()
    permission_classes = (AllowAny,)

    '''
    Like functions for classes
    '''
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def like_class(self, request, *args, **kwargs):
        # Like or Unlike a class or a product
        
        class_id = request.query_params.get('class_id', None)
        if not class_id:
            return Response({'error': 'class_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        is_like = request.data.get('is_like', False)

        glass_class = get_object_or_404(GlassClass, pk=class_id)

        # 사용자가 좋아요를 누른 여부에 따라 좋아요 수를 증가하가나 감소
        if is_like:
            like = Like(
                user=request.user,
                glass_class=glass_class,
                created_at=timezone.now()
            )
            like.save()

            glass_class.likes += 1
            glass_class.save()
            return Response({'message': glass_class.title + '의 좋아요가 1 증가되었습니다.'}, status=status.HTTP_200_OK)
        else:
            like = self.queryset.filter(
                user=request.user,
                glass_class=glass_class
            )
            like.delete()

            glass_class.likes -= 1
            glass_class.save()
            return Response({'message': glass_class.title + '의 좋아요가 1 감소되었습니다.'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def is_like_class(self, request, *args, **kwargs):
        # Check if the user liked a class
        class_id = request.query_params.get('class_id')
        if not class_id:
            return Response({'error': 'class_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user:
            return Response({'is_like': False}, status=status.HTTP_200_OK)

        glass_class = get_object_or_404(GlassClass, pk=class_id)
        is_like = self.queryset.filter(user=request.user, glass_class=glass_class).exists()

        return Response({'is_like': is_like}, status=status.HTTP_200_OK)
    
    '''
    Like functions for products
    '''
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def like_product(self, request, *args, **kwargs):
        # Like or Unlike a product

        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        is_like = request.data.get('is_like', False)

        product = get_object_or_404(Product, pk=product_id)

        # 사용자가 좋아요를 누른 여부에 따라 좋아요 수를 증가하가나 감소
        if is_like:
            like = Like(
                user=request.user,
                product=product,
                created_at=timezone.now()
            )
            like.save()

            product.likes += 1
            product.save()

            return Response({'message': product.title + '의 좋아요가 1 증가되었습니다.'}, status=status.HTTP_200_OK)
        else:
            like = self.queryset.filter(
                user=request.user,
                product=product
            )
            like.delete()

            product.likes -= 1
            product.save()

            return Response({'message': product.title + '의 좋아요가 1 감소되었습니다.'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def is_like_product(self, request, *args, **kwargs):
        # Check if the user liked a product
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user:
            return Response({'is_liked': False}, status=status.HTTP_200_OK)

        product = get_object_or_404(Product, pk=product_id)
        is_liked = self.queryset.filter(user=request.user, product=product).exists()

        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)