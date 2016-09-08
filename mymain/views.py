from django.shortcuts import render
from django.http import HttpResponse
import django.contrib.auth as auth


# Create your views here.

def index(request):
    if request.user.is_authenticated():
        userList = [user.username for user in auth.models.User.objects.all()]
    else:
        userList = []
    return render(request, "mymain/index.html", {'userList': userList})
