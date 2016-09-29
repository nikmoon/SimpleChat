from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed
from django.http import HttpResponseServerError
from django.contrib import auth
from django.core.exceptions import PermissionDenied

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

from mychat.models import ChatMessage

from tornado.httpclient import HTTPClient
from comet_secret import AUTH_SECRET
import json

# Create your views here.


@login_required
def index(request):
    return render(request, 'mychat/index.html', 
#        {
#            'userList': User.objects.all(),
#        }
    )


@csrf_exempt
def new_message(request):
    if not request.user.is_authenticated():
        raise PermissionDenied()

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Недопустимый метод')

    msg = request.body.decode('utf-8')
    username = request.user.username

    newMessage = ChatMessage.objects.create(msgText=msg, msgAuthor=request.user)

    cometMsg = json.dumps({'secret': AUTH_SECRET, 'id': newMessage.id, 'text': msg, 'username': username})
    try:
        cometResponse = HTTPClient().fetch('http://127.0.0.1/tornado/sendmsg', method='POST', body=cometMsg)
        return HttpResponse(cometResponse.body)
    except Exception:
        print('Исключительная ситуация')
        return HttpResponseServerError('Нет ответа от comet-сервера')


def last_messages(request):
    '''
    20 последних сообщений из базы.
    '''
    if not request.user.is_authenticated():
        raise PermissionDenied()
    
    messages = list(ChatMessage.objects.order_by('id'))[-20:]
    return JsonResponse({
        'count': len(messages),
        'lastID': messages[-1].id,
        'messages': { msg.id: {'text': msg.msgText, 'user': msg.msgAuthor.username} for msg in messages },
    })


def users_logged(request):
#    secret = request.body.decode('utf-8')
#    if secret != AUTH_SECRET:
#        raise PermissionDenied
    data = {}
    for session in Session.objects.all():
        uid = session.get_decoded()['_auth_user_id']
        username = User.objects.filter(id=uid)[0].username
        data[session.session_key] = username
    return JsonResponse(data)



def test_template(request):
    return render(request, 'mychat/index.html')
