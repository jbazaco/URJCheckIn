
$(document).ready(function() {
	$('#mainbody').delegate('#checkinbox', 'submit', checkIn);
})

function checkIn(event) {
	event.preventDefault();
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
	$('#latitude').attr('value', position.coords.latitude);
	$('#longitude').attr('value', position.coords.longitude);
	$('#accuracy').attr('value', position.coords.accuracy);
	$.post($('#checkinbox').attr('action'), $('#checkinbox').serialize(), checkinDone);
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

