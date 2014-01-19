
/* Genera un formulario para editar el perfil */
function showEditProfile(id) {
	setForm();
	$('#show_form')
					.html('Cancelar')
					.attr('onclick', "cancelEditProfile('"+id+"')")
					.after('<button type="submit" name="checkin_submit" id="save_changes" form="profile_form"' + 
								'>Guardar Cambios</button>');
}

/* Genera las cajas para el formulario inicializando su valor con la informacion del perfil */
function setForm() {
	var name = $('#name_profile');
	name.wrap('<input disabled="disabled" class="name" value="' + name.html() + 
				'" type="text" name="name" maxlength="30" size="25px" form="profile_form"> </input>');
	var age = $('#age_profile');
	age.wrap('<input class="name" required value="' + "18" + //age.html() + //TODO
				'" type="number" name="age" min="17" max="100" step="1" form="profile_form"/> </input>'); //FIREFOX NO LO MUESTRA COMO NUMBER
	//TODO para el resto de campos
}

/* Realiza un unwrap de cada campo del perfil del usuario y modifica su valor
	por el que se relleno en el formulario */
function unsetForm() {//TODO que coja los datos de la respuesta mejor
	$('#name_profile').unwrap();
	var age = $('#age_profile');
	if (age.parent().val()) age.html(age.parent().val());
	age.unwrap();
	//TODO hacerlo con el resto de propiedades
}

/* Elimina el boton de cancelar y cambia el texto del otro boton a 'Editar perfil' y lo habilita */
function restartButtons(id) {
	$('#show_form')
						.html('Editar perfil')
						.attr('onclick', "showEditProfile('"+id+"')");
	$('#save_changes').remove();
	enableButtons(['button']);
}

/* Cuando se recibe una confirmacion de los cambios realizados*/
function infoSaved(data, textStatus, jqXHR ) {//TODO hace otra cosa!!!
	restartButtons(this.url.split("/").pop());//TODO necesito la id!!
	hideElements(['#saving_profile']);
	unsetForm();
}

/* Avisa de que se ha producido un error y revierte los cambios */
function errorSaving() {
	hideElements(['#saving_profile']);
	alert("Error al cambiar el perfil. Vuelva a intentarlo.");
	enableButtons(['button']);
}

/* Envia un POST al servidor para que actualice el perfil del usuario con la 
	informacion del formulario */
function sendChanges(id) {
		disableButtons(['button']);
		$('#saving_profile').css('display','inline');
		$.post("http://" + document.location.host + "/profile/view/" + id, 
								$('#profile_form').serialize(), infoSaved)
				.fail(errorSaving);
}

/* Quita el formulario y vuelve a mostrar el perfil */
function cancelEditProfile(id) {
	$('#name_profile').unwrap();
	$('#age_profile').unwrap();
	restartButtons(id);
}

