$(document).ready(function() {
	$('#mainbody').delegate('#control_filter', 'submit', filterControl);
})

/* Envia un GET al servidor para obtener la infromacion filtrada */
function filterControl(event) {
	event.preventDefault();
	disableButtons(['button']);
	$('#loading_page').show();
	$.get($(this).attr('action'), $(this).serialize(), loadAjaxPage);
}
