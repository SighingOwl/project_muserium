from django import forms
from django.core.exceptions import ValidationError
from ..models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'image', 'rating', 'sub_rating_1', 'sub_rating_2', 'sub_rating_3']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None or rating <= 0 or rating > 5:
            raise forms.ValidationError('평점은 1점 이상 5점 이하로 입력해주세요.')
        return rating

    def clean_sub_rating(self):
        sub_rating_1 = self.cleaned_data.get('sub_rating_1')
        sub_rating_2 = self.cleaned_data.get('sub_rating_2')
        sub_rating_3 = self.cleaned_data.get('sub_rating_3')

        if sub_rating_1 is None or sub_rating_1 <= 0 or sub_rating_1 > 3 or \
            sub_rating_2 is None or sub_rating_2 <= 0 or sub_rating_2 > 3 or \
            sub_rating_3 is None or sub_rating_3 <= 0 or sub_rating_3 > 3:
            raise forms.ValidationError('평점이 최대 3점인 항목은 1점 이상 3점 이하로 입력해주세요.')
