from django.shortcuts import render
from .models import Image
from .forms import ImageForm

def upload_image(request):
    if request.method() == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'upload_image.html', {'form': form})