from django import forms
from django.core.exceptions import ValidationError
from ..models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'image', 'rating', 'teacher_rating', 'readiness_rating', 'content_rating']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None or rating <= 0 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5')
        return rating

    def clean_teacher_rating(self):
        teacher_rating = self.cleaned_data.get('teacher_rating')
        if teacher_rating is None or teacher_rating <= 0 or teacher_rating > 3:
            raise forms.ValidationError('Teacher rating must be between 1 and 3')
        return teacher_rating

    def clean_readiness_rating(self):
        readiness_rating = self.cleaned_data.get('readiness_rating')
        if readiness_rating is None or readiness_rating <= 0 or readiness_rating > 3:
            raise forms.ValidationError('Readiness rating must be between 1 and 3')
        return readiness_rating

    def clean_content_rating(self):
        content_rating = self.cleaned_data.get('content_rating')
        if content_rating is None or content_rating <= 0 or content_rating > 3:
            raise forms.ValidationError('Content rating must be between 1 and 3')
        return content_rating