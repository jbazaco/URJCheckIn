# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext
from django.shortcuts import render_to_response


def notFound(request):
	return render_to_response('main.html', {'htmlname': '404.html'},
		context_instance=RequestContext(request))


def home(request):
	return render_to_response('main.html', {'htmlname': 'home.html'},
		context_instance=RequestContext(request))


def checkin(request):
	if request.method == "POST":
		#TODO guardar la informacion en la BD y procesarla si es necesario
		#de momento hago prints
		qd = request.POST
		print qd.__getitem__("longitude")
		print qd.__getitem__("latitude")
		print qd.__getitem__("accuracy")
		print qd.__getitem__("codeword")
	elif request.method != "GET":
		return render_to_response('main.html', {'htmlname': 'error.html', 
						'message': "M&eacutetodo no soportado"},
						context_instance=RequestContext(request))
	
	return render_to_response('main.html', {'htmlname': 'checkin.html'},
			context_instance=RequestContext(request))
