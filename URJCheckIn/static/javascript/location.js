function checkIn() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(sendLocation, geolocationError, {enableHighAccuracy: true});
	} else {
		alert("Geolocalización no disponible en este dispositivo");
	}
}

function sendLocation(position) {//TODO
	var codeword = $('#codeword');
	if (codeword && codeword.val()) {
		alert("posicion: " + position.coords.latitude + ", " + 
			position.coords.longitude + "\nprecision: " + 
			position.coords.accuracy + "\n" + codeword.val());
		codeword.val("");
	} else {
		alert ("Debes insertar el código");
	}
}

function geolocationError(error) {
	alert("Error #" + error.code + " " + error.message);
}
