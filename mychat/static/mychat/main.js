"use strict"


var waitMsgURL = '/tornado/waitmsg';
var lastMsgID;



$(document).ready(function(){

	alert('Алерт мать вашу)');
	return;

	// получим последние 20 сообщений с сервера
	var xhr = new XMLHttpRequest();
	xhr.open('get', '/chat/last-messages', false);
	xhr.send();
	var messages = JSON.parse(xhr.responseText);
	var msgDiv = $('#messages');
	messages.messages.forEach(function(msg, i, arr){
		msgDiv.append('<p>' + msg.author + '<br />' + msg.text + '</p>');
	})

	function subscribe() {
		var xhr = new XMLHttpRequest();
		xhr.timeout = 100;
		xhr.ontimeout = function() {
			console.log('Закрываем соединение по таймауту');
			subscribe();
		}
		xhr.onreadystatechange = function() {
			console.log('readyState: ' + this.readyState + '  status: ' + this.status + ' statusText: ' + this.statusText + ' responseText: ' + this.responseText);
			if (this.readyState != 4 || this.status == 0) return;
			if (this.status == 500) {
				setTimeout(subscribe, 5000);
				return;
			}
			if (this.status == 200) {
				msgDiv.append('<p>' + this.responseText + '</p>');
			}
			subscribe();
		}
		xhr.open('GET', waitMsgURL, true);
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
