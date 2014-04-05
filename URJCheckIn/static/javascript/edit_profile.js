
$(document).ready(function() {
	$('#mainbody').delegate('#show_form', 'click', showEditProfile);
	$('#mainbody').delegate('#hide_form', 'click', cancelEditProfile);
	$('#mainbody').delegate('#password_form', 'submit', changePassword);
	$('#mainbody').delegate('#profile_form', 'submit', sendChanges);

	/*Al no estar siempre #photo_form, tiene que escucharse con delegate, pero el envio del
	formulario se realiza con ajaxForm, por lo que se activa cuando existe y se intenta enviar,
	y para evitar que se vuelva a ejecutar la funcion de delegate se quita la clase unsetted_form*/
	$('#mainbody').delegate('#photo_form.unsetted_form', 'submit', function(event) {
		event.preventDefault();
		$(this).removeClass('unsetted_form');
		/*para subir la imagen con ajax*/
		$('#photo_form').ajaxForm({
			beforeSubmit: function() {
				$('#loading_page').show();
				disableButtons(['button']);
			},
			success: photoChanged
		});
		/* Para que se dispare el evento ajaxForm*/
		$('#photo_form').trigger('submit');
	});
	$('#mainbody').delegate('#delete_prof_img', 'submit', deletePhoto);
})

/*Envia una peticion para eliminar la foto de perfil*/
function deletePhoto(event) {
	event.preventDefault();
	disableButtons(['button']);
	$('#loading_page').show();
	$.post($(this).attr('action'), $(this).serialize(), photoChanged);
}

/*Muestra el perfil con la nueva foto*/
function photoChanged(data) {
	$('#loading_page').hide();
	enableButtons(['button']);
	if (data.ok) {
		$('#profile_img').attr('src', data.img_url+"?="+ Math.round(100000*Math.random()));
		$('#hide_form').trigger('click');
	} else {
		alert(data.error||"error al modificar la foto");
	}
}

/* Genera un formulario para editar el perfil */
function showEditProfile(event) {
	setForm();
	$('#show_form').addClass('hidden');
	$('#editing_profile').removeClass('hidden');
}

/* Muestra el formulario inicializando su valor con la informacion del perfil y oculta el perfil*/
function setForm() {
	$('#id_name').attr('value', $('#name_profile').html());
	$('#id_age').attr('value', $('#age_profile').html()); //FIREFOX NO LO MUESTRA COMO NUMBER
	$('#id_description').html($('#desc_profile').html());
	//TODO para el resto de campos
	$('#profile').hide();
	$('#profile_form').css('display','inherit');
	$('#photo_form').css('display','inherit');
}

/* Oculta el formulario y muestra y modifica el perfil con los nuevos datos del usuario */
function unsetForm(user) {//TODO que coja los datos de la respuesta mejor
	$('#name_profile').html($('#id_name').val());
	$('#age_profile').html(user.age);
	$('#desc_profile').html(user.description);
	//TODO hacerlo con el resto de propiedades
	$('#profile_form').hide();
	$('#photo_form').hide();
	$('#profile').show();
}

/* Elimina el boton de cancelar y cambia el texto del otro boton a 'Editar perfil' y lo habilita */
function restartButtons() {
	$('#editing_profile').addClass('hidden');
	$('#show_form').removeClass('hidden');
	enableButtons(['button']);
}

/* Cuando se recibe una confirmacion de los cambios realizados*/
function infoSaved(data) {
	if(data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], '#group_'+error, 
						'profile_alert', 'danger', '#profile_form');
		enableButtons(['button']);
	} else {
		restartButtons();
		emptyPasswords();
		unsetForm(data.user);
	}
	$('#loading_page').hide();
}

/* Envia un POST al servidor para que actualice el perfil del usuario con la 
	informacion del formulario */
function sendChanges(event) {
	event.preventDefault();
	$('.profile_alert').remove();
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	$.post($(this).attr('action'), $(this).serialize(), infoSaved);
}

/* Quita el formulario y vuelve a mostrar el perfil */
function cancelEditProfile() {
	$('#profile_form').hide();
	$('#photo_form').hide();
	emptyPasswords();
	$('#profile').show();
	restartButtons();
}

/*Vacia los inputs de passwords*/
function emptyPasswords() {
	$('#old_password').val('');
	$('#new_password1').val('');
	$('#new_password2').val('');
}

/* Envia un POST al servidor para que modifique la password */
function changePassword(event) {
	event.preventDefault();
	$('.password_alert').remove();
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	$.post('/password_change/ajax', $(this).serialize(), passwordChanged);
}

/* Reactiva los botones e indica el resultado del cambio de password*/
function passwordChanged(data) {
	var alert_class = 'password_alert';
	if(data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], 
				'#group_'+error, alert_class, 'danger', '#password_form');
	} else {
		alertBefore(['Contrase&ntilde;a cambiada con &eacute;xito'], 
				'#password_button', alert_class, 'success', '#password_form');
	}
	emptyPasswords();
	$('#loading_page').hide();
	enableButtons(['button']);
}



