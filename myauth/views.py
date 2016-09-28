from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib import auth

from tornado.httpclient import HTTPClient
from comet_secret import AUTH_SECRET

from . import forms


# Create your views here.


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        return redirect(login_view)

'''
def say_to_tornado(request, action):
    actionUrl = 'http://127.0.0.1:8889/tornado' + action
    result = HTTPClient().fetch(actionUrl, method='POST', body='{}\n{}\n{}'.format(AUTH_SECRET, request.session.session_key, request.user.username))
'''


def login_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        form = forms.LoginForm()
    elif request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            logName = form.cleaned_data['logName']
            logPassword = form.cleaned_data['logPassword']
            user = auth.authenticate(username=logName, password=logPassword)
            if user is not None:
                auth.login(request, user)
                #say_to_tornado(request, '/login')
                return HttpResponseRedirect(request.POST.get('next', '/'))
    else:
        return HttpResponseNotAllowed(['GET', 'POST'], 'Недопустимый метод')

    return render(request, 'myauth/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated():
        #say_to_tornado(request, '/logout')
        auth.logout(request)
    return HttpResponseRedirect("/")


def registration_view(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse(login_view))
    else:
        form = forms.RegistrationForm()
    return render(request, 'myauth/registration.html', {'form': form})


def info_view(request):
    if request.user.is_authenticated():
        return JsonResponse({
            'username': request.user.username,
            'sid': request.session.session_key,
        })
    else:
        raise PermissionDenied()
