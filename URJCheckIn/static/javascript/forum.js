
/* Envia el comentario con un POST, bloquea el boton hasta recibir respuesta */
function sendComment() {
	var content = $('#comment_field').val()
	if(content) {
		disableButtons(['#comment_button']);//LLAMAR CON LA FUNCION QUE TENGO QUE SACAR DE EDIT_PROFILE.JS
		/*$.post("http://" + document.location.host + "/forum", $('#comment_form').serialize(), commentSaved)
						.fail(errorCommenting);*/
		Dajaxice.app.publish_forum(commentSaved, {'comment': content});
	} else {
		alert('No puedes enviar comentarios vacios');
	}
}

function commentSaved(data) {
	if (data.error) {
		alert(data.error);
	} else if (data.ok) {
		$('#comment_field').val('');
			//TODO cargar ese comentario y los nuevos
		//TODO quitar cuando se haga el TODO anterior
		alert("Comentario guardado");
	}
	enableButtons(['#comment_button']);
	//poner los nuevos comentarios arriba
}

/*function errorCommenting() {
	enableButtons(['#comment_button']);
	alert('Error guardando el mensaje. Vuelve a intentarlo.');
}*/
