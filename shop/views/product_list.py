from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from ..models import Product
from ..serializers import ProductSerializer

class PaginationConfig(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_total_pages(self):
        if self.page.paginator.count == 0 or self.page_size == 0:
            return 0
        page_size = int(self.page_size)
        return (self.page.paginator.count + page_size - 1) // page_size

class ProductListViewSets(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = PaginationConfig

    @action(detail=False, methods=['get'])
    def list_products(self, request):
        # List all products with sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        vaild_sort_by = ['-created_at', 'title', 'price', '-price', '-likes', '-average_rating']
        if sort_by not in vaild_sort_by:
            return Response({'error': '잘못된 정렬 기준입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset()).order_by(sort_by)
        if queryset.count() == 0:
            return Response({'error': '상품이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

        page_size = request.query_params.get('page_size', 5)
        self.pagination_class.page_size = page_size

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = paginator.get_paginated_response(serializer.data)
            response.data['total_pages'] = paginator.get_total_pages()
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def list_top_products(self, request):
        # List top 4 products

        sort_by = '-likes'
        queryset = self.filter_queryset(self.get_queryset()).order_by(sort_by)[:4]
        if queryset.count() == 0:
            return Response({'error': '상품이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)