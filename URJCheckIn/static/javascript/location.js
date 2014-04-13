
$(document).ready(function() {
	$('#mainbody').delegate('#checkinbox', 'submit', checkIn);
})

var checkin_alert_class = 'alert_checkin';

function checkIn(event) {
	event.preventDefault();
	$('.'+checkin_alert_class).remove();
	$('#result_checkin').html("");
	$('#loading_page').css('display','inline');
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(sendLocation, geolocationError, {enableHighAccuracy: true});
	} else {
		$.post($('#checkinbox').attr('action'), $('#checkinbox').serialize(), checkinDone);
	}
}

/* Rellena los inputs Longitude y Latitude con la posicion */
function sendLocation(position) {
	$('#id_latitude').attr('value', position.coords.latitude);
	$('#id_longitude').attr('value', position.coords.longitude);
	$.post($('#checkinbox').attr('action'), $('#checkinbox').serialize(), checkinDone);
}

function checkinDone(data) {
	if (data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], 
				'#group_'+error, checkin_alert_class, 'danger', '#checkinbox');
	} else if (data.ok) {
		$('#id_codeword').val('');
		$('#id_longitude').attr('value', '');
		$('#id_latitude').attr('value', '');
		$('#id_comment').val('');
		$('#id_mark').val('3');
		$('#n_students').val('0');
	}
	$('#loading_page').hide();
	if (data.msg) {
		if (data.ok)
			alert_type = "success";
		else
			alert_type = "danger";
		$('#alert_checkin').html('<div class="alert alert-' + alert_type + '"><button ' +
			'type="button" class="close" aria-hidden="true" data-dismiss="alert" ' +
			'aria-hidden="true">&times;</button><p>'+ data.msg + '</p></div>');
	}
}

/* En caso de error informa al usuario sobre el error y envia el formulario sin la localizacion.
	Esto es lo mas logico puesto que el error puede deberse a que el usuario ha denegado la
	localizacion o es imposible localizarlo, por lo que tiene que poder realizar el checkin de 
	alguna manera */
function geolocationError(error) {
	alertBefore('Error #' + error.code + ' ' + error.message + 
				' (check in enviado sin geolocalizaci&oacute;n)', 
				'#checkinbox button', checkin_alert_class, 'warning', '#checkinbox');
	$.post($('#checkinbox').attr('action'), $('#checkinbox').serialize(), checkinDone);
	$('#loading_page').hide();
}

/* funcion cogida de https://github.com/LazarSoft/jsqrcode */
function handleFiles(f) {
	var o=[];
	for(var i =0;i<f.length;i++)
	{
	  var reader = new FileReader();

      reader.onload = (function(theFile) {
        return function(e) {
          qrcode.decode(e.target.result);
        };
      })(f[i]);

      // Read in the image file as a data URL.
      reader.readAsDataURL(f[i]);	}
}

function setQRDecoder() {
	$('#qr_uploader').show();
	qrcode.callback = function(msg) { $('#id_codeword').val(msg); };
}

