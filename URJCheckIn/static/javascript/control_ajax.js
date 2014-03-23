
$(document).ready(function() {
	$('body').delegate('a.ajax', 'click', event_ask_ajax_page);
})

/* Pide la pagina en el href del elemento seleccionado y carga su contenido */
function event_ask_ajax_page(event) {
	$('#loading_page').css('display','inherit');
	var href = $(this).attr('href');
	event.preventDefault();
	$.getJSON(href, loadAjaxPage);
}

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
function ask_ajax_page(url, callback, arg) {
	$('#loading_page').css('display','inherit');
	$.getJSON(url, callback);
}



/*Para controlar el boton de atras y alante del navegador
	El timeout es para evitar que algunos navegadores como Chrome 
	y Safari lancen el evento al cargar la pagina inicialmente*/
window.setTimeout(function(){
    window.onpopstate = function(){
		$.getJSON(window.location.href, insertHtml)
    };
}, 1000);

/*Para cerrar el menu desplegable en pantallas pequenas al pulsar
	sobre un enlace*/
$(document).ready(function() {
	$('.nav a').on('click touchend', function(){
		/*Solo si el menu esta compacto (en pantallas pequenas)*/
		if($('.navbar-toggle').css('display') != 'none')
			$(".navbar-toggle").trigger( "click" );
	});
});
