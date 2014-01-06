function checkIn() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(sendLocation, geolocationError, {enableHighAccuracy: true});
	} else {
		alert("Geolocalización no disponible en este dispositivo");
	}
}

function sendLocation(position) {//TODO
	alert("posicion: " + position.coords.latitude + ", " + 
			position.coords.longitude + " precision: " + 
			position.coords.accuracy);
}

function geolocationError(error) {
	alert("Error #" + error.code + " " + error.message);
}
