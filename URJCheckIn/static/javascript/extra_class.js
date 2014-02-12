function deleteClass(id) {
	Dajaxice.app.process_class(removeFromDOM, {'form':{'idclass':id, 'actions':'delete'}});
	/*$.post("http://" + document.location.host + "/class/" + id, "action=delete", //TODO mirar si es esa URL
				function() { removeFromDOM("#xc_" + id); })
				.fail(function() { alert( "Error al eliminar clase" ); });*/
}

function uncheckClass(id) {//TODO posiblemente mejor fusionar con la de arriba
	Dajaxice.app.process_class(removeFromDOM, {'form':{'idclass':id, 'actions':'uncheck'}});
	/*$.post("http://" + document.location.host + "/class/" + id, "action=uncheck", //TODO mirar si es esa URL
				function() { removeFromDOM("#xc_" + id); })
				.fail(function() { alert( "Error al desapuntarse del seminario" ); });*/
}

////////////////////LLEVAR A UN JS GENERICO
//Elimina el elemento con la id=id del arbol DOM
function removeFromDOM(/*id*/data) {//TODO realmente le pasare un array de id y los borrara
									//Sera un callback general el que se encargue de comprobar errores, deletefromdom, html...
	console.log("CCCC");
	/*var elem = $(id);
	if (elem) elem.remove();*/
	for (i=0; i<data['deleteFromDOM'].length; i++) {
		$(data['deleteFromDOM'][i]).remove();
	}
}
