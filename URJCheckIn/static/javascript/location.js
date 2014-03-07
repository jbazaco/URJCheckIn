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
	$('#loading_page').css('display','inline');
	if (codeword && codeword.val()) {
		var info = {
					'latitude':  position.coords.latitude,
					'longitude': position.coords.longitude,
					'accuracy': position.coords.accuracy,
					'idsubj': $('#subject_select').val(),
					'codeword': codeword.val(),
					'id_mark': $('#id_mark').val() ? $('#id_mark').val():0,
					'id_comment': $('#id_comment').val() ? $('#id_comment').val():""
				};
		/*$.post("http://" + document.location.host + "/checkin", info, 
				function() { codeword.val("CheckIn realizado"); }) //TODO cambiar, poner en otro sitio el mensaje
				.fail(function() { alert( "Error al enviar el CheckIn" ); });*/
		Dajaxice.app.process_checkin(checkinDone, {'form': info});
	} else {
		hideElements(['#loading_page']);
		alert ("Debes insertar el código");
	}
}

function checkinDone(data) {
	if (data.error) {
		var msg = "Error: " + data.error;
		var alert_type = "danger";
	} else if (data.ok) {
		$('#codeword').val('');
		var msg = "Checkin realizado";
		var alert_type = "success";
	}
	hideElements(['#loading_page']);
	$('#alert_checkin').html('<div class="alert alert-' + alert_type + '"><button ' +
			'type="button" class="close" aria-hidden="true" data-dismiss="alert" ' +
			'aria-hidden="true">&times;</button><p>'+ msg + '</p></div>');
}

function geolocationError(error) {
	alert("Error #" + error.code + " " + error.message);
}

