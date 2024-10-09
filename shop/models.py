from django.db import models
from accounts.models import User

class Product(models.Model):
    class Meta:
        app_label = 'shop'

    # Product model
    title = models.CharField(max_length=127)
    short_description = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    discount_rate = models.IntegerField(default=0)
    image_url = models.URLField()
    image_alt = models.CharField(max_length=50)
    likes = models.IntegerField(default=0)
    reviews = models.IntegerField(default=0)
    total_rating = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    questions = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)
    purchased_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_products', null=True, blank=True)

    def __str__(self):
        return self.title