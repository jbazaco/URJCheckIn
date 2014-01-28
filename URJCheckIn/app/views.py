# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError

from forms import ReviewClassForm, ProfileEditionForm

#TODO comprobar que el usuario esta registrado antes de enviar una pagina
# y actuar en consecuencia


def not_found(request):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	return render_to_response('main.html', {'htmlname': '404.html'},	#mostrar en el html las paginas mas "frecuentes"
																	#checkin, inicio, perfil...
		context_instance=RequestContext(request))


def home(request):
	"""Devuelve la pagina de inicio"""
	if request.method != "GET":
		return method_not_allowed(request)
	
	return render_to_response('main.html', {'htmlname': 'home.html'},
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
	
	return render_to_response('main.html', {'htmlname': 'checkin.html'},
			context_instance=RequestContext(request))

#TODO
def profile(request, iduser):
	"""Devuelve la pagina de perfil del usuario loggeado y modifica el perfil si recibe un POST"""
	if request.method == "POST":
		#comprobar user = usuarioregistrado
		qd = request.POST
		try:
			#TODO con el resto de campos
			try:
				age = int(qd.__getitem__("age"))
			except ValueError:
				return HttpResponseBadRequest()
			print age
		except MultiValueDictKeyError:
			return HttpResponseBadRequest()

	elif request.method != "GET":
		return method_not_allowed(request)
	#if existe el usuario
	
	return render_to_response('main.html', {'htmlname': 'profile.html', 'user': {'name':iduser, 'student': False, 'id':iduser}, 
					'classes': [{'id':'idclase1', 'name':'clase1'}, {'id':'idclase2', 'name':'clase2'}],
					'form': ProfileEditionForm()
					},#pasar user info
			context_instance=RequestContext(request))
	#else 
	#return not_found(request)


#TODO
def profile_img(request, user):
	"""Devuelve la foto de perfil del usuario user"""
	return render_to_response('main.html', {'htmlname': '404.html'},
		context_instance=RequestContext(request))


#TODO
def delete_class(request, idclass):
	"""Elimina una clase si lo solicita el usuario que la creo"""
	#Comprobar que esta la clase y que se puede borrar, si no informar del error
	print "delete!"
	return render_to_response('main.html', {'htmlname': '404.html'},
		context_instance=RequestContext(request))

#TODO
def uncheck_class(request, idclass):
	"""El usuario que lo solicita deja de estar suscrito a esa clase(solo para seminarios)"""
	print "uncheck!"
	return render_to_response('main.html', {'htmlname': '404.html'},
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

	return render_to_response('main.html', {'htmlname': 'class.html','form': ReviewClassForm()},
		context_instance=RequestContext(request))


def method_not_allowed(request):
	"""Devuelve una pagina indicando que el metodo no esta permitido"""
	return render_to_response('error.html', {'message': "M&eacutetodo " + request.method + 
						" no soportado en " + request.path},
						context_instance=RequestContext(request))
	#405 Method Not Allowed return HttpResponseNotAllowed(['GET'(, 'POST')]);


def forum(request):
	"""Devuelve la pagina del foro y almacena comentarios nuevos"""
	if request.method == "POST":
		qd = request.POST
		try:
			comment = qd.__getitem__("comment")
		except MultiValueDictKeyError:
			return HttpResponseBadRequest()
		comment = comment[:150] #si el comentario tiene mas de 150 caracteres se corta
		print comment
	
	elif request.method != "GET":
		return method_not_allowed(request)

	return render_to_response('main.html', {'htmlname': 'forum.html',
				'comments':[
					{'user':{'id':'id1', 'name':'name1', 'surname1':'sur1', 'surname2':'sur2'}, 'content':'comentario 1'},
					{'user':{'id':'id2', 'name':'name2', 'surname1':'sur12', 'surname2':'sur22'}, 'content':'comentario 2'}
				]
				},
				context_instance=RequestContext(request))

def subjects(request):
	"""Devuelve la pagina con las asignaturas del usuario registrado"""
	return render_to_response('main.html', {'htmlname': 'subjects.html', 'subjects':[{'name':'subject1', 'id':'111'}, 
					{'name':'subject2', 'id':'222'}]}, context_instance=RequestContext(request))

def subject(request, idsubj):
	"""Devuelve la pagina con las clases de una asignatura"""
	return render_to_response('main.html', {'htmlname': 'subject.html','classes':[{'name':'class1', 'id':'111'}, 
					{'name':'class2', 'id':'222'}]}, context_instance=RequestContext(request))
