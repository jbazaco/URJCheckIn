/* Desactiva los botones que recibe en un array, indicados para obtenerse con $() */
function disableButtons(butts) {
	butts.forEach(function(butt) {
		$(butt).attr("disabled", "disabled"); 
	});
}

/* Activa los botones que recibe en un array, indicados para obtenerse con $() */
function enableButtons(butts) {
	butts.forEach(function(butt) {
		$(butt).removeAttr("disabled"); 
	});
}

/* Pone un elemento de la clase alert del tipo alert_type antes del 
	elemento con id elem_id, poniendole la clase class_id y los 
	mensajes del array errors como texto. En caso de que no existe el elemento
	elem_id, se pondra despues del elemento legend del formulario form_id */
function alertBefore(errors, elem_id, class_id, alert_type, form_id) {
	var error_msg = "";
	for (var i=0; i < errors.length; i++)
		error_msg += errors[i];
	elem = $(elem_id);
	if (elem.length > 0) {
		elem.before('<div class="row ' + class_id + '">' +
				'<div class="col-sm-10 col-sm-offset-1">' +
				'<div class="alert alert-'+ alert_type + '">' +
				error_msg + '</div></div></div>');
	} else { //en caso de que no exista el elemento sobre el que hay que ponerlo
		var form = $(form_id + ' legend');
		if (form.length > 0) {
			form.after('<div class="row ' + class_id + '">' +
					'<div class="col-sm-10 col-sm-offset-1">' +
					'<div class="alert alert-'+ alert_type + '">' +
					error_msg + '</div></div></div>');
		} else { //si tampoco existe el formulario
			alert(error_msg);
		}
	}
}


