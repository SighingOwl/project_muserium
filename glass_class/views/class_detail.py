from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from glass_class.models import GlassClass
from glass_class.serializers import ClassDetailSerializer

class ClassViewSets(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = GlassClass.objects.all()
    serializer_class = ClassDetailSerializer

    @action(detail=False, methods=['get'])
    def get_class_detail(self, request):
        # Get the detail of a specific class

        pk = request.query_params.get('id', None)

        selected_class = get_object_or_404(GlassClass, pk=pk)
        serializer = self.get_serializer(selected_class)
        return Response(serializer.data)