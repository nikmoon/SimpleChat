



$(document).ready(function(){

	"use strict"

	var waitMsgURL = '/tornado/waitmsg';
	var lastMsgID;


	var waitTimeout = 0;
	var timeoutStep = 5000;


	// получим последние 20 сообщений с сервера
	var xhr = new XMLHttpRequest();
	xhr.open('get', '/chat/last-messages', false);
	xhr.send();
	var messages = JSON.parse(xhr.responseText);
	var msgDiv = $('#messages');
	lastMsgID = messages.lastID;
	messages.messages.forEach(function(msg, i, arr){
		msgDiv.append('<p>' + msg.username + ' ' + msg.id + '<br />' + msg.text + '</p>');
	})
	msgDiv.scrollTop(msgDiv[0].scrollHeight);


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
//	xhr.send('Примите новое сообщение');
	if (xhr.responseText) {
//		alert(xhr.responseText);
	}
	else {
//		alert('Пустой ответ');
	}

	return {};

})();

alert($);
*/

//alert(xhr.getAllResponseHeaders());
