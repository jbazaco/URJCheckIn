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
	return render_to_response('main.html', {'htmlname': 'checkin.html'},
		context_instance=RequestContext(request))
