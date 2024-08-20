from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from ..models import GlassClass
from ..serializers import ClassDetailSerializer

class ClassViewSets(viewsets.ModelViewSet):
    queryset = GlassClass.objects.all()
    serializer_class = ClassDetailSerializer

    @action(detail=False, methods=['get'])
    def get_class_detail(self, request):
        # Get the detail of a specific class

        pk = request.query_params.get('id', None)

        selected_class = GlassClass.objects.get(pk=pk)
        serializer = self.get_serializer(selected_class)
        return Response(serializer.data)