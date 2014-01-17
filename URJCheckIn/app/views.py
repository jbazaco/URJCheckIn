# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError

#TODO comprobar que el usuario esta registrado antes de enviar una pagina
# y actuar en consecuencia


def not_found(request):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	return render_to_response('404.html', {},	#mostrar en el html las paginas mas "frecuentes"
																	#checkin, inicio, perfil...
		context_instance=RequestContext(request))


def home(request):
	"""Devuelve la pagina de inicio"""
	if request.method != "GET":
		return method_not_allowed(request)
	
	return render_to_response('home.html', {},
		context_instance=RequestContext(request))


def checkin(request):
	"""Devuelve la pagina para hacer check in (GET) o procesa un check in (POST)"""
	if request.method == "POST":
		#TODO guardar la informacion en la BD y procesarla si es necesario
		#de momento hago prints
		qd = request.POST
		try:
			print qd.__getitem__("longitude")
			print qd.__getitem__("latitude")
			print qd.__getitem__("accuracy")
			print qd.__getitem__("codeword")
		except MultiValueDictKeyError:
			return HttpResponseBadRequest()

	elif request.method != "GET":
		return method_not_allowed(request)
	
	return render_to_response('checkin.html', {},
			context_instance=RequestContext(request))

#TODO
def profile(request, user):
	"""Devuelve la pagina de perfil del usuario loggeado y modifica el perfil si recibe un POST"""
	if request.method != "GET":
		return method_not_allowed(request)
	#if existe el usuario
	return render_to_response('profile.html', {'user': {'name':user, 'student': False, 'id':user}, 
					'classes': [{'id':'idclase1', 'name':'clase1'}, {'id':'idclase2', 'name':'clase2'}]
					},#pasar user info
			context_instance=RequestContext(request))
	#else 
	#return not_found(request)


#TODO
def profile_img(request, user):
	"""Devuelve la foto de perfil del usuario user"""
	return render_to_response('404.html', {},
		context_instance=RequestContext(request))


#TODO
def delete_class(request, idclass):
	"""Elimina una clase si lo solicita el usuario que la creo"""
	#Comprobar que esta la clase y que se puede borrar, si no informar del error
	print "delete!"
	return render_to_response('404.html', {},
		context_instance=RequestContext(request))

#TODO
def uncheck_class(request, idclass):
	"""El usuario que lo solicita deja de estar suscrito a esa clase(solo para seminarios)"""
	print "uncheck!"
	return render_to_response('404.html', {},
		context_instance=RequestContext(request))

action_class = {'delete': delete_class,
				'uncheck': uncheck_class,
				#'check': check_class,
}


def process_class(request, idclass):
	"""Procesa las peticiones sobre una clase o seminario"""
	if request.method == "POST":
		qd = request.POST
		try:
			action = qd.__getitem__("action")
			if action in action_class:
				return action_class[action](request, idclass)
		except MultiValueDictKeyError:
			pass
		return HttpResponseBadRequest()

	return render_to_response('404.html', {},
		context_instance=RequestContext(request))

def method_not_allowed(request):
	"""Devuelve una pagina indicando que el metodo no esta permitido"""
	return render_to_response('error.html', {'message': "M&eacutetodo " + request.method + 
						" no soportado en " + request.path},
						context_instance=RequestContext(request))
	#405 Method Not Allowed return HttpResponseNotAllowed(['GET'(, 'POST')]);

