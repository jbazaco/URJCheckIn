/*Inserta el html en data segun la id y cambia la url por la que haya en data.url
	y esconde el elemento #loading_page
	Callback para funciones de dajaxice*/
function loadAjaxPage(data) {
	/*echarle un ojo a lo de onpopstate*/
	window.history.pushState({/*datos para window.onpopstate*/}, "URJCheckin", data.url);
	hideElements(['#loading_page']);
	insertHtml(data);		
}

/*Inserta el html en data segun la id ignorando el elemento url y realiza un scroll
	al principio de la ventana*/
function insertHtml(data) {
	window.scrollTo(window.pageXOffset, 0);
	delete data.url;
	for (var id in data) {
		if (id) $(id).html(data[id]);
	}
}

/*Realiza una peticion ajax al recurso app.dfunct, pasandole un callback
	y los argumento a enviar, mostrando el elemento #loading_page*/
function ask_ajax_page(dfunct, callback, arg) {
	$('#loading_page').css('display','inherit');
	Dajaxice.app[dfunct](callback, arg);
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
		else if (pathsplit.length === 3 /*TODO && pathsplit[2] es un numero*/)
			Dajaxice.app.subject(insertHtml, {'idsubj': pathsplit[2]});
		else
			Dajaxice.app.not_found(insertHtml);
		break;
	case "class":
		if (pathsplit.length === 3 /*TODO && pathsplit[2] es un numero*/)
			Dajaxice.app.class_info(insertHtml, {'idclass': pathsplit[2]})
		else
			Dajaxice.app.not_found(insertHtml);
		break;
	case "profile":
		if(pathsplit.length === 4 && pathsplit[2] === "view" /*TODO && pathsplit[3] es un numero*/)
			Dajaxice.app.profile(insertHtml, {'iduser': pathsplit[3]})
		else
			Dajaxice.app.not_found(insertHtml, {'path': path});
		break;
	default:
		Dajaxice.app.not_found(insertHtml, {'path': path});
		break;
	}
};

