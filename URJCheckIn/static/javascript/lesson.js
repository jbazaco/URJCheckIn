
$(document).ready(function() {
	$('#mainbody').delegate('button.show_map', 'click', show_location);
})

function show_location() {
	var img_url = 'http://maps.googleapis.com/maps/api/staticmap?center=' + $(this).attr('name') +
				'&zoom=10&size=300x200&sensor=false&markers=color:red%7C' + $(this).attr('name') +
				'&markers=color:green%7C' + $('#room_latitude').html() + ',' + 
				$('#room_longitude').html();
	$(this).after('<img class="map" src="' + img_url + '" width="300" height="200">');
	$(this).remove();
}

