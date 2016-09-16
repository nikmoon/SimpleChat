from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms

import django.contrib.auth as auth
from django.core.urlresolvers import reverse

from tornado.httpclient import HTTPClient


# Create your views here.


def index(request):
    return redirect(mylogin, permanent=True)


class NameForm(forms.Form):
    f_username = forms.CharField(label="Имя", max_length=100)
    f_password = forms.CharField(label="Пароль", max_length=100, widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    userName = forms.CharField(50, label='Имя')
    userPassw1 = forms.CharField(50, label='Пароль', widget=forms.PasswordInput)
    userPassw2 = forms.CharField(50, label='Повтор пароля', widget=forms.PasswordInput)

    def clean(self):
        super(RegistrationForm, self).clean()
        if self.errors:
            return

        userName = self.cleaned_data['userName']
        userPassw1 = self.cleaned_data['userPassw1']
        userPassw2 = self.cleaned_data['userPassw2']
        if userPassw1 == userPassw2:
            try:
                self.user = auth.models.User.objects.create_user(userName, password=userPassw1)
            except Exception:
                raise forms.ValidationError('Пользователь с таким именем уже существует. Пожалуйста, выберите другое имя')
        else:
            self.add_error('userPassw1', forms.ValidationError('Пароли не совпадают'))



def say_to_tornado(request):
    HTTPClient().fetch('http://127.0.0.1:8889/tornado/auth/login', method='POST', body=request.session.session_key)


def mylogin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(request.GET.get("next", "/"))
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['f_username'], password=form.cleaned_data['f_password'])
            if user is not None:
                auth.login(request, user)
                say_to_tornado(request)
                return HttpResponseRedirect(request.POST.get("next", "/"))
    else:
        form = NameForm()
    return render(request, 'myauth/login.html', {'form': form})


def mylogout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def reg_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse(mylogin))
    else:
        form = RegistrationForm()
    return render(request, 'myauth/register.html', {'form': form})

