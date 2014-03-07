# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from forms import ReviewClassForm, ProfileEditionForm
from models import UserProfile, ForumComment, Lesson, CheckIn
from django.contrib.auth.models import User

from ajax_views_bridge import get_class_ctx, get_subject_ctx, get_checkin_ctx, process_profile_post, get_profile_ctx, get_subjects_ctx, process_class_post, get_seminars_ctx

def not_found(request):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	return render_to_response('main.html', {'htmlname': '404.html'},	#mostrar en el html las paginas mas "frecuentes"
																	#checkin, inicio, perfil...
		context_instance=RequestContext(request))


@login_required
def home(request):#TODO tengo que hacer la pagina
	"""Devuelve la pagina de inicio"""
	if request.method != "GET":
		return method_not_allowed(request)
	
	return render_to_response('main.html', {'htmlname': 'home.html'},
		context_instance=RequestContext(request))

@login_required
def checkin(request):
	"""Devuelve la pagina para hacer check in, no procesa un checkin ya que la informacion enviada
		en el POST se genera con javascript y si hay javascript se realiza el POST con ajax"""
	if request.method != "GET":
		return method_not_allowed(request)

	ctx = get_checkin_ctx(request)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'checkin.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


@login_required
def profile(request, iduser):
	"""Devuelve la pagina de perfil del usuario loggeado y modifica el perfil si recibe un POST"""
	if request.method == "POST":
		if iduser == str(request.user.id):
			resp = process_profile_post(request.POST, request.user)
			if ('errors' in resp):
				return render_to_response('main.html', {'htmlname': 'error.html',
						'message': resp['errors']}, 
						context_instance=RequestContext(request))
		else:
			return render_to_response('main.html', {'htmlname': 'error.html',
					'message': 'Est&aacute;s intentando cambiar un perfil distinto del tuyo'}, 
					context_instance=RequestContext(request))

	elif request.method != "GET":
		return method_not_allowed(request)
	
	ctx = get_profile_ctx(request, iduser)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'profile.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


#TODO
@login_required
def profile_img(request, user):
	"""Devuelve la foto de perfil del usuario user"""
	return render_to_response('main.html', {'htmlname': '404.html'},
		context_instance=RequestContext(request))


@login_required
def process_class(request, idclass):
	"""Procesa las peticiones sobre una clase o seminario"""
	if request.method == "POST":
		resp = process_class_post(request.POST, request.user, idclass)
		if ('error' in resp):
			return render_to_response('main.html', {'htmlname': 'error.html',
					'message': resp['error']}, context_instance=RequestContext(request))
	
	ctx = get_class_ctx(request, idclass)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'class.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


def method_not_allowed(request):
	"""Devuelve una pagina indicando que el metodo no esta permitido"""
	return render_to_response('error.html', {'message': "M&eacutetodo " + request.method + 
						" no soportado en " + request.path},
						context_instance=RequestContext(request))
	#405 Method Not Allowed return HttpResponseNotAllowed(['GET'(, 'POST')]);

@login_required
def forum(request):
	"""Devuelve la pagina del foro y almacena comentarios nuevos"""
	if request.method == "POST":
		qd = request.POST
		try:
			comment = qd.__getitem__("comment")
		except MultiValueDictKeyError:
			return HttpResponseBadRequest()
		comment = comment[:150] #si el comentario tiene mas de 150 caracteres se corta
		ForumComment(comment=comment, user=request.user).save()
	elif request.method != "GET":
		return method_not_allowed(request)

	#TODO paginator si no hay javascript?
	comments = ForumComment.objects.filter().order_by('-date')[:10]
	return render_to_response('main.html', {'htmlname': 'forum.html',
				'comments':comments},
				context_instance=RequestContext(request))

@login_required
def subjects(request):
	"""Devuelve la pagina con las asignaturas del usuario registrado"""
	if request.method != 'GET':
		return method_not_allowed(request)

	ctx = get_subjects_ctx(request)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'subjects.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


@login_required
def seminars(request):
	"""Devuelve la pagina con las asignaturas del usuario registrado"""
	if request.method != 'GET':
		return method_not_allowed(request)

	ctx = get_seminars_ctx(request)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'seminars.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


@login_required
def subject(request, idsubj):
	"""Devuelve la pagina con la informacion y las clases de una asignatura"""
	if request.method != 'GET':
		return method_not_allowed(request)
	
	ctx = get_subject_ctx(request, idsubj)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'subject.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))

