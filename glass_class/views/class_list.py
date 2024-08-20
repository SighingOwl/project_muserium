from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from ..models import GlassClass
from ..serializers import ClassSerializer

class PaginationConfig(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_total_pages(self):
        if self.page.paginator.count == 0 or self.page_size == 0:
            return 0
        page_size = int(self.page_size)
        return (self.page.paginator.count + page_size - 1) // page_size

class ClassListViewSets(viewsets.ModelViewSet):
    queryset = GlassClass.objects.all()
    serializer_class = ClassSerializer
    pagination_class = PaginationConfig

    @action(detail=False, methods=['get'])
    def list_classes(self, request):
        # List all classes with sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        queryset = self.filter_queryset(self.get_queryset()).order_by(sort_by)

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
    def list_top_classes(self, request):
        # List top 4 classes

        sort_by = '-likes'
        queryset = self.filter_queryset(self.get_queryset()).order_by(sort_by)[:4]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)