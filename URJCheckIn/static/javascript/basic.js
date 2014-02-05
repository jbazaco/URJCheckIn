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
	console.log(pathsplit[1]);
	/*switch(pathsplit[1]){
	case "checkin": //Fastidia el history
		Dajaxice.app.checkin(insertHtml);
		break;
	case "":
		Dajaxice.app.home(insertHtml);
		break;
	case "forum":
		Dajaxice.app.forum(insertHtml);
		break;
	case "subjects":
		//if pathsplit[2]
		Dajaxice.app.subjects(insertHtml);
		break;
	case "subject":
		break;
	case "class":
		break;
	case "profile":
		break;
	default:
		//TODO las que varian
		alert(window.location.pathname);
		break;
	}*/
};
