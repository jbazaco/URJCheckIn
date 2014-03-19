# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required

from models import UserProfile, Lesson, Subject, CheckIn, LessonComment, ForumComment
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from forms import ProfileEditionForm, ReviewClassForm, SubjectForm
from dateutil import parser
from django.core.exceptions import ValidationError
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader, RequestContext
from django.contrib.auth.models import User
import json

from ajax_views_bridge import get_class_ctx, get_subject_ctx, get_checkin_ctx,  get_forum_ctx, process_profile_post, get_profile_ctx, get_subjects_ctx, process_class_post, get_seminars_ctx, process_seminars_post, process_subject_post, get_subject_attendance_ctx, get_home_ctx, get_subject_edit_ctx, process_subject_edit_post

def not_found(request):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	return render_to_response('main.html', {'htmlname': '404.html'},	#mostrar en el html las paginas mas "frecuentes"
																	#checkin, inicio, perfil...
		context_instance=RequestContext(request))

def send_error(request, error):
	"""Devuelve una pagina de error"""
	if request.is_ajax():
		html = loader.get_template('error.html').render(RequestContext(request, {'message':error}))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', {'htmlname': 'error.html',
				'message': error}, context_instance=RequestContext(request))
	

WEEK_DAYS_BUT_SUNDAY = ['Lunes', 'Martes', 'Mi&eacute;rcoles', 'Jueves', 'Viernes', 'S&aacute;bado']

@login_required
def home(request):
	"""Devuelve la pagina de inicio"""
	if request.method != "GET":
		return method_not_allowed(request)
	try:
		week = int(request.GET.get('page'))
	except (TypeError, ValueError):
		week = 0

	try:
		profile = request.user.userprofile
	except UserProfile.DoesNotExist:
		return send_error(request, 'No tienes un perfil creado.')

	today = datetime.date.today()
	monday = today + datetime.timedelta(days= -today.weekday() + 7*week)
	events = []
	all_lessons = Lesson.objects.filter(subject__in=profile.subjects.all())
	for day in WEEK_DAYS_BUT_SUNDAY:
		date = monday + datetime.timedelta(days=WEEK_DAYS_BUT_SUNDAY.index(day))
		events.append({
						'day': day,
						'events': all_lessons.filter(
								start_time__year = date.year,
								start_time__month = date.month,
								start_time__day = date.day
							).order_by('start_time')
					})
	ctx = {'events': events, 'firstday':monday, 'lastday':monday + datetime.timedelta(days=7),
			'previous':week-1, 'next': week+1, 'htmlname': 'home.html'}
	if request.is_ajax():
		print request.get_full_path()
		html = loader.get_template('home.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")#TODO
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))

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
		resp = process_class_post(request, request.POST, idclass)
		if ('error' in resp):
			return render_to_response('main.html', {'htmlname': 'error.html',
					'message': resp['error']}, context_instance=RequestContext(request))
	elif request.method != "GET":
		return method_not_allowed(request)
	
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

	ctx = get_forum_ctx(request)
	ctx['htmlname'] = 'forum.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


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
	resp = False
	if request.method == "POST":
		resp = process_seminars_post(request.POST, request.user)
		if ('idsubj' in resp):
			idsubj = resp['idsubj']
			return HttpResponseRedirect('/subjects/' + str(idsubj))
		else:
			if ('errors' in resp):
				error = resp['errors']
			else:
				resp['errors'] = ["Se ha producido un error interno al crear el semianio"]
	elif request.method != "GET":
		return method_not_allowed(request)

	ctx = get_seminars_ctx(request)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'seminars.html'#Elemento necesario para renderizar main.html
	#resp es distinto de false si se recibio un POST erroneo y por tanto 
	#resp['errors'] contiene los errores
	if resp:
		ctx['errors'] = resp['errors']
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))

@login_required
def subject(request, idsubj):
	"""Devuelve la pagina con la informacion y las clases de una asignatura"""
	if request.method == 'POST':
		resp = process_subject_post(idsubj, request.user)
		if 'error' in resp:
			return render_to_response('main.html', {'htmlname': 'error.html',
					'message': resp['error']}, context_instance=RequestContext(request))
	elif request.method != 'GET':
		return method_not_allowed(request)
	
	ctx = get_subject_ctx(request, idsubj)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'subject.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


@login_required
def subject_attendance(request, idsubj):
	"""Devuelve la pagina con la informacion y las clases de una asignatura"""
	if request.method != 'GET':
		return method_not_allowed(request)
	
	ctx = get_subject_attendance_ctx(request, idsubj)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	ctx['htmlname'] = 'subject_attendance.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


@login_required
def subject_edit(request, idsubj):
	"""Devuelve la pagina para editar/eliminar una asignatura y para crear nuevas
		clases"""
	errors = False
	if request.method == 'POST':
		resp = process_subject_edit_post(request, request.POST, idsubj)
		if 'errors' in resp:
			errors = resp['errors']
	elif request.method != 'GET':
		return method_not_allowed(request)
	
	ctx = get_subject_edit_ctx(request, idsubj)
	if ('error' in ctx):
		return render_to_response('main.html', {'htmlname': 'error.html',
					'message': ctx['error']}, context_instance=RequestContext(request))
	if errors:
		ctx['errors'] = errors
	ctx['htmlname'] = 'subject_edit.html'#Elemento necesario para renderizar main.html
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


