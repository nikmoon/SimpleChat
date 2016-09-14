//"use strict"

function my_test() {
	var i = 1;
	for (var propName in window) {
		document.write(i + ". " + propName + '<br/>');
		i++;
	}
}

function my_args() {
	alert(arguments.length);
}

var xhr = new XMLHttpRequest();

xhr.open("get", "https://www.yandex.ru", false);
xhr.send();
alert(xhr.getAllResponseHeaders());
