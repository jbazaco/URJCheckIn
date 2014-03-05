
/* Genera un formulario para editar el perfil */
function showEditProfile(id) {
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
function restartButtons(id) {
	$('#editing_profile').addClass('hidden');
	$('#show_form').removeClass('hidden');
	enableButtons(['button']);
}

/* Cuando se recibe una confirmacion de los cambios realizados*/
function infoSaved(data) {//TODO hace otra cosa!!!
	if(data.errors) {
		errorSaving(data.errors);
	} else {
		restartButtons(data.user.id);//TODO necesito la id!!
		emptyPasswords();
		hideElements(['#saving_profile']);
		unsetForm(data.user);
	}
}

/* Avisa de que se ha producido un error y revierte los cambios */
function errorSaving(errors) {
	hideElements(['#saving_profile']);
	var errorstr = "";
	for (error in errors)
		errorstr += error + ": " + errors[error] + "\n";
	alert(errorstr);
	enableButtons(['button']);
}

/* Envia un POST al servidor para que actualice el perfil del usuario con la 
	informacion del formulario */
function sendChanges(id) {
		disableButtons(['button']);
		$('#saving_profile').css('display','inline');
		/*$.post("http://" + document.location.host + "/profile/view/" + id, 
								$('#profile_form').serialize(), infoSaved)
				.fail(errorSaving);*/
		Dajaxice.app.update_profile(infoSaved, {'iduser': id, 'form':$('#profile_form').serializeObject()});
}

/* Quita el formulario y vuelve a mostrar el perfil */
function cancelEditProfile(id) {
	hideElements(['#profile_form', '#photo_form']);
	emptyPasswords();
	$('#profile .fields').css('display','inherit');
	restartButtons(id);
}

/*Vacia los inputs de passwords*/
function emptyPasswords() {
	$('#old_password').val('');
	$('#new_password').val('');
	$('#rep_password').val('');
}

