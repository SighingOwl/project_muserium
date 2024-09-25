from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from ..models import Product
from ..serializers import ProductDetailSerializer

class ProductViewSets(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer

    @action(detail=False, methods=['get'])
    def get_product_detail(self, request):
        # Get the detail of a specific product

        pk = request.query_params.get('id', None)
        if pk == None:
            return Response({'error': '상품 id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_class = self.queryset.filter(pk=pk).first()
        serializer = self.get_serializer(selected_class)
        return Response(serializer.data, status=status.HTTP_200_OK)