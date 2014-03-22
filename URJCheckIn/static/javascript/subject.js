
/*Envia un POST al servidor para que ponga o elimine 
	la asignatura al usuario que lo solicita*/
function changeSignSeminar(){
	$('#alert_change_sign').html('');
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	$.post(window.location.href, $('#sign_seminar').serialize(), signedSeminarChanged);
}

/* Modifica el boton y realiza los cambios que implican el haberse apuntado 
	o desapuntado a un seminario */
function signedSeminarChanged(data) {
	if (data.ok) {
		if (data.is_student) {
			var n_students = $('#n_students');
			var val_n_students = Number(n_students.html());
			if (data.signed) {
				val_n_students++;
				$('#sign_button').replaceWith(newChangeSignButton('Desapuntarme', 
														'danger', 'remove-circle'));
			} else {
				val_n_students--;
				$('#sign_button').replaceWith(newChangeSignButton('Apuntarme', 
														'success', 'ok-circle'));
			}
			n_students.html(val_n_students);
		} else {
			if (data.signed) {
				var idsubj = window.location.pathname.split('/')[2];
				var professor_list = $('#profesor_list');
				if (professor_list.html().indexOf('La asignatura no es impartida') != -1)
					professor_list.html('');
				professor_list.append('<li id="professor_' + data.iduser + '">' +
							'<a onClick="ask_ajax_page(\'/profile/view/' + data.iduser + 
							'\', loadAjaxPage); return false;" href="/profile/view/' + 
							data.iduser + '">' + data.name + '</a></li>');
				$('#sign_button').replaceWith(newChangeSignButton('Dejar de ser organizador', 
														'danger', 'remove-circle'));
				$('#professor_options').show();
			} else {
				$('#professor_'+data.iduser).remove();
				$('#sign_button').replaceWith(newChangeSignButton('Hacerme organizador', 
														'success', 'ok-circle'));
				if ($('#profesor_list > li').size() <= 0)
					$('#profesor_list').html('La asignatura no es impartida por ' +
											'ning&uacute;n profesor.');
				$('#professor_options').hide();
			}
		}
	} else {
		if (!data.error)
			data['error'] = "Error interno desconocido";
		$('#alert_change_sign').html('<div class="alert alert-danger">' + 
										data['error'] + '</div>');
	}

	hideElements(['#loading_page']);
	enableButtons(['button']);
}

/* Devuelve un string con el html para el boton de apuntarse/desapuntarse
	con el texto indicado, el icono indicado y el color segun el tipo */
function newChangeSignButton(text, type, logo) {
	return '<button class="btn btn-' + type + ' btn-block" id="sign_button">' +
			'<span class="glyphicon glyphicon-' + logo + '"></span> ' +
			text + '</button>';
}


/* Pide mas clases a partir de idlesson, si newer es True pide las 
	clases siguientes y si es False las pasadas */
function askLessons(idlesson, newer) {
	if (newer) 
		disableButtons(['#ask_newer']);
	else
		disableButtons(['#ask_older']);
	path = window.location.pathname + '?idlesson=' + idlesson + '&newer=' + newer;
	$.getJSON(path, lessonsReceived);
}

/* Coloca las clases recibidas en su sitio */
function lessonsReceived(data) {
	if (data.newer) {
		var button = $('#ask_newer')
	} else {
		var button = $('#ask_older')
	}
	if (data.idlesson == 0) {
		button.replaceWith('<div class="btn btn-primary ' +
							'btn-sm btn-block disabled">No hay m&aacute;s clases</div>');
	} else {
		if (data.newer) {
			$('#future_lessons > a:last').after(data.lessons);
		} else {
			$('#past_lessons > a:last').after(data.lessons);
		}
		button.attr('onClick', 
					'askLessons(' + data.idlesson + ',' + data.newer + ');return false;');
	}
	button.removeAttr("disabled"); 
}

/* Envia el contenido del formulario idform para editar o eliminar un objeto */
function editObject(idform) {
	disableButtons(['button']);
	$('.object_alert').remove();
	$('#loading_page').css('display','inline');
	$.post(window.location.href, $('#' + idform).serialize(), objectEdited);
}

/*Si recibe errores los imprime en su lugar correspondiente y si recibe un deleted
	carga la pagina en data.redirect*/
function objectEdited(data) {
	if (data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], '#group_'+error, 'object_alert', 'danger');
	} else if (data.deleted) {
		$.getJSON(data.redirect, loadAjaxPage);
	}
	hideElements(['#loading_page']);
	enableButtons(['button']);
}

/* Solicita la creacion de una clase y si se crea redirige a ella */
function createLesson() {
	disableButtons(['button']);
	$('.lesson_alert').remove();
	$('#loading_page').css('display','inline');
	$.post(window.location.href, $('#new_class').serialize(), lessonCreated);
}

/*Si recibe errores los imprime en su lugar correspondiente y si recibe un ok
	carga la pagina en data.redirect*/
function lessonCreated(data) {
	if (data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], '#group_'+error, 'lesson_alert', 'danger');
	} else if (data.ok) {
		$.getJSON(data.redirect, loadAjaxPage);
	}
	hideElements(['#loading_page']);
	enableButtons(['button']);
}


