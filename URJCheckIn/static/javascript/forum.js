
/*TODO funcion que pida mensajes nuevos cada X tiempo*/

/* Envia el comentario con un POST, bloquea el boton hasta recibir respuesta */
function sendComment() {
	var content = $('#comment_field').val()
	if(content) {
		disableButtons(['#comment_button']);
		Dajaxice.app.publish_forum(commentSaved, {'comment': content});
	} else {
		alert('No puedes enviar comentarios vacios');
	}
}

/* Escribe el mensaje arriba */
function commentSaved(data) {
	if (data.error) {
		alert(data.error);
	} else if (data.ok) {
		$('#comment_field').val('');
		data['newer'] = true;
		data['comments'] = data.comment;
		commentsReceived(data);
	}
	enableButtons(['#comment_button']);
}

/* Pide mas comentarios del foro, si newer es True pide mas recientes y si es False anteriores*/
function askComments(id, newer) {
	disableButtons(['#ask_newer', '#ask_older']);
	Dajaxice.app.more_forum_comments(commentsReceived, {'current': id, 'newer': newer});
}

/* Coloca los mensajes recibidos en su sitio */
function commentsReceived(data) {
	//TODO una vez hecha funcion que los pida solos, si hay mensajes almacenados tambien se introducen
	if (data.idcomment == 0) {
		if (!data.newer) {
			$('#ask_older').replaceWith('<div class="btn btn-primary ' +
							'btn-sm btn-block disabled">No hay mensajes anteriores</div>')
		}
	} else {
		if (data.newer) {
			$('#forum_comment_list > li:first').before(data.comments);
			$('#ask_newer').attr('onClick', 
						'askComments(' + data.idcomment + ', true);return false;');
		} else {
			$('#forum_comment_list > li:last').after(data.comments);
			$('#ask_older').attr('onClick', 
						'askComments(' + data.idcomment + ', false);return false;');
		}
	}
	enableButtons(['#ask_newer', '#ask_older']);
}

