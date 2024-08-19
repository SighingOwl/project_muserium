from django.contrib import admin
from .models import Review, Question, Answer, Comment

admin.site.register(Review)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Comment)