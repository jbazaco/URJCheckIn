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

from models import UserProfile, ForumComment, Subject, ForumComment, CheckIn, Lesson, LessonComment
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from ajax_views_bridge import get_class_ctx, get_subject_ctx, get_checkin_ctx, get_forum_ctx, process_profile_post, get_profile_ctx, get_subjects_ctx, process_class_post, get_seminars_ctx, process_seminars_post, process_subject_post, get_subject_attendance_ctx

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
		resp = process_class_post(request, form, idclass)
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
def forum(request):
	"""Devuelve el contenido de la pagina del foro"""
	if request.method == "GET":
		ctx = get_forum_ctx(request)
		html = loader.get_template('forum.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/forum'})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')#quitar POSTs si son por defecto
@login_required
def publish_forum(request, comment):
	""" procesa un check in"""
	if request.method == "POST":
		comment = comment[:150]
		new_comment = ForumComment(comment=comment, user=request.user)
		new_comment.save()
		html = loader.get_template('pieces/comments.html').render(RequestContext(
												request, {'comments': [new_comment]}))
		return simplejson.dumps({'ok': True, 'comment': html, 'idcomment': new_comment.id})
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
	"""Devuelve una pagina indicando el error que se le pasa"""
	templ = loader.get_template('error.html')
	cont = RequestContext(request, {'message':error})
	html = templ.render(cont)
	return simplejson.dumps({'#mainbody':html, 'url':url})


def wrongMethodJson(request):
	"""Devuelve una pagina de error con un mensaje que indica que se ha utilizado
		un metodo equivocado"""
	return simplejson.dumps({'error':'Metodo ' + request.method + ' no soportado'})


########################################################
# Funciones para solicitar mas elementos de algun tipo #
########################################################

@dajaxice_register(method='GET')
@login_required
def more_comments(request, current, newer, idlesson):
	"""Si newer = True devuelve un fragmento html con 10 comentarios mas nuevos que num ordenados
		de mas nuevo a mas antiguo. Si newer = False los anteriores.
		Ademas indica si son newer y el id del mas reciente/mas antiguo (si no hay devuelve 0)
		Si idlesson es menor que 1 los coge del foro y si no de la lesson con id idlesson"""
	if current > 0:
		try:
			if idlesson > 0:
				comment = LessonComment.objects.get(id=current)
			else:
				comment = ForumComment.objects.get(id=current)
		except ForumComment.DoesNotExist:
			return  simplejson.dumps({'comments': [], 'idcomment': 0, 'newer': True})
		current_date = comment.date
	else: #Para el caso en el que no hubiese ningun mensaje en la pagina
		current_date = timezone.now() - timedelta(days=1)
		

	if idlesson > 0:
		try:
			lesson = Lesson.objects.get(id=idlesson)
			profile = request.user.userprofile
			if not lesson.subject in profile.subjects.all():#TODO PROBAR
				return  simplejson.dumps({'comments': [], 'idcomment': 0, 'newer': True})
		except (ForumComment.DoesNotExist, Lesson.DoesNotExist, UserProfile.DoesNotExist):
			return  simplejson.dumps({'comments': [], 'idcomment': 0, 'newer': True})
		all_comments = LessonComment.objects.filter(lesson=lesson)
	else:
		all_comments = ForumComment.objects.all()

	if newer:
		comments = all_comments.filter(date__gt=current_date).order_by('-date')
		#Se tiene que hacer asi porque si se hace el slice primero con order_by('date')
		# y luego se llama a reverse() se seleccionan los 10 elementos opuestos
		n_comments = comments.count()
		if n_comments > 10:
			comments = comments[n_comments-10:]
	else:
		comments = all_comments.filter(date__lt=current_date).order_by('-date')[0:10]
	if comments:
		if newer:
			idcomment = comments[0].id
		else:
			idcomment = comments[comments.count()-1].id
	else:
		idcomment = 0
	html = loader.get_template('pieces/comments.html').render(RequestContext(
												request, {'comments':comments}))
	return  simplejson.dumps({'comments':html, 'newer':newer, 
							'idcomment':idcomment, 'idlesson':idlesson})

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
	return  simplejson.dumps({'lessons': html, 'newer': newer, 'idlesson': idlesson})


