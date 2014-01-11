# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError


#Devuelve una pagina que indica que la pagina solicitada no existe
def not_found(request):
	return render_to_response('main.html', {'htmlname': '404.html'},#mostrar en el html las paginas mas "frecuentes"
																	#checkin, inicio, perfil...
		context_instance=RequestContext(request))


#Devuelve la pagina de inicio
def home(request):
	if request.methos != "GET":
		return render_to_response('main.html', {'htmlname': 'error.html', 
						'message': "M&eacutetodo no soportado"},
						context_instance=RequestContext(request))
	
	return render_to_response('main.html', {'htmlname': 'home.html'},
		context_instance=RequestContext(request))


#Devuelve la pagina para hacer check in (GET) o procesa un check in (POST)
def checkin(request):
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
		return render_to_response('main.html', {'htmlname': 'error.html', 
						'message': "M&eacutetodo no soportado"},
						context_instance=RequestContext(request))
		#405 Method Not Allowed return HttpResponseNotAllowed(['GET', 'POST']);
	
	return render_to_response('main.html', {'htmlname': 'checkin.html'},
			context_instance=RequestContext(request))

