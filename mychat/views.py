from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.contrib.auth import authenticate, login, logout

# Create your views here.


def index(request):
    return redirect(mylogin, permanent=True)



class NameForm(forms.Form):
    f_username = forms.CharField(label="Имя: ", max_length=100)
    f_password = forms.CharField(label="Пароль: ", max_length=100, widget=forms.PasswordInput)


def mylogin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(request.GET.get("next", "/"))
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['f_username'], password=form.cleaned_data['f_password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(request.POST.get("next", "/"))
    else:
        form = NameForm()
    return render(request, 'myauth/login.html', {'form': form})


def mylogout(request):
    logout(request)
    return HttpResponseRedirect("/")
