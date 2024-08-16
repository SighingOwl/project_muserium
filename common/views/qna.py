import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import QnA
from glass_class.models import GlassClass
from ..forms import QnAForm

# Glass class QnA
#@login_required(login_url='#')
@require_POST
@csrf_protect
def create_class_qna(request, glass_class_id):
    # Create a QnA
    
    pass

def read_class_qna(request, glass_class_id):
    # Read a QnA
    pass

#@login_required(login_url='#')
@require_POST
@csrf_protect
def update_class_qna(request, glass_class_id):
    # update a QnA
    pass

#@login_required(login_url='#')
@csrf_protect
def delete_class_qna(request, glass_class_id):
    # Delete a QnA
    pass