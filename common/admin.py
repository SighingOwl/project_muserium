from django.contrib import admin
from .models import Like, DetailInfo,Review, Question, Answer, Comment

admin.site.register(Like)
admin.site.register(DetailInfo)
admin.site.register(Review)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Comment)