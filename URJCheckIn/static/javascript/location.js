
$(document).ready(function() {
	$('#mainbody').delegate('#checkinbox', 'submit', checkIn);
	$('#mainbody').delegate('#without_geolocation', 'click', sendWithoutGeolocation);
})

var checkin_alert_class = 'alert_checkin';

/* Envia el formulario sin la localizacion si el navegador no tiene localizacion
	o localiza al usuario y envia el formulario con su posicion */
function checkIn(event) {
	event.preventDefault();
	$('.'+checkin_alert_class).remove();
	$('#result_checkin').html("");
	$('#loading_page').css('display','inline');
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(sendLocation, geolocationError, 
		{enableHighAccuracy: true, timeout: 5000});
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
	var error_msg;
	if (error.code == 1) {
		error_msg = 'Acceso a la localizaci&oacute;n denegado';
	} else if (error.code == 2) {
		error_msg = 'Posici&oacute;n no disponible';
	} else if (error.code == 3) {
		error_msg = 'El tiempo de localizaci&oacute;n excedi&oacute; el l&iacute;mite';
	} else {
		error_msg = error.message;
	}
	error_msg += ' <a href="#" id="without_geolocation" class="btn btn-info">' + 
				'<span class="glyphicon glyphicon-circle-arrow-right"></span> ' +
				'Enviar sin localizaci&oacute;n</a>';
	alertBefore(error_msg, '#checkinbox button', checkin_alert_class, 'warning', '#checkinbox');
	$('#loading_page').hide();
}

/* Envia el formulario sin intentar localizar al usuario */
function sendWithoutGeolocation(event) {
	event.preventDefault();
	$('.'+checkin_alert_class).remove();
	$('#result_checkin').html("");
	$('#loading_page').css('display','inline');
	$.post($('#checkinbox').attr('action'), $('#checkinbox').serialize(), checkinDone);
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

