
$(document).ready(function(){
	// var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
	// var socket = new WebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);
	
	var socket = new WebSocket('ws://127.0.0.1:8000/chat/');
	socket.onopen = websocket_welcome;
	socket.onmessage = websocket_message_show;
	var queryString = window.location.href.substring(1);
	var varArray = queryString.split("/"); //eg. index.html?msg=1
    arrl = varArray.length;
    url = varArray[arrl-2]

	$('#Chatform').submit(function(event){
		event.preventDefault();
		var message_data={
			'username':$('input[name="username"]').val(),
			'usermsg':$('input[name="usermsg"]').val(),
			'userid':$('input[name="userid"]').val(),
			'room_id':url,
		}
		socket.send(JSON.stringify(message_data));
		$('#Chatform')[0].reset();
	});
});

function websocket_welcome(){

}


function websocket_message_show(e) {
	if (typeof e !== 'undefined') {
	    var message_data = JSON.parse(e.data);
	    
	    coding = "<h5 style='color:blue;'>" + message_data.username + "</h5>" +
			"<p class = 'coding'>"+ message_data.usermsg + "</p>";
		$('#messageCanvas').append(coding);
	}
}
