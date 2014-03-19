from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.template import loader, RequestContext
from forms import ReviewClassForm, ProfileEditionForm
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect

from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from models import UserProfile, ForumComment, Subject, ForumComment, CheckIn, Lesson, LessonComment
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from ajax_views_bridge import get_class_ctx, get_subject_ctx, get_checkin_ctx, get_forum_ctx, process_profile_post, get_profile_ctx, get_subjects_ctx, process_class_post, get_seminars_ctx, process_seminars_post, process_subject_post, get_subject_attendance_ctx, get_home_ctx, get_subject_edit_ctx


@dajaxice_register(method='POST')
@login_required
def process_class(request, form, idclass):
	if request.method == "POST":
		resp = process_class_post(request, form, idclass)
		return simplejson.dumps(resp)
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def seminars(request):
	"""Devuelve el contenido de la pagina de los proximos seminarios"""
	if request.method == "GET":
		ctx = get_seminars_ctx(request)
		if ('error' in ctx):
			return send_error(request, ctx['error'], '/seminars')
		html = loader.get_template('seminars.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/seminars'})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='POST')#quitar POSTs si son por defecto
@login_required
def create_seminar(request, form):
	"""procesa la creacion de un seminario y devuelve la id del seminario creado"""
	if request.method == "POST":
		return simplejson.dumps(process_seminars_post(form, request.user))
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='POST')#quitar POSTs si son por defecto
@login_required
def changeSignSeminar(request, idsubj):
	"""procesa la creacion de un seminario y devuelve la id del seminario creado"""
	if request.method == "POST":
		return simplejson.dumps(process_subject_post(idsubj, request.user))
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='GET')
@login_required
def subject(request, idsubj):
	"""Devuelve el contenido de la pagina de la asignatura indicada en idsubj"""
	if request.method == "GET":
		ctx = get_subject_ctx(request, idsubj)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/subjects/"+str(idsubj))
		html = loader.get_template('subject.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects/'+str(idsubj)})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def subject_attendance(request, idsubj):
	"""Devuelve el contenido de la pagina de asistencia de la asignatura indicada en idsubj"""
	if request.method == "GET":
		ctx = get_subject_attendance_ctx(request, idsubj)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/subjects/"+str(idsubj)+"/attendance")
		html = loader.get_template('subject_attendance.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects/'+str(idsubj)+'/attendance'})
	else:
		return wrongMethodJson(request)

dajaxice_register(method='GET')
@login_required
def subject_edit(request, idsubj):
	"""Devuelve el contenido de la pagina de asistencia de la asignatura indicada en idsubj"""
	if request.method == "GET":
		ctx = get_subject_edit_ctx(request, idsubj)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/subjects/"+str(idsubj)+"/edit")
		html = loader.get_template('subject_edit.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects/'+str(idsubj)+'/edit'})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def class_info(request, idclass):
	"""Devuelve el contenido de la pagina de la clase indicada en idclass"""
	if request.method == "GET":
		ctx = get_class_ctx(request, idclass)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/class/"+str(idclass))
		html = loader.get_template('class.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/class/'+str(idclass)})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='GET')
@login_required
def home(request, week):
	"""Devuelve la pagina para hacer check in"""
	if request.method == "GET":
		try:
			n_week = int(week)
		except (TypeError, ValueError):
			n_week = 0
		ctx = get_home_ctx(request, n_week)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/")
		html = loader.get_template('home.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/?page=' + str(n_week)})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')
def logout(request):
	"""Cierra sesion y devuelve el body y la url de la pagina /login"""
	auth_logout(request)
	html = loader.get_template('registration/login_body.html').render(RequestContext(request, {}))
	return simplejson.dumps({'body': html, 'url': '/login'})


def wrongMethodJson(request):
	"""Devuelve una pagina de error con un mensaje que indica que se ha utilizado
		un metodo equivocado"""
	return simplejson.dumps({'error':'Metodo ' + request.method + ' no soportado'})


########################################################
# Funciones para solicitar mas elementos de algun tipo #
########################################################

@dajaxice_register(method='GET')
@login_required
def more_lessons(request, current, newer):
	"""Si newer = True devuelve un fragmento html con 10 clases posteriores a la lesson con
		id current ordenados de menor fecha a mayor fecha. Si newer = False las anteriores 
		ordenadas de mayor fecha a menos fecha.
		Ademas indica si son newer y el id de la ultima lesson que devuelve (si no hay 
		devuelve 0)"""
	try:
		lesson = Lesson.objects.get(id=current)
		subject = lesson.subject
	except Lesson.DoesNotExist:
		return simplejson.dumps({'lessons': [], 'newer': newer, 'idlesson': 0})
	#no tiene acceso a asignaturas que no tiene
	if not subject.is_seminar:
		try:
			profile = request.user.userprofile
		except UserProfile.DoesNotExist:
			return simplejson.dumps({'lessons': [], 'newer': newer, 'idlesson': 0})
		if not subject in profile.subjects.all():
			return simplejson.dumps({'lessons': [], 'newer': newer, 'idlesson': 0})

	all_lessons = Lesson.objects.filter(subject=subject.id)
	if newer:
		lessons = all_lessons.filter(end_time__gt=lesson.end_time).order_by('end_time')[0:10]
	else:
		lessons = all_lessons.filter(start_time__lt=lesson.start_time).order_by('-start_time')[0:10]
	if lessons:
		idlesson = lessons[lessons.count()-1].id
	else:
		idlesson = 0
	html = loader.get_template('pieces/lessons.html').render(RequestContext(
									request, {'lessons':lessons, 'future':newer}))
	return simplejson.dumps({'lessons': html, 'newer': newer, 'idlesson': idlesson})
