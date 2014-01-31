function checkIn() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(sendLocation, geolocationError, {enableHighAccuracy: true});
	} else {
		alert("Geolocalización no disponible en este dispositivo");
	}
}

function sendLocation(position) {
	var codeword = $('#codeword');
	if (codeword && codeword.val()) {
		var info = {
					'latitude':  position.coords.latitude,
					'longitude': position.coords.longitude,
					'accuracy': position.coords.accuracy,
					'codeword': codeword.val()
				};
		/*$.post("http://" + document.location.host + "/checkin", info, 
				function() { codeword.val("CheckIn realizado"); }) //TODO cambiar, poner en otro sitio el mensaje
				.fail(function() { alert( "Error al enviar el CheckIn" ); });*/
		Dajaxice.app.process_checkin(checkinDone, {'form': info});
	} else {
		alert ("Debes insertar el código");
	}
}

function checkinDone(data) {
	if (data.error) {
		alert("Error: " + data.error);
	} else if (data.ok) {
		$('#codeword').val('');
					//TODO enviar a la pagina de la clase para que la valore
		//TODO quitar cuando este el TODO anterior
		alert("¡Check in realizado!")
	}
}

function geolocationError(error) {
	alert("Error #" + error.code + " " + error.message);
}

