
/* Genera un formulario para editar el perfil */
function showEditProfile() {
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
	hideElements(['#profile .fields']);
	$('#profile_form').css('display','inherit');
	$('#photo_form').css('display','inherit');
}

/* Oculta el formulario y muestra y modifica el perfil con los nuevos datos del usuario */
function unsetForm(user) {//TODO que coja los datos de la respuesta mejor
	$('#name_profile').html($('#id_name').val());
	$('#age_profile').html(user.age);
	$('#desc_profile').html(user.description);
	//TODO hacerlo con el resto de propiedades
	hideElements(['#profile_form', '#photo_form']);
	$('#profile .fields').css('display','inherit');
}

/* Elimina el boton de cancelar y cambia el texto del otro boton a 'Editar perfil' y lo habilita */
function restartButtons() {
	$('#editing_profile').addClass('hidden');
	$('#show_form').removeClass('hidden');
	enableButtons(['button']);
}

/* Cuando se recibe una confirmacion de los cambios realizados*/
function infoSaved(data) {//TODO hace otra cosa!!!
	if(data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], '#group_'+error, 
						'profile_alert', 'danger');
		enableButtons(['button']);
	} else {
		restartButtons();
		emptyPasswords();
		unsetForm(data.user);
	}
	hideElements(['#loading_page']);
}

/* Envia un POST al servidor para que actualice el perfil del usuario con la 
	informacion del formulario */
function sendChanges() {
	$('.profile_alert').remove();
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	$.post(window.location.href, $('#profile_form').serialize(), infoSaved);
}

/* Quita el formulario y vuelve a mostrar el perfil */
function cancelEditProfile() {
	hideElements(['#profile_form', '#photo_form']);
	emptyPasswords();
	$('#profile .fields').css('display','inherit');
	restartButtons();
}

/*Vacia los inputs de passwords*/
function emptyPasswords() {
	$('#old_password').val('');
	$('#new_password1').val('');
	$('#new_password2').val('');
}

/* Envia un POST al servidor para que modifique la password */
function changePassword() {//TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!
	$('.password_alert').remove();
	disableButtons(['button']);
	$('#loading_page').css('display','inline');
	$.post('/password_change/ajax', $('#password_form').serialize(), passwordChanged);
}

/* Reactiva los botones e indica el resultado del cambio de password*/
function passwordChanged(data) {
	var alert_class = 'password_alert';
	if(data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], 
				'#group_'+error, alert_class, 'danger');
	} else {
		alertBefore(['Contrase&ntilde;a cambiada con &eacute;xito'], 
				'#password_button', alert_class, 'success');
	}
	emptyPasswords();
	hideElements(['#loading_page']);
	enableButtons(['button']);
}

