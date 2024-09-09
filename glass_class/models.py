from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class GlassClass(models.Model):
    # Glass Class model
    title = models.CharField(max_length=127)
    teacher = models.CharField(max_length=50, default='이소정')
    category = models.CharField(max_length=50, default='One Day Class')
    description = models.TextField()
    short_description = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    discount_rate = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    image_url = models.URLField()
    image_alt = models.CharField(max_length=50)
    likes = models.IntegerField(default=0)
    reviews = models.IntegerField(default=0)
    total_rating = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    questions = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)

class Reservation(models.Model):
    # Class Reservation model
    STAUTS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    glass_class = models.ForeignKey(GlassClass, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    created_at = models.DateTimeField()
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f'{self.user.username} - {self.glass_class.title} on {self.reservation_date} at {self.reservation_time}'