
/* Envia el comentario de la clase con un POST, bloquea el boton hasta recibir respuesta */
function sendClassComment(idclass) {
	var content = $('#comment_field').val()
	if(content) {
		disableButtons(['#comment_button']);
		Dajaxice.app.process_class(commentClassSaved, 
						{'form':$('#comment_form').serializeObject(),
						'idclass':idclass});
	} else {
		alert('No puedes enviar comentarios vacios');
	}
}

function commentClassSaved(data) {
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
