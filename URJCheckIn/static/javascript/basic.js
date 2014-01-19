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
