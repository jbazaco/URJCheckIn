
$(document).ready(function() {
	$('#mainbody').delegate('#create_seminar', 'submit', createSeminar);
})

/* Envia un POST al servidor para que se cree un nuevo seminario */
function createSeminar(event) {
	event.preventDefault();
	$('.seminar_alert').remove();
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	$.post($(this).attr('action'), $(this).serialize(), seminarCreated);
}

/* Reactiva los botones y 'recarga' indica el resultado del cambio de password*/
function seminarCreated(data) {
	var alert_class = 'seminar_alert';
	$('#loading_page').hide();
	enableButtons(['button']);
	if(data.errors) {
		//TODO HAY OTROS ERRORES!!
		for (error in data.errors)
			alertBefore(data.errors[error], 
				'#group_'+error, alert_class, 'danger');
	} else if (data.idsubj) {
		ask_ajax_page('/subjects/' + data.idsubj, loadAjaxPage);
	} else {
		alert("Se ha producido un error");
	}
}
