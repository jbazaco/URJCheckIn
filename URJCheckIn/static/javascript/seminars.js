
/* Envia un POST al servidor para que se cree un nuevo seminario */
function createSeminar() {
	$('.seminar_alert').remove();
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	var form = $('#create_seminar').serializeObject();
	//Si solo se selecciona uno no crea un array lo que provoca errores al validar el form
	if (!isNaN(form['degrees'])) form['degrees'] = [form['degrees']];
	Dajaxice.app.create_seminar(seminarCreated, {'form':form});
}

/* Reactiva los botones y 'recarga' indica el resultado del cambio de password*/
function seminarCreated(data) {
	var alert_class = 'seminar_alert';
	hideElements(['#loading_page']);
	enableButtons(['button']);
	if(data.errors) {
		//TODO HAY OTROS ERRORES!!
		for (error in data.errors)
			alertBefore(data.errors[error], 
				'#group_'+error, alert_class, 'danger');
	} else if (data.idsubj) {
		ask_ajax_page('subject', loadAjaxPage, {'idsubj':data.idsubj});
	} else {
		alert("Se ha producido un error");
	}
}
