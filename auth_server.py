'''


 НА ДАННЫЙ МОМЕНТ НЕ ИСПОЛЬЗУЕТСЯ



'''
import os
import socket
import json
import struct

socketFile = '/tmp/mysite-auth-server.sock'
packetLenField = len(struct.pack('<L', 0))


def client_socket():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socketFile)
    return sock


def send_message(msg, sock):
    data = msg.encode('utf-8')
    dataLen = struct.pack('<L', len(data))
    sock.send(dataLen + data)


def get_message(sock):
    msgLen = sock.recv(packetLenField)
    if not msgLen:
        return ''
    msgLen = struct.unpack('<L', msgLen)[0]
    msg = sock.recv(msgLen)
    if msg: msg = msg.decode('utf-8')
    return msg


def set_user(username, sid, _sock=None):
    sock = _sock if _sock is not None else client_socket()
    data = {'action': 'SET', 'name': username, 'sid': sid}
    msg = json.dumps(data)
    send_message(msg, sock)
    response = get_message(sock)
    if _sock is None:
        sock.close()
    return response


def start_server():
    if os.path.exists(socketFile):
        os.remove(socketFile)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socketFile)
    server.listen(2)

    while 1:
        conn, addr = server.accept()
        
        while 1:
            data = get_message(conn)
            if not data: break
            msg = json.loads(data)
        
            if msg['action'] == 'SET':
                prevSid = ''
                username = msg['name']
                sid = msg['sid']
                if username in users:
                    prevSid = users[username]
                    del sids[prevSid]
                users[username] = sid
                sids[sid] = username
                send_message(prevSid, conn)
            elif msg['action'] == 'GET':
                if 'name' in msg:
                    send_message(users[msg['name']], conn)
                elif 'sid' in msg:
                    send_message(sids[msg['sid']], conn)
        conn.close()
    server.close()


if __name__ == '__main__':
    users = {}
    sids  = {}
    start_server()
