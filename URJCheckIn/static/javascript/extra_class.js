function deleteClass(id) {
	$.post("http://" + document.location.host + "/class/" + id, "action=delete", //TODO mirar si es esa URL
				function() { removeFromDOM("#xc_" + id); })
				.fail(function() { alert( "Error al eliminar clase" ); });
}

function uncheckClass(id) {
	removeFromDOM("#xc_" + id);
	$.post("http://" + document.location.host + "/class/" + id, "action=uncheck", //TODO mirar si es esa URL
				function() { removeFromDOM("#xc_" + id); })
				.fail(function() { alert( "Error al desapuntarse del seminario" ); });
}

////////////////////LLEVAR A UN JS GENERICO
//Elimina el elemento con la id=id del arbol DOM
function removeFromDOM(id) {
	var elem = $(id);
	if (elem) elem.remove();
}
