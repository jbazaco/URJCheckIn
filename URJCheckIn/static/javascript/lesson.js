
$(document).ready(function() {
	$('#mainbody').delegate('button.show_map', 'click', show_location);
	$('#mainbody').delegate('#free_room_form', 'submit', askFreeRoom);
})

/* Muestra un mapa con la localizacion contenida en el boton y la localizacion del aula */
function show_location() {
	var img_url = 'http://maps.googleapis.com/maps/api/staticmap?center=' + $(this).attr('name') +
				'&zoom=10&size=300x200&sensor=false&markers=color:red%7C' + $(this).attr('name') +
				'&markers=color:green%7C' + $('#room_latitude').html() + ',' + 
				$('#room_longitude').html();
	$(this).after('<img class="map" src="' + img_url + '" width="300" height="200">');
	$(this).remove();
}

/* Envia el formulario con un GET para pedir un aula libre */
function askFreeRoom(event) {
	event.preventDefault();
	$('.free_room_alert').remove();
	disableButtons(['button']);
	$('#loading_page').show();
	$.get($(this).attr('action'), $(this).serialize(), freeRoomReceived);
}

/* Reactiva los botones e imprime el aula libre*/
function freeRoomReceived(data) {
	var alert_class = 'free_room_alert';
	$('#loading_page').hide();
	enableButtons(['button']);
	if(data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], 
				'#group_fr_'+error, alert_class, 'danger', '#free_room_form');
	} else if (data.ok) {
		alertBefore('Aula libre: ' + data.free_room, 
				'#free_room_form button', alert_class, 'success', '#free_room_form');
	} else {
		alert("Se ha producido un error");
	}
}
