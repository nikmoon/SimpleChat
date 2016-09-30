
$(document).ready(function(){

    "use strict"

    var waitMsgURL = '/tornado/waitmsg?lastid=';
    var lastMsgID;
    var msgDiv = $('#messages'),
        msgForm = $('#msgForm'),
        formActionURL = msgForm.attr('action'),
        msgText = $('#msgText');

    var waitTimeout = 0;
    var timeoutStep = 5000;

    msgForm.submit(function(event) {
        event.preventDefault();
        var msg = msgText.val()
        var xhr = new XMLHttpRequest();
        xhr.open('POST', formActionURL, true);
        xhr.onreadystatechange = function() {
            console.log('state: ' + this.readyState + '  status: ' + this.status);
            if (this.readyState != 4 || this.status == 0) return;
            if (this.status == 200) {
                //msgDiv.append('<p>' + 'yours' + ' ' + '<br />' + msg + '</p>');
                //msgDiv.scrollTop(msgDiv[0].scrollHeight);
            }
        }
        xhr.send(msg);
    })


    // получим последние 20 сообщений с сервера
    var xhr, msgData;

    xhr = new XMLHttpRequest();
    xhr.open('get', '/chat/last-messages', false);
    xhr.send();
    msgData = JSON.parse(xhr.responseText);
    lastMsgID = msgData.lastID;
    var messages = msgData.messages;
    for (var key in messages) {
        msgDiv.append('<p>' + messages[key].user + ' ' + key + '<br />' + messages[key].text + '</p>');
    }
    msgDiv.scrollTop(msgDiv[0].scrollHeight);

    function start_polling() {
        var xhr;

        function wait_new_messages() {
        
            xhr = new XMLHttpRequest();           
            xhr.onreadystatechange = function() {
                console.log('state: ' + this.readyState + '  status: ' + this.status);
                if (this.readyState != 4) return;

                if (this.status == 0) {
                    console.log('XHR wait messages error');
                    return;
                }

                if (this.status == 200) {
                    messages = JSON.parse(this.responseText);
                    messages.messages.forEach(function(msg, i, arr){
                        msgDiv.append('<p>' + msg.username + ' ' + msg.id + '<br />' + msg.text + '</p>');
                    })
                    msgDiv.scrollTop(msgDiv[0].scrollHeight);
                    lastMsgID = messages.lastID;

                    wait_new_messages();
                    return;
                }
                
                if (this.status == 504) {
                    wait_new_messages();
                }
 
            }
            xhr.error = function() {
                alert();
            }

            xhr.open('GET', waitMsgURL + lastMsgID, true);
            xhr.send();
        }

        wait_new_messages();

    }

    start_polling();
});

/*
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
*/
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
