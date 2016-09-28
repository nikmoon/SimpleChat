
$(document).ready(function(){

    "use strict"

    var waitMsgURL = '/tornado/waitmsg';
    var lastMsgID, msgDiv;

    msgDiv = $('#messages');

    var waitTimeout = 0;
    var timeoutStep = 5000;

    $('#msgForm').submit(function(event) {
        event.preventDefault();

        var form = $(this)
        var msgText = $('#msgText').val();
        var url = form.attr('action');

        var xhr = new XMLHttpRequest();
        xhr.open('post', url, true);
        xhr.onreadystatechange = function() {
            if (this.readyState != 4 || this.status == 0) return;
            if (this.status == 200) {
                msgDiv.append('<p>' + 'yours' + ' ' + '<br />' + msgText + '</p>');
                msgDiv.scrollTop(msgDiv[0].scrollHeight);
            }
        }
        xhr.send(msgText);
    })


    // получим последние 20 сообщений с сервера
    var xhr, messages;

    xhr = new XMLHttpRequest();
    xhr.open('get', '/chat/last-messages', false);
    xhr.send();
    messages = JSON.parse(xhr.responseText);
    lastMsgID = messages.lastID;
//  messages.messages.forEach(function(msg, i, arr){
//      msgDiv.append('<p>' + msg.username + ' ' + msg.id + '<br />' + msg.text + '</p>');
//  })
    var msg = messages.messages;
    for (var key in msg) {
        msgDiv.append('<p>' + msg[key].user + ' ' + key + '<br />' + msg[key].text + '</p>');
    }
    msgDiv.scrollTop(msgDiv[0].scrollHeight);

    return;

    function subscribe() {
        var xhr = new XMLHttpRequest();
        xhr.timeout = 10000;
        xhr.ontimeout = function() {
            console.log('Закрываем соединение по таймауту');
            subscribe();
        }
        xhr.onreadystatechange = function() {
            var messages;
            console.log('readyState: ' + this.readyState + '  status: ' + this.status + ' statusText: ' + this.statusText);
            if (this.readyState != 4 || this.status == 0) return;

            if (this.status == 500) {
                if (waitTimeout < 15000) {
                    waitTimeout += timeoutStep;
                }
                console.log('wait for ' + waitTimeout.toString());
                setTimeout(subscribe, waitTimeout);
                return;
            }

            if (this.status == 200) {
                waitTimeout = 0;
                messages = JSON.parse(this.responseText);
                lastMsgID = messages.lastID;
                messages.messages.forEach(function(msg, i, arr){
                    msgDiv.append('<p>' + msg.username + ' ' + msg.id + '<br />' + msg.text + '</p>');
                })
                msgDiv.scrollTop(msgDiv[0].scrollHeight);
            }
            subscribe();
        }
        xhr.open('GET', waitMsgURL + '?lastid=' + lastMsgID, true);
        xhr.send();
    }

    subscribe();

});

/*
var myModule = (function() {

    var xhr = new XMLHttpRequest();

    xhr.open("post", "/chat/new-message", false);
//  xhr.send('Примите новое сообщение');
    if (xhr.responseText) {
//      alert(xhr.responseText);
    }
    else {
//      alert('Пустой ответ');
    }

    return {};

})();

alert($);
*/

//alert(xhr.getAllResponseHeaders());
