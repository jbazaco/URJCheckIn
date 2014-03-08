from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.template import loader, RequestContext
from forms import ReviewClassForm, ProfileEditionForm
from django.utils import timezone
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect

from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

from models import UserProfile, ForumComment, Subject, ForumComment, CheckIn, Lesson
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from ajax_views_bridge import get_class_ctx, get_subject_ctx, get_checkin_ctx, process_profile_post, get_profile_ctx, get_subjects_ctx, process_class_post, get_seminars_ctx, process_seminars_post

@dajaxice_register(method='GET')
@login_required
def profile(request, iduser):
	"""Devuelve el contenido de la pagina de perfil"""
	if request.method == "GET":
		ctx = get_profile_ctx(request, iduser)
		if ('error' in ctx):
			return send_error(request, ctx['error'], '/profile/view/'+iduser)
		html = loader.get_template('profile.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/profile/view/'+iduser})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')
@login_required
def update_profile(request, iduser, form):
	"""Modifica el perfil del usuario registrado"""
	if request.method == "POST":
		if iduser == str(request.user.id):
			return simplejson.dumps(process_profile_post(form, request.user))
		else:
			return simplejson.dumps({'errors': ['Estas intentando cambiar un perfil distinto del tuyo']})#TODO pone en el alert '0: Estas....'
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')
@login_required
def process_class(request, form, idclass):#TODO mirar el campo class del form
	if request.method == "POST":
		resp = process_class_post(form, request.user, idclass)
		return simplejson.dumps(resp)
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def checkin(request):
	"""Devuelve la pagina para hacer check in"""
	if request.method == "GET":
		ctx = get_checkin_ctx(request)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/checkin")
		html = loader.get_template('checkin.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/checkin'})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='POST')
@login_required
def process_checkin(request, form):
	""" procesa un check in"""
	if request.method == "POST":
		try:
			try:
				idsubj = int(form["idsubj"])
			except ValueError:
				return simplejson.dumps({'error':'Informacion de la asignatura incorrecta.'})
			try:
				profile = UserProfile.objects.get(user=request.user)
				subject = profile.subjects.get(id=idsubj)
				lesson = subject.lesson_set.get(start_time__lte=timezone.now(),
													end_time__gte=timezone.now())
			except UserProfile.DoesNotExist:
				return simplejson.dumps({'error':'No tienes un perfil creado.'})
			except Subject.DoesNotExist:
				return simplejson.dumps({'error':'No estas matriculado en esa asignatura.'})
			except Lesson.DoesNotExist:
				return simplejson.dumps({'error':'Ahora no hay ninguna clase de la asignatura ' + 
										str(subject)})
			except Lesson.MultipleObjectsReturned:
				return simplejson.dumps({'error':'Actualmente hay dos clases de ' + 
						str(subject) + ', por favor, contacte con un administrador'})
			print form["longitude"]
			print form["latitude"]
			print form["accuracy"]
			print form["codeword"]
			checkin = CheckIn(user=request.user, lesson=lesson, mark=form["id_mark"],
								comment=form["id_comment"])
		except KeyError:
			return simplejson.dumps({'error': 'Formulario incorrecto.'})
		try:
			checkin.save()
		except IntegrityError:
			return simplejson.dumps({'error': 'Ya habias realizado el checkin para esta clase.'})
		return simplejson.dumps({'ok': True})
	else:
		return wrongMethodJson(request)

def wrongMethodJson(request):
	return simplejson.dumps({'error':'Metodo ' + request.method + ' no soportado'})

@dajaxice_register(method='GET')
@login_required
def subjects(request):
	"""Devuelve el contenido de la pagina de las asignaturas"""
	if request.method == "GET":
		ctx = get_subjects_ctx(request)
		if ('error' in ctx):
			return send_error(request, ctx['error'], '/subjects')
		html = loader.get_template('subjects.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects'})
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

#TODO una funcion que mande nuevos comentarios si hay nuevos y se sigue en la pagina
@dajaxice_register(method='GET')
@login_required
def forum(request):
	"""Devuelve el contenido de la pagina del foro"""
	if request.method == "GET":
		comments = ForumComment.objects.filter().order_by('-date')[:10]
		templ = loader.get_template('forum.html')
		cont = RequestContext(request, {'comments': comments})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/forum'})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')#quitar POSTs si son por defecto
@login_required
def publish_forum(request, comment):
	""" procesa un check in"""
	if request.method == "POST":
		comment = comment[:150]
		ForumComment(comment=comment, user=request.user).save()
		return simplejson.dumps({'ok': True})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='GET')
@login_required
def home(request):
	"""Devuelve la pagina para hacer check in"""
	if request.method == "GET":
		html = loader.get_template('home.html').render(RequestContext(request, {}))
		return simplejson.dumps({'#mainbody':html, 'url': '/'})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def not_found(request, path):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	html = loader.get_template('404.html').render(RequestContext(request, {}))
	return simplejson.dumps({'#mainbody':html, 'url': path})

@dajaxice_register(method='POST')
@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request, form):
	"""Metodo de django.contrib.auth adaptado a ajax"""
	if request.method == "POST":
		pform = PasswordChangeForm(user=request.user, data=form)
		if pform.is_valid():
			pform.save()
			return simplejson.dumps({'ok': True})
		else:
			return simplejson.dumps({'errors': pform.errors})
	else:
		return wrongMethodJson(request)


def send_error(request, error, url):
	templ = loader.get_template('error.html')
	cont = RequestContext(request, {'message':error})
	html = templ.render(cont)
	return simplejson.dumps({'#mainbody':html, 'url':url})
