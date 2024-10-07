from django import forms
from ..models import DetailInfo

class DetailInfoForm(forms.ModelForm):
    class Meta:
        model = DetailInfo
        fields = ['title', 'description_1', 'description_2', 'description_3', 'product_image', 'notice_image', 'event_image', 'glass_class', 'product']

    def __init__(self, *arg, **kwargs):
        super(DetailInfoForm, self).__init__(*arg, **kwargs)
        self.fields['product'].required = True if not self.instance.glass_class else False
        


    