
/* Genera un formulario para editar el perfil */
function showEditProfile(id) {
	setForm();
	$('#change_profile')
						.html('Guardar cambios')
						.attr('onclick', "sendChanges('"+id+"')")
						.before("<button onclick=\"cancelEditProfile('" + id +
								"')\" id=\"cancel_edit_profile\">Cancelar</button>");
}

/* Genera las cajas para el formulario inicializando su valor con la informacion del perfil */
function setForm() {
	var name = $('#name_profile');
	name.wrap('<input disabled="disabled" class="name" value="' + name.html() + 
				'" type="text" name="name" maxlength="30" size="25px"> <input>');
	var age = $('#age_profile');
	age.wrap('<input class="name" value="' + "18" + //age.html() + //TODO
				'" type="number" name="age" min="18" max="100" step="1"> <input>'); //FIREFOX NO LO MUESTRA COMO NUMBER
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
	$('#change_profile')
						.html('Editar perfil')
						.attr('onclick', "showEditProfile('"+id+"')");
	$('#cancel_edit_profile').remove();
	enableButtons(['#change_profile']);
}

/* Cuando se recibe una confirmacion de los cambios realizados*/
function infoSaved() {//TODO hace otra cosa!!!
	restartButtons('ads'/*id*/);//TODO necesito la id!!
	hideElements(['#saving_profile']);
	unsetForm();
}

/* Avisa de que se ha producido un error y revierte los cambios */
function errorSaving() {
	hideElements(['#saving_profile']);
	alert("Error al cambiar el perfil. Vuelva a intentarlo.");
	enableButtons(['#change_profile', '#cancel_edit_profile']);
}

/* Envia un POST al servidor para que actualice el perfil del usuario con la 
	informacion del formulario */
function sendChanges(id) {
		disableButtons(['#change_profile', '#cancel_edit_profile']);
		$('#saving_profile').css('display','inline');
		var qstring = "age=" + $('#age_profile').parent().val(); // +& otras propiedades
		$.post("http://" + document.location.host + "/profile/view/" + id, qstring, infoSaved)
						.fail(errorSaving);
}

/* Quita el formulario y vuelve a mostrar el perfil */
function cancelEditProfile(id) {
	$('#name_profile').unwrap();
	$('#age_profile').unwrap();
	restartButtons(id);
}

/* Desactiva los botones que recibe en un array, indicados para obtenerse con $() */
//TODO poner en un .js con funciones basicas
function disableButtons(butts) {
	butts.forEach(function(butt) {
		$(butt).attr("disabled", "disabled"); 
	});
}

/* Activa los botones que recibe en un array, indicados para obtenerse con $() */
//TODO poner en un .js con funciones basicas
function enableButtons(butts) {
	butts.forEach(function(butt) {
		$(butt).removeAttr("disabled"); 
	});
}

/* Oculta los elementos que recibe en un array, indicados para obtenerse con $() */
//TODO poner en un .js con funciones basicas
function hideElements(elems){
	elems.forEach(function(elem) {
		$(elem).css('display', 'none'); 
	});
}

