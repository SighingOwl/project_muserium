from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from glass_class.models import GlassClass
from shop.models import Product
from accounts.models import User

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class ContentModel(TimeStampedModel):
    # Content model

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    image = models.URLField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True

class DetailInfo(TimeStampedModel):
    # Detail info model

    title = models.CharField(max_length=100, blank=True, null=True)
    description_1 = models.TextField(blank=True, null=True)
    description_2 = models.TextField(blank=True, null=True)
    description_3 = models.TextField(blank=True, null=True)
    product_image = models.URLField(max_length=255, blank=True, null=True)
    notice_image = models.URLField(max_length=255, blank=True, null=True)
    event_image = models.URLField(max_length=255, blank=True, null=True)
    glass_class = models.ForeignKey(GlassClass, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.description_1[:50]

class Like(TimeStampedModel):
    # Like model

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    glass_class = models.ForeignKey(GlassClass, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'glass_class')

class Review(ContentModel):
    # Review model

    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    '''
    sub_rating_1: teacher rating or product quality rating
    sub_rating_2: readiness rating or product design rating
    sub_rating_3: content rating or product price rating
    '''
    sub_rating_1 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], default=1)
    sub_rating_2 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], default=1)
    sub_rating_3 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], default=1)
    glass_class = models.ForeignKey(GlassClass, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)

class Question(ContentModel):
    # QnA model

    title = models.CharField(max_length=100)
    is_secret = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    answered_at = models.DateTimeField(null=True, blank=True)
    glass_class = models.ForeignKey(GlassClass, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)

class Answer(ContentModel):
    # Answer model

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Comment(ContentModel):
    # Comment model

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    