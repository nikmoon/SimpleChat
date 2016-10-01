import tornado.ioloop
import tornado.web
from tornado.concurrent import Future
from tornado import gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPRequest
from tornado.queues import Queue
from comet_secret import AUTH_SECRET

import json

waiters = []

msgQueue = Queue(maxsize=10)
msgBuffer = []
msgLastID = 0


def get_sid(requestHandler):
    sid = requestHandler.get_cookie('sessionid')
    return sid


@gen.coroutine
def send_message():
    '''Ждем появления сообщения в очереди, затем рассылаем его всем ожидающим'''
    global waiters, msgLastID
    while 1:
        msg = yield msgQueue.get()
        msgBuffer.append(msg)
        print('Рассылаем сообщение: ' + str(msg))
        for waiter in waiters:
            if not waiter.done():
                waiter.set_result(msg)
            else:
                print('Пропускаем уже установленный future')
        waiters = []
        msgLastID = msg['id']
        msgQueue.task_done()


class WaitMessage(tornado.web.RequestHandler):
    '''
    Обработчик соединений клиентов, ожидающих получить новые сообщения чата
    Клиент передает свой в cookies свой 'sessionid', в теле сообщения ID последнего сообщения, которое у
    него есть
    '''
    @gen.coroutine
    def get(self):
        sid = get_sid(self)
        if not sid:
            self.set_status(403)
            self.write('Вы не авторизованы и не можете получать сообщения чата')
            return

        clientLastMsgID = int(self.get_argument('lastid'))
        if clientLastMsgID < msgLastID:
            print('Отправка клиенту предыдущих сообщений')
            newMsgList = msgBuffer[clientLastMsgID - msgLastID:]
            self.write(json.dumps({
                'count': len(newMsgList),
                'lastID': newMsgList[-1]['id'],
                'messages': newMsgList,
            }))
            return
        self.future = Future()
        waiters.append(self.future)
        self.waitID = len(waiters) - 1
        print('Добавился ожидающий {}, всего: {}'.format(self.waitID, len(waiters)))
        msg = yield self.future
        if not msg:
            print('Для waitID = {} пропускаем отправку сообщения = {}'.format(self.waitID, str(msg)))
            return
        print('Cообщение отправлено клиенту {} : {}'.format(self.waitID, str(msg)))
        self.write(json.dumps({
            'count': 1,
            'lastID': msg['id'],
            'messages': [msg]
        })
        )

    def on_connection_close(self):
        print('Connection closed by client')
        print('Устанавливаем результат future = None, waitID = {}'.format(self.waitID))
        self.future.set_result(None)


class SendMessage(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        try:
            msg = json.loads(self.request.body.decode('utf-8'))
            if msg['secret'] != AUTH_SECRET:
                print('Invalid secret')
                self.set_status(403)
                self.write('Вам запрещено пользоваться данным сервисом')
                return
            del msg['secret']
            yield msgQueue.put(msg)
            self.write('OK')
        except Exception:
            self.write('Исключительная ситуация при получении сообщения comet-сервером')


if __name__ == '__main__':
    app = tornado.web.Application([
        (r"/tornado/login", UserLogin),
        (r"/tornado/logout", UserLogout),
        (r"/tornado/sendmsg", SendMessage),
        (r"/tornado/waitmsg", WaitMessage),
    ])
    app.listen(8889)
    tornado.ioloop.IOLoop.current().add_callback(send_message)
    tornado.ioloop.IOLoop.current().start()
#    tornado.ioloop.IOLoop.current().run_sync(print_message)

