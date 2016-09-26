from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import django.contrib.auth as auth
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

from mychat.models import ChatMessage

from tornado.httpclient import HTTPClient
from comet_secret import AUTH_SECRET
import json

# Create your views here.


def valid_request(user):
    return user.is_authenticated()

def index(request):
    return render(request, 'mychat/index.html', 
        {
            'userList': auth.models.User.objects.all(),
            'messages': ChatMessage.objects.order_by('id')[:20],
        }
    )


@csrf_exempt
def new_message(request):
    if valid_request(request.user) and request.method == 'POST':
        msgText = request.POST['edit-window']
        message = ChatMessage.objects.create(msgText=msgText, msgAuthor=request.user)
        response = json.dumps({'secret': AUTH_SECRET, 'id': message.id, 'text': msgText, 'username': request.user.username})
        result = HTTPClient().fetch('http://127.0.0.1:8889/tornado/sendmsg',
            method='POST',
            body=response
        )
        return HttpResponseRedirect('/chat/')
    else:
        return HttpResponseRedirect('/chat/')




def last_messages(request):
    '''
        Возвращается 20 последних сообщений в формате:
        число сообщений\n
        сообщение1,автор\n
        сообщение2,автор\n
        ...
        сообщениеN,автор\n
        ID последнего сообщения

        Данный URL должен вызываться при первой загрузке или обновлении главной страницы чата.
    '''
    if valid_request(request.user):
        messages = ChatMessage.objects.order_by('-id')[:20]
        return JsonResponse({
            'count': len(messages),
            'lastID': messages.first().id,
            'messages': list(reversed([ {'id': msg.id, 'username': msg.msgAuthor.username, 'text': msg.msgText} for msg in messages]))
        })
    else:
        return HttpResponse('FAIL') 


def users_online(request):
    sessions = Session.objects.all()
    data = {}
    for session in sessions:
        decoded = session.get_decoded()
        uid = decoded['_auth_user_id']
        sid = session.session_key
        username = User.objects.filter(id=uid)[0].username
        data[sid] = username
    return JsonResponse(data)



def test_template(request):
    return render(request, 'mychat/index.html')
