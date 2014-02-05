/* Desactiva los botones que recibe en un array, indicados para obtenerse con $() */
function disableButtons(butts) {
	butts.forEach(function(butt) {
		$(butt).attr("disabled", "disabled"); 
	});
}

/* Activa los botones que recibe en un array, indicados para obtenerse con $() */
function enableButtons(butts) {
	butts.forEach(function(butt) {
		$(butt).removeAttr("disabled"); 
	});
}

/* Oculta los elementos que recibe en un array, indicados para obtenerse con $() */
function hideElements(elems){
	elems.forEach(function(elem) {
		$(elem).css('display', 'none'); 
	});
}

/*Inserta el html en data segun la id y cambia la url por la que haya en data.url
	Callback para funciones de dajaxice*/
function loadAjaxPage(data) {
	/*echarle un ojo a lo de onpopstate*/
	window.history.pushState({/*datos para window.onpopstate*/}, "URJCheckin", data.url);
	insertHtml(data);		
}

/*Inserta el html en data segun la id ignorando el elemento url*/
function insertHtml(data) {
	delete data.url;
	for (var id in data) {
		if (id) $(id).html(data[id]);
	}
}

/*Para controlar el boton de atras y alante del navegador*/
window.onpopstate = function() {
	var path = window.location.pathname;
	var pathsplit = path.split('/');
	switch(pathsplit[1]){
	case "checkin": //Fastidia el history
		if (pathsplit.length === 2)
			Dajaxice.app.checkin(insertHtml);
		else
			Dajaxice.app.not_found(insertHtml);
		break;
	case "":
		Dajaxice.app.home(insertHtml);
		break;
	case "forum":
		if (pathsplit.length === 2)
			Dajaxice.app.forum(insertHtml);
		else
			Dajaxice.app.not_found(insertHtml);
		break;
	case "subjects":
		if (pathsplit.length === 2)
			Dajaxice.app.subjects(insertHtml);
		else if (pathsplit.length === 3)
			Dajaxice.app.subject(insertHtml, {'idsubj': pathsplit[2]});
		else
			Dajaxice.app.not_found(insertHtml);
		break;
	case "class":
		if (pathsplit.length === 3)
			Dajaxice.app.class_info(insertHtml, {'idclass': pathsplit[2]})
		else
			Dajaxice.app.not_found(insertHtml);
		break;
	case "profile":
		if(pathsplit.length === 4 && pathsplit[2] === "view")
			Dajaxice.app.profile(insertHtml, {'iduser': pathsplit[3]})
		else
			Dajaxice.app.not_found(insertHtml, {'path': path});
		break;
	default:
		Dajaxice.app.not_found(insertHtml, {'path': path});
		break;
	}
};
