import tornado.ioloop
import tornado.web
from tornado.concurrent import Future
from tornado import gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPRequest
from tornado.queues import Queue


'''
    Словарь аутентифицированных в Django пользователей.
    При аутентификации пользователя, Django отправляет comet-серверу sessionid в теле запроса post. Comet-сервер, чтобы убедиться,
    что sessionid действительно существует, обращается к Django. В случае подтверждения запись добавляется в данный словарь.
    Аналогичная ситуация с завершением сессии.
    Формат записи: 'sessionid': [username, [...|], где ... - асинхронные запросы данного пользователя.
'''
authUsers = {}


waiters = []
last_id = 0



'''
@gen.coroutine
def user_authenticated(headers):
    response = yield AsyncHTTPClient().fetch(
        'http://127.0.0.1:8888/chat/check',
        headers={'Cookie': headers['Cookie']}
    )
    return response.body == b'OK'
'''
def is_authenticated(requestHandler):
    django_sid = requestHandler.get_cookie('sessionid')
    return django_sid in authUsers


def get_django_user(django_response):
    body = django_response.result().body
    if body != b"UNKNOWN":
        '''
        Проверка аутентификации прошла успешно
        '''
        username, django_sid = body.decode('utf-8').split('\n')
        authUsers[django_sid] = [username, []]


class UserLogin(tornado.web.RequestHandler):
    def post(self):
        django_sid = self.request.body
        future = AsyncHTTPClient().fetch('http://127.0.0.1:8888/chat/check-user', headers={'Cookie': b'sessionid=' + django_sid})
        tornado.ioloop.IOLoop.current().add_future(future, get_django_user)
        self.write(django_sid)



class UserLogout(tornado.web.RequestHandler):
    def post(self):
        body = self.request.body
        self.write(body)
        


class MessageSender(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self):
        if not is_authenticated(self):
            self.write('Пошел вон отсюда!')
            return
        try:
            user_last_id = int(self.request.body)
        except Exception:
            self.write('Чо за херню ты мне тут передаешь? Я ожидаю ID последнего сообщения, которое ты получил.')
            return
        if user_last_id >= last_id:
            self.messages = Future()
            waiters.append(self.messages)
            result = yield self.messages
            self.write(result)
        else:
            pass
        self.write('Здесь должны быть новые сообщения')
        


class MessageReceiver(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        global waiters, last_id
        if not is_authenticated(self):
            self.write('Пошел вон отсюда')
            return
        for waiter in waiters:
            waiter.set_result(self.request.body)
        waiters = []
        self.write('OK')


if __name__ == '__main__':
    app = tornado.web.Application([
        (r"/tornado/auth/login", UserLogin),
        (r"/tornado/auth/logout", UserLogout),
        (r"/tornado/sendmsg", MessageReceiver),
        (r"/tornado/getmsg", MessageSender),
    ])
    app.listen(8889)
    tornado.ioloop.IOLoop.current().start()
#    tornado.ioloop.IOLoop.current().run_sync(print_message)

