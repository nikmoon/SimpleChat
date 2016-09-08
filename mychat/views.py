from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.contrib.auth import authenticate, login, logout
import django.contrib.auth as auth

# Create your views here.


def index(request):
    return render(request, 'mychat/index.html', {'userList': auth.models.User.objects.all()})


