from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.contrib.auth import authenticate, login, logout
import django.contrib.auth as auth

from mychat.models import ChatMessage

# Create your views here.


def can_send(user, method):
    return user.is_authenticated() and method == "GET"

def index(request):
    return render(request, 'mychat/index.html', {'userList': auth.models.User.objects.all()})


def save_message(request):
    if can_send(request.user, request.method):
        msgText = request.body
        print('Пришло сообщение:')
        print('    Текст: {}'.format(msgText))
        print('    Отправитель: {}'.format(request.user))
        message = ChatMessage.objects.create(msgText=msgText, msgAuthor=request.user)
        return HttpResponse('OK, {}'.format(mesage.id))
    else:
        return HttpResponse("FAIL")


def check_user(request):
    if not request.user.is_authenticated():
        result = HttpResponse('UNKNOWN')
    else:
        username = request.user.username
        session_key = request.session.session_key
        result = HttpResponse(username + '\n' + session_key)
    return result


def last_messages(request):
    '''
        Возвращается строка в формате:
        число сообщений
        сообщение1
        сообщение2
        ...
        сообщениеN
        ID последнего сообщения

        Данный URL должен вызываться при первой загрузке или обновлении главной страницы чата.
        Возвращает не более 20 последних сообщений.
    '''
    if can_send(request.user, request.method):
        messages = ['{}, {}'.format(msg.msgText, msg.msgAuthor) for msg in ChatMessage.objects.order_by('id')[:20]]
        messages = str(len(messages)) + '\n' + '\n'.join(messages) + '\n' + str(ChatMessage.objects.last().id)
        return HttpResponse(messages)
    else:
        return HttpResponse('FAIL') 
