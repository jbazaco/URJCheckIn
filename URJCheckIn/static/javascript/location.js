function checkIn() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(sendLocation, geolocationError, {enableHighAccuracy: true});
	} else {
		alert("Geolocalización no disponible en este dispositivo");
	}
}

function sendLocation(position) {
	$('#result_checkin').html("");
	var codeword = $('#codeword');
	if (codeword && codeword.val()) {
		var info = {
					'latitude':  position.coords.latitude,
					'longitude': position.coords.longitude,
					'accuracy': position.coords.accuracy,
					'idsubj': $('#subject_select').val(),
					'codeword': codeword.val(),
					'id_mark': $('#id_mark') ? $('#id_mark').val():-1,
					'id_comment': $('#id_comment') ? $('#id_comment').val():""
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
		$('#result_checkin').html("Error: " + data.error);
	} else if (data.ok) {
		$('#codeword').val('');
					//TODO enviar a la pagina de la clase para que la valore
		//TODO quitar cuando este el TODO anterior
		$('#result_checkin').html("¡Check in realizado!");
	}
}

function geolocationError(error) {
	alert("Error #" + error.code + " " + error.message);
}

