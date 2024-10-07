import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Comment
from glass_class.models import GlassClass
from ..forms import CommentForm

# Glass class Comment
#@login_required(login_url='#')
@require_POST
@csrf_protect
def create_class_comment(request):
    # Create a comment
    pass


def read_class_comment(request):
    # Read a comment
    pass

#@login_required(login_url='#')
@require_POST
@csrf_protect
def update_class_comment(request):
    # update a comment
    pass

#@login_required(login_url='#')
@csrf_protect
def delete_class_comment(request):
    # Delete a comment

    pass