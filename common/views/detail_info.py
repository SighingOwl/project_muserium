from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from ..models import GlassClass, DetailInfo
from ..serializers import DetailInfoSerializer

class ClassDetailInfoViewSets(viewsets.ViewSet):
    # Class detail info view sets
    queryset = DetailInfo.objects.all()

    @action(detail=False, methods=['get'])
    def get_detail_info(self, request):
        # Get detail info
        class_id = request.query_params.get('class_id')
        if class_id is None:
            return Response({'error': 'class_id가 필요합니다.'}, status=400)

        glass_class = GlassClass.objects.get(id=class_id)
        detail_info = DetailInfo.objects.filter(glass_class=glass_class)

        serializer = DetailInfoSerializer(detail_info, many=True)
        return Response(serializer.data, status=200)

        