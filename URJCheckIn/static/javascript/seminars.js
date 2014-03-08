
/* Envia un POST al servidor para que se cree un nuevo seminario */
function createSeminar() {
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	Dajaxice.app.create_seminar(seminarCreated, {'form':$('#create_seminar').serializeObject()});
}

/* Reactiva los botones y 'recarga' indica el resultado del cambio de password*/
function seminarCreated(data) {
	var alert_class = 'password_alert';
	if(data.error) {
		//TODO Poner alert donde corresponda
		alert(data.error);
		hideElements(['#loading_page']);
		enableButtons(['button']);
	} else if (data.idsubj) {
		ask_ajax_page('subject', loadAjaxPage, {'idsubj':data.idsubj});
	} else {
		alert("Se ha producido un error");
	}
}
