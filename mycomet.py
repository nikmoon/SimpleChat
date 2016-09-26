import tornado.ioloop
import tornado.web
from tornado.concurrent import Future
from tornado import gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPRequest
from tornado.queues import Queue
from comet_secret import AUTH_SECRET

import json

'''
    Словарь аутентифицированных в Django пользователей.
    При аутентификации пользователя, Django отправляет comet-серверу sessionid в теле запроса post. Comet-сервер, чтобы убедиться,
    что sessionid действительно существует, обращается к Django. В случае подтверждения запись добавляется в данный словарь.
    Аналогичная ситуация с завершением сессии.
    Формат записи: 'sessionid': [username, [...|], где ... - асинхронные запросы данного пользователя.
'''
authUsers = {}

waiters = []

msgQueue = Queue(maxsize=10)
msgBuffer = []
msgLastID = 0



import sys
from tornado.escape import json_decode
response = HTTPClient().fetch('http://127.0.0.1/chat/users-online')
data = json_decode(response.body)
for sid in data:
    authUsers[sid] = data[sid]
print(authUsers)



def get_sid(requestHandler):
    sid = requestHandler.get_cookie('sessionid')
    return sid if sid in authUsers else None



@gen.coroutine
def send_message():
    global waiters, msgLastID
    while 1:
        msg = yield msgQueue.get()
        print('Рассылаем сообщение: ' + msg['text'])
        for waiter in waiters:
            print('Отослали.')
            waiter.set_result(msg)
        waiters = []
        msgLastID = msg['id']
        msgBuffer.append(msg)
        msgQueue.task_done()


class UserLogin(tornado.web.RequestHandler):
    def post(self):
        result = 'FAILED'
        try:
            secret, sid, userName = self.request.body.decode('utf-8').split('\n', 2)
            if secret == AUTH_SECRET:
                authUsers[sid] = userName
                result = 'OK'
                print(authUsers)
        except Exception:
            pass
        print('Login: ' + result)
        self.write(result)



class UserLogout(tornado.web.RequestHandler):
    def post(self):
        result = 'FAILED'
        try:
            secret, sid, userName = self.request.body.decode('utf-8').split('\n', 2)
            if secret == AUTH_SECRET:
                del authUsers[sid]
                result = 'OK'
                print(authUsers)
        except Exception:
            pass
        print('Logout: ' + result)
        self.write(result)



class WaitMessage(tornado.web.RequestHandler):
    '''
    Обработчик соединений клиентов, ожидающих получить новые сообщения чата
    Клиент передает свой в cookies свой 'sessionid', в теле сообщения ID последнего сообщения, которое у
    него есть
    '''
    @gen.coroutine
    def get(self):
        sid = get_sid(self)
        if sid is not None:
            clientLastMsgID = int(self.get_argument('lastid'))
            if clientLastMsgID < msgLastID:
                # получаем и отправляем клиенту все сообщения, начиная с clientLastMsgID+1
                newMsgList = msgBuffer[clientLastMsgID - msgLastID:]
                self.write(json.dumps({
                    'count': len(newMsgList),
                    'lastID': newMsgList[-1]['id'],
                    'medssages': newMsgList,
                })
                )
                return
            waiters.append(Future())
            self.future = waiters[-1]
            msg = yield waiters[-1]
            self.write(json.dumps({
                'count': 1,
                'lastID': msg['id'],
                'messages': [msg]
            })
            )
        else:
            self.set_status(403)
            self.write('Этот ресурс Вам не доступен')



class MessageWait(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        sid = get_sid(self)
        if sid:
            print('Пришел запрос на ожидание сообщений, sid = ' + sid);
            future = Future()
            waiters.append(future)
            self.future = future
            msg = yield future
            self.write('{}\n{}'.format(*msg))
        else:
            self.write('FAILED')

    def on_connection_close(self):
        print('Соединение разорвано')
        waiters.remove(self.future)
        self.future.set_result([])


class SendMessage(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        try:
            msg = json.loads(self.request.body.decode('utf-8'))
            if msg['secret'] != AUTH_SECRET:
                print('Invalid secret')
                self.write('FAILED')
                return
            yield msgQueue.put({
                'id': msg['id'],
                'text': msg['text'],
                'username': authUsers[sid],
            })
            self.write('OK')
        except Exception:
            self.write('FAILED')


class MessageSender(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        result = 'FAILED'
        try:
            secret, sid, msgText, msgID = self.request.body.decode('utf-8').split('\n', 3)
            if secret == AUTH_SECRET:
                yield msgQueue.put({
                    'id': msgID,
                    'text': msgText,
                    'username': authUsers[sid]
                })
            result = 'OK'
        except Exception:
            pass
        self.write(result)

'''
    @gen.coroutine
    def save_message(self, msgText, sid):
        userName = authUsers[sid][0]
        result = yield AsyncHTTPClient('http://127.0.0.1:8888/chat/save-message').fetch(body=msgText, headers={'Cookie': 'sessionid={}'.format(sid)})
        print(result)
        return result
'''


if __name__ == '__main__':
    app = tornado.web.Application([
        (r"/tornado/login", UserLogin),
        (r"/tornado/logout", UserLogout),
        #(r"/tornado/sendmsg", MessageSender),
        #(r"/tornado/waitmsg", MessageWait),
        (r"/tornado/sendmsg", SendMessage),
        (r"/tornado/waitmsg", WaitMessage),
    ])
    app.listen(8889)
    tornado.ioloop.IOLoop.current().add_callback(send_message)
    tornado.ioloop.IOLoop.current().start()
#    tornado.ioloop.IOLoop.current().run_sync(print_message)

