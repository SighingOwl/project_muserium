from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GlassClass, Reservation
from .serializers import ClassSerializer, ReservationSerializer
from datetime import datetime, timedelta

class ClassListView(APIView):
    # List all classes
    def get(self, request):
        glass_class = GlassClass.objects.all()
        serializer = ClassSerializer(glass_class, many=True)
        return Response(serializer.data)

class ClassDetailView(APIView):
    # Retrieve a class
    def get(self, request, key):
        try:
            selected_class = GlassClass.objects.get(title=key)
        except GlassClass.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        class_serializer = ClassSerializer(selected_class)

        return Response(class_serializer.data)

class ClassReservationView(APIView):
    # List all reservations for a specific class
    def get(self, request, key):
        try:
            selected_class = GlassClass.objects.get(title=key)
        except GlassClass.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Calculate the date range to limit the dates of resservations to search
        today = datetime.today().date()
        last_day = today + timedelta(days = 30)

        reservations = Reservation.objects.filter(
            glass_class=selected_class,
            reservation_date__range=(today, last_day)
        )
        if not reservations.exists():
            return Response([])
        
        reservation_serializer = ReservationSerializer(reservations, many=True)
        return Response(reservation_serializer.data)