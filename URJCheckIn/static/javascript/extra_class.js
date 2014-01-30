function deleteClass(id) {
	console.log("AAAAAAAA");
	Dajaxice.app.process_class(removeFromDOM, {'idclass':id});
	console.log("BBB");
	/*$.post("http://" + document.location.host + "/class/" + id, "action=delete", //TODO mirar si es esa URL
				function() { removeFromDOM("#xc_" + id); })
				.fail(function() { alert( "Error al eliminar clase" ); });*/
}

function uncheckClass(id) {
	Dajaxice.app.process_class(removeFromDOM, {'idclass':id});
	/*$.post("http://" + document.location.host + "/class/" + id, "action=uncheck", //TODO mirar si es esa URL
				function() { removeFromDOM("#xc_" + id); })
				.fail(function() { alert( "Error al desapuntarse del seminario" ); });*/
}

////////////////////LLEVAR A UN JS GENERICO
//Elimina el elemento con la id=id del arbol DOM
function removeFromDOM(/*id*/data) {
	console.log("CCCC");
	/*var elem = $(id);
	if (elem) elem.remove();*/
	for (i=0; i<data.length; i++) {
		console.log($(data[i]));
		$(data[i]).remove();
		console.log("removed");
	}
}
