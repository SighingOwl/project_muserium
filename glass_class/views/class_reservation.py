from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from ..models import GlassClass, Reservation
from ..serializers import ReservationSerializer
from datetime import datetime, timedelta
from collections import Counter

class DateConfig:
    def __init__(self):
        self.start_date = datetime.now() + timedelta(hours=9)
        self.end_30 = [4, 6, 9, 11]
        self.end_31 = [1, 3, 5, 7, 8, 10, 12]
        if self.start_date.month in self.end_30:
            self.end_date = self.start_date + timedelta(days=30)
        elif self.start_date.month in self.end_31:
            self.end_date = self.start_date + timedelta(days=31)
        else:
            year = self.start_date.year
            if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
                self.end_date = self.start_date + timedelta(days=29)
            else:
                self.end_date = self.start_date + timedelta(days=28)
        self.vaild_times = ['10:00:00', '12:00:00', '14:00:00', '16:00:00']

    def get_disabled_dates(self, reservations):
        reservation_dates = [reservation.reservation_date for reservation in reservations]
        reservation_count = Counter(reservation_dates)

        disabled_dates = [date for date, count in reservation_count.items() if count == 4]

        # Add dates that are Mondey
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() == 0:
                disabled_dates.append(current_date)
            current_date += timedelta(days=1)

        return disabled_dates

    def get_end_date(self):
        return self.end_date

    def get_start_date(self):
        return self.start_date

class ClassReservationViewSets(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    '''
    로그인 기능 추가 후 수정 필요
    '''
    #@login_required(login_url='#')
    @action(detail=False, methods=['post'])
    @csrf_protect
    @transaction.atomic
    def create_reservation(self, request):
        # Create a reservation

        class_id = request.data.get('class_id', None)
        reservation_date = request.data.get('reservation_date', None)
        reservation_time = request.data.get('reservation_time', None)
        if not class_id:
            return Response({'error': 'class_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not reservation_date:
            return Response({'error': 'reservation_date is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not reservation_time:
            return Response({'error': 'reservation_time is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        date_config = DateConfig()
        disabled_dates = date_config.get_disabled_dates(Reservation.objects.all())
        valid_times = date_config.vaild_times
        disabled_times = [reservation.reservation_time for reservation in Reservation.objects.filter(reservation_date=reservation_date)]
        
        if reservation_date in disabled_dates:
            return Response({'error': 'This date is not available for reservation'}, status=status.HTTP_400_BAD_REQUEST)
        if reservation_time not in valid_times or reservation_time in disabled_times:
            return Response({'error': 'This time is not available for reservation'}, status=status.HTTP_400_BAD_REQUEST)

        glass_class = GlassClass.objects.get(id=class_id)
        reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d')

        # Check if the user has already made a reservation
        # 유저별로 예약을 관리하는 모델이 필요... if Reservation.objects.filter(glass_class=glass_class, user = request.user, reservation_date=reservation_date).exists():
        #     return Response({'error': 'You have already made a reservation for this class'}, status=status.HTTP_400_BAD_REQUEST)

    
    @action(detail=False, methods=['get'])
    def list_reservations(self, request):
        # List all reservations for a specific class

        class_id = request.query_params.get('class_id', None)
        if not class_id:
            return Response({'error': 'class_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        glass_class = GlassClass.objects.get(id=class_id)
        
        date_config = DateConfig()
        start_date = date_config.get_start_date()
        end_date = date_config.get_end_date()

        reservations = Reservation.objects.filter(
            glass_class=glass_class,
            reservation_date__range=[start_date, end_date]
        )
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'])
    def get_disabled_dates(self, request):
        # Get disabled dates for all reservations
        
        date_config = DateConfig()
        start_date = date_config.get_start_date()
        end_date = date_config.get_end_date()

        reservations = Reservation.objects.filter(
            reservation_date__range=[start_date, end_date]
        )

        disabled_dates = date_config.get_disabled_dates(reservations)

        return Response(disabled_dates)

    @action(detail=False, methods=['get'])
    def get_disabled_timezones(self, request):
        # Get disabled timezones for all reservations

        selected_date = request.query_params.get('selected_date', None)
        if not selected_date:
            return Response({'error': 'selected_date is required'}, status=status.HTTP_400_BAD_REQUEST)

        date_config = DateConfig()
        now = date_config.get_start_date()
        vaild_times = date_config.vaild_times
        threshold_time = now + timedelta(hours=1, minutes=30)

        print(threshold_time)
        
        disabled_timezones = [reservation.reservation_time for reservation in Reservation.objects.filter(reservation_date=selected_date)]
        for time in vaild_times:
            if threshold_time.strftime('%H:%M:%S') > time and time not in disabled_timezones:
                disabled_timezones.append(time)
        
        return Response(disabled_timezones)