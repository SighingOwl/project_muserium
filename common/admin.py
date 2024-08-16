from django.contrib import admin
from .models import Review, QnA, Comment

admin.site.register(Review)
admin.site.register(QnA)
admin.site.register(Comment)