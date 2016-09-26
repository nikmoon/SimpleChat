from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth


# Create your views here.


def index(request):
    if request.user.is_authenticated():
        userList = [user.username for user in auth.models.User.objects.all()]
    else:
        userList = []
    return render(request, "mainpage/index.html", {'userList': userList})
