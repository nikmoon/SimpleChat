
$(document).ready(function(){

    "use strict"

    var waitMsgURL = '/tornado/waitmsg?lastid=',
        lasMsgURL = '/chat/last-messages',
        lastMsgID,
        msgDiv = $('#messages'),
        msgForm = $('#msgForm'),
        formActionURL = msgForm.attr('action'),
        msgText = $('#msgText');


    // Отправка сообщений нажатием на кнопку
    msgForm.submit(function(event) {
        event.preventDefault();
        var msg = msgText.val()
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            console.log('state: ' + this.readyState + '  status: ' + this.status);
            //if (this.readyState != 4 || this.status == 0) return;
            //if (this.status == 200) {
                //msgDiv.append('<p>' + 'yours' + ' ' + '<br />' + msg + '</p>');
                //msgDiv.scrollTop(msgDiv[0].scrollHeight);
            //}
        }
        xhr.open('POST', formActionURL, true);
        xhr.send(msg);
    })


    // 20 последних сообщений с сервера
    var xhr = new XMLHttpRequest(),
        msgData, messages;
    xhr.onreadystatechange = function() {
        console.log('state: ' + this.readyState + '  status: ' + this.status);
        if (this.readyState == 4 && this.status == 200) {
            console.log('Последние сообщения с сервера получены');
            msgData = JSON.parse(this.responseText);
            lastMsgID = msgData.lastID;
            messages = msgData.messages;
            for (var key in messages) {
                msgDiv.append('<p>' + messages[key].user + ' ' + key + '<br />' + messages[key].text + '</p>');
            }
            msgDiv.scrollTop(msgDiv[0].scrollHeight);

            // Можно приступать к long polling
            start_polling();
        }
    }
    xhr.open('get', '/chat/last-messages', true);
    xhr.send();


    function start_polling() {
        var xhr,
            startRequest, endRequest, reqTime,
            reqErrorTimeout = 5000;

        function wait_new_messages() {
        
            xhr = new XMLHttpRequest();           
            
            xhr.onreadystatechange = function() {
                //var xhrInfo = 'state: ' + this.readyState + '  status: ' + this.status;
                //console.log(xhrInfo);
                //msgDiv.append(xhrInfo + '<br />');
                //msgDiv.scrollTop(msgDiv[0].scrollHeight);
                
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

                }
                else {
                    endRequest = new Date();
                    reqTime = endRequest - startRequest;
                    console.log('Сюда попали, прошло: ' + reqTime);
                    if (reqTime < reqErrorTimeout) {
                        setTimeout(wait_new_messages, reqErrorTimeout - reqTime + 1000);
                    }
                    else {
                        wait_new_messages();
                    }

                }
            }

            startRequest = new Date();
            xhr.open('GET', waitMsgURL + lastMsgID + '&' + startRequest.getTime(), true);
            xhr.send();
        }

        wait_new_messages();
    }
});

