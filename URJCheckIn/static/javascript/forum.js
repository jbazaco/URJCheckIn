
/* Envia el comentario con un POST, bloquea el boton hasta recibir respuesta */
function sendComment() {
	var content = $('#comment_field').val()
	if(content) {
		disableButtons(['#comment_button']);//LLAMAR CON LA FUNCION QUE TENGO QUE SACAR DE EDIT_PROFILE.JS
		$.post("http://" + document.location.host + "/forum", "comment="+content, commentSaved)
						.fail(errorCommenting);
	} else {
		alert('No puedes enviar comentarios vacios');
	}
}

function commentSaved() {
	$('#comment_field').val('');
	enableButtons(['#comment_button']);
	//poner los nuevos comentarios arriba
}

function errorCommenting() {
	enableButtons(['#comment_button']);
	alert('Error guardando el mensaje. Vuelve a intentarlo.');
}
