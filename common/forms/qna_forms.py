from django import forms
from ..models import QnA

class QnAForm(forms.ModelForm):
    class Meta:
        model = QnA
        fields = ['title', 'content', 'is_secret']