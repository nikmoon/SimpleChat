"use strict"

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

xhr.open("post", "/tornado/getmsg", false);
xhr.send("5");
if (xhr.responseText) {
	alert(xhr.responseText);
}
//alert(xhr.getAllResponseHeaders());
