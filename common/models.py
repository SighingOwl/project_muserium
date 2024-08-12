from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from glass_class.models import GlassClass

class Image(models.Model):
    # Image model
    title = models.CharField(max_length=127)
    image = models.ImageField(upload_to='images/')

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class ContentModel(TimeStampedModel):
    title = models.CharField(max_length=127)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        abstract = True

class Review(models.Model):
    # Review model

    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    glass_class = models.ForeignKey(GlassClass, on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        super.clean()
        if self.rating < 0 or self.rating > 5:
            raise ValidationError('Rating must be between 0 and 5')

class QnA(models.Model):
    # QnA model

    is_secret = models.BooleanField(default=False)
    glass_class = models.ForeignKey(GlassClass, on_delete=models.CASCADE, null=True, blank=True)

class Comment(models.Model):
    # Comment model

    title = models.CharField(max_length=127)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    