
function showEditProfile(id) {
	setForm();
	$('#change_profile')
						.html('Guardar cambios')
						.attr('onclick', "sendChanges('"+id+"')")
						.before("<button onclick=\"cancelEditProfile('" + id +
								"')\" id=\"cancel_edit_profile\">Cancelar</button>");
}

function setForm() {
	var name = $('#name_profile');
	name.wrap('<input disabled="disabled" class="name" value="' + name.html() + 
				'" type="text" name="name" maxlength="30" size="25px"> <input>');
	var age = $('#age_profile');
	age.wrap('<input class="name" value="' + "18" + //age.html() + //TODO
				'" type="number" name="age" min="18" max="100" step="1"> <input>'); //FIREFOX NO LO MUESTRA COMO NUMBER
}

function sendChanges(id) {
	alert('Enviar cambios aquí');
	//TODO
	//enviarlo
	//cambiarlo por lo que hay en cada caja + unwrap
	//si hay error notificarlo y recargar pagina
}

function cancelEditProfile(id) {
	$('#name_profile').unwrap();
	$('#age_profile').unwrap();
	$('#change_profile')
						.html('Editar perfil')
						.attr('onclick', "showEditProfile('"+id+"')");
	$('#cancel_edit_profile').remove();
}
