# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.debug import sensitive_post_parameters
from models import UserProfile, Lesson, Subject, CheckIn, LessonComment, ForumComment
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from forms import ProfileEditionForm, ReviewClassForm, SubjectForm, ExtraLessonForm
from dateutil import parser
from django.core.exceptions import ValidationError
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader, RequestContext
from django.contrib.auth.models import User
import json
from django.db import IntegrityError

WEEK_DAYS_BUT_SUNDAY = ['Lunes', 'Martes', 'Mi&eacute;rcoles', 'Jueves', 'Viernes', 'S&aacute;bado']

def ajax_required(funct):
	"""Decorator requiring an ajax request"""
	def wrap(request, *args, **kwargs):
		if not request.is_ajax():
			return HttpResponseBadRequest()
		return funct(request, *args, **kwargs)
	wrap.__doc__=funct.__doc__
	wrap.__name__=funct.__name__
	return wrap


def my_paginator(request, collection, n_elem):
	paginator = Paginator(collection, n_elem)
	page = request.GET.get('page')
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		#Si no es un entero devuelve la primera
		results = paginator.page(1)
	except EmptyPage:
		#Si no hay tantas paginas devuelve la ultima
		results = paginator.page(paginator.num_pages)
	return results

def response_ajax_or_not(request, ctx):
	"""Devuelve un HttpResponse con un objeto JSON con '#mainbody' el contenido de 
	ctx['htmlname'] y 'url' la url pedida si la peticion es ajax o la pagina main.html
	renderizada con el contexto ctx si no es ajax"""
	if request.is_ajax():
		html = loader.get_template(ctx['htmlname']).render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx,
			context_instance=RequestContext(request))

def not_found(request):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	return response_ajax_or_not(request, {'htmlname': '404.html'})

def send_error_page(request, error):
	"""Devuelve una pagina de error"""
	return response_ajax_or_not(request, {'htmlname': 'error.html', 'message': error})

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
		return send_error_page(request, 'No tienes un perfil creado.')

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
	return response_ajax_or_not(request, ctx)


def process_checkin(request):
	"""Procesa un formulario para hacer checkin y devuelve un diccionario con 'ok' = True 
		si se realiza con exito o con 'error' = mensaje_de_error si hay errores"""
	try:#TODO hacer form
		form = request.POST
		try:
			idsubj = form.__getitem__("subject")
		except ValueError:
			return {'error': 'Informacion de la asignatura incorrecta.'}
		try:
			profile = UserProfile.objects.get(user=request.user)
			subject = profile.subjects.get(id=idsubj)
			lesson = subject.lesson_set.get(start_time__lte=timezone.now(),
												end_time__gte=timezone.now())
		except UserProfile.DoesNotExist:
			return {'error': 'No tienes un perfil creado.'}
		except Subject.DoesNotExist:
			return {'error': 'No estas matriculado en esa asignatura.'}
		except Lesson.DoesNotExist:
			return {'error': 'Ahora no hay ninguna clase de la asignatura ' + str(subject)}
		except Lesson.MultipleObjectsReturned:
			return {'error': 'Actualmente hay dos clases de ' + str(subject) + 
								', por favor, contacte con un administrador'}
		print form.__getitem__("longitude")
		print form.__getitem__("latitude")
		print form.__getitem__("accuracy")
		print form.__getitem__("codeword")
		try:
			mark = form.__getitem__("id_mark")
		except KeyError:
			mark = 3
		try:
			comment = form.__getitem__("id_comment")
		except KeyError:
			comment = ""
		checkin = CheckIn(user=request.user, lesson=lesson, mark=mark,comment=comment)
	except KeyError:
		return {'error': 'Formulario incorrecto.'}
	try:
		checkin.save()
	except IntegrityError:
		return {'error': 'Ya habias realizado el checkin para esta clase.'}
	return {'ok': True}

@login_required
def checkin(request):
	"""Devuelve la pagina para hacer check in y procesa un checkin si recibe un POST"""
	if request.method == "POST":
		resp = process_checkin(request)
		if request.is_ajax():
			return HttpResponse(json.dumps(resp), content_type="application/json")
	elif request.method != "GET":
		return method_not_allowed(request)

	try:
		profile = request.user.userprofile
	except UserProfile.DoesNotExist:
		return send_error_page(request, 'No tienes un perfil creado.')
	
	subjects = profile.subjects.all()
	ctx = {'htmlname': 'checkin.html', 'form': ReviewClassForm(), 'profile':profile, 
			'subjects':subjects}
	if request.method == "POST":
		if 'error' in resp:
			ctx['error'] = resp['error']
	return response_ajax_or_not(request, ctx)


@login_required
def profile(request, iduser):
	"""Devuelve la pagina de perfil del usuario loggeado y modifica el perfil si recibe un POST"""
	if request.method != "GET" and request.method != "POST":
		return method_not_allowed(request)

	try:
		profile = UserProfile.objects.get(user=iduser)
	except UserProfile.DoesNotExist:			
		return send_error_page(request, 'El usuario con id ' + iduser + ' no tiene perfil')

	if request.method == "POST":
		if iduser == str(request.user.id):
			pform = ProfileEditionForm(request.POST, instance=profile)
			if not pform.is_valid():
				if request.is_ajax():
					return HttpResponse(json.dumps({'errors': pform.errors}), 
										content_type="application/json")
				else:
					#si no lo obtengo de nuevo cuando renderice con
					# profile puede aparecer mal la edad
					profile = UserProfile.objects.get(user=iduser)
			else:
				pform.save()
				if request.is_ajax():
					resp = {'user': {'age': profile.age, 'description': profile.description}}
					return HttpResponse(json.dumps(resp), content_type="application/json")
		else:
			return send_error_page(request, 
						'Est&aacute;s intentando cambiar un perfil distinto del tuyo')
	if request.method != "POST":#si es un POST coge el form que ha recibido
		pform = ProfileEditionForm(instance=profile)

	ctx = {'profile': profile, 'form': pform, 'htmlname': 'profile.html'}
	return response_ajax_or_not(request, ctx)


@sensitive_post_parameters()
@login_required
@ajax_required
def password_change(request):
	"""Metodo de django.contrib.auth adaptado a ajax"""
	if request.method == "POST":
		pform = PasswordChangeForm(user=request.user, data=request.POST)
		if pform.is_valid():
			pform.save()
			return HttpResponse(json.dumps({'ok': True}), content_type="application/json")
		else:
			return HttpResponse(json.dumps({'errors': pform.errors}), content_type="application/json")
	else:
		return method_not_allowed(request)


@login_required
def my_logout(request):
	"""Cierra sesion"""
	resp = logout(request)
	if request.is_ajax():
		if resp.status_code == 200:
			html = loader.get_template('registration/login_body.html').render(
												RequestContext(request, {}))
			ajax_resp = {'body': html, 'url': '/login'}
			return HttpResponse(json.dumps(ajax_resp), content_type="application/json")
	return resp


#TODO
@login_required
def profile_img(request, user):
	"""Devuelve la foto de perfil del usuario user"""
	return render_to_response('main.html', {'htmlname': '404.html'},
		context_instance=RequestContext(request))


@login_required
def process_class(request, idclass):
	"""Procesa las peticiones sobre una clase y guarda un LessonComment si recibe un POST"""
	if request.method != "GET" and request.method != "POST":
		return method_not_allowed(request)

	try:
		lesson = Lesson.objects.get(id=idclass)
		profile = lesson.subject.userprofile_set.get(user=request.user)
	except Lesson.DoesNotExist:
		return send_error_page(request, 'La clase a la que intentas acceder no existe.')
	except UserProfile.DoesNotExist:
		return send_error_page(request, 'No est&aacutes matriculado en ' + str(lesson.subject))

	if request.method == "POST":
		if profile.is_student:
			return send_error_page(request, 'Solo los profesores pueden comentar en las clases')
		resp = save_lesson_comment(request, lesson)
		if request.is_ajax():
			return HttpResponse(json.dumps(resp), content_type="application/json")

	#Para el caso en el que pida mas comentarios con ajax
	if request.is_ajax():
		if request.GET.get('idlesson') and request.GET.get('newer') and request.GET.get('idcomment'):
			try:
				return more_comments(request, int(request.GET.get('idcomment')), 
								request.GET.get('newer') == 'true',
								 int(request.GET.get('idlesson')))
			except ValueError:
				pass
	
	lesson_state = lesson_str_state(lesson, request.user)
	comments = my_paginator(request, lesson.lessoncomment_set.all().order_by('-date'), 10)
	profesors = lesson.subject.userprofile_set.filter(is_student=False)
	
	ctx = {'lesson':lesson, 'comments':comments, 'profile':profile, 'lesson_state':lesson_state,
			'profesors':profesors, 'subject': lesson.subject, 'htmlname': 'class.html'}
	if not profile.is_student and lesson_state != "sin realizar":
		opinions = lesson.checkin_set.filter(user__userprofile__is_student=True)
		ctx['opinions'] = opinions
	return response_ajax_or_not(request, ctx)


@login_required
def save_lesson_comment(request, lesson):
	"""Guarda un LessonComment con la informacion del formulario recibido para la clase lesson y 
		el usuario request.user y devuelve un diccionario con un ok = True si la peticion no es ajax
		o la respuesta para una peticion ajax. O con error = mensaje de error si se produce un error"""
	try:
		comment = request.POST.__getitem__("comment")
	except MultiValueDictKeyError:
		return {'error': 'Formulario para comentar incorrecto'}
	comment = comment[:250]
	new_comment = LessonComment(comment=comment, user=request.user, lesson=lesson)
	new_comment.save()
	if request.is_ajax():
		html = loader.get_template('pieces/comments.html').render(RequestContext(
												request, {'comments': [new_comment]}))
		return {'ok': True, 'comment': html, 'idcomment': new_comment.id, 'idlesson':lesson.id}
	else:
		return {'ok': True}
	


def lesson_str_state(lesson, user):#TODO poner tambien si no fue el profesor
	"""Devuelve un string indicando el estado de la clase o si asististe o no si ya
		se ha realizado la clase"""
	if (lesson.start_time > timezone.now()):
		return 'sin realizar'
	elif (lesson.end_time < timezone.now()):
		try:
			lesson.checkin_set.get(user=user)
			return 'asististe'
		except CheckIn.DoesNotExist:
			return 'no asististe'
	else:
		return 'imperti&eacute;ndose en este momento'

def method_not_allowed(request):
	"""Devuelve una pagina indicando que el metodo no esta permitido"""
	if request.is_ajax():
		resp = {'error': 'Metodo ' + request.method + ' no soportado'}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('error.html', {'message': "M&eacutetodo " + request.method + 
						" no soportado en " + request.path},
						context_instance=RequestContext(request))
	#405 Method Not Allowed return HttpResponseNotAllowed(['GET'(, 'POST')]);

@login_required
def forum(request):
	"""Devuelve la pagina del foro y almacena comentarios nuevos"""
	if request.method == "POST":
		resp = save_forum_comment(request)
		if request.is_ajax():
			return HttpResponse(json.dumps(resp), content_type="application/json")
	elif request.method != "GET":
		return method_not_allowed(request)

	#Para el caso en el que pida mas comentarios con ajax
	if request.is_ajax():
		if request.GET.get('idlesson') and request.GET.get('newer') and request.GET.get('idcomment'):
			try:
				return more_comments(request, int(request.GET.get('idcomment')), 
								request.GET.get('newer') == 'true',
								 int(request.GET.get('idlesson')))
			except ValueError:
				pass

	comments =  ForumComment.objects.all().order_by('-date')
	ctx = {'comments': my_paginator(request, comments, 10), 'htmlname': 'forum.html'}
	return response_ajax_or_not(request, ctx)


@login_required
def save_forum_comment(request):
	"""Guarda un ForumComment del usuario request.user con la informacion del formulario recibido 
		y devuelve un diccionario con un ok = True si la peticion no es ajax o la respuesta para 
		una peticion ajax. O con error = mensaje de error si se produce un error"""
	try:
		comment = request.POST.__getitem__("comment")
	except MultiValueDictKeyError:
		return {'error': 'Formulario para comentar incorrecto'}
	comment = comment[:150] #si el comentario tiene mas de 150 caracteres se corta
	new_comment = ForumComment(comment=comment, user=request.user)
	new_comment.save()
	if request.is_ajax():
		html = loader.get_template('pieces/comments.html').render(RequestContext(
											request, {'comments': [new_comment]}))
		return {'ok': True, 'comment': html, 'idcomment': new_comment.id}
	else:
		return {'ok': True}


@login_required
def subjects(request):
	"""Devuelve la pagina con las asignaturas del usuario registrado"""
	if request.method != 'GET':
		return method_not_allowed(request)

	try:
		profile = UserProfile.objects.get(user=request.user)
	except UserProfile.DoesNotExist:			
		return send_error_page(request, 'No tienes un perfil creado.')
	subjects = profile.subjects.all()
	ctx = {'subjects':subjects.filter(is_seminar=False), 
			'seminars':subjects.filter(is_seminar=True), 'htmlname': 'subjects.html'}
	return response_ajax_or_not(request, ctx)
	

@login_required
def seminars(request):
	"""Devuelve la pagina con las asignaturas del usuario registrado"""
	if request.method != "GET" and request.method != "POST":
		return method_not_allowed(request)

	try:
		profile = request.user.userprofile
	except UserProfile.DoesNotExist:			
		return send_error_page(request, 'No tienes un perfil creado.')

	errors = False
	if request.method == "POST":
		if profile.is_student:
			return send_error_page(request, 'Los estudiantes no pueden crear seminarios')

		subj = Subject(is_seminar=True)
		csform = SubjectForm(request.POST, instance=subj)
		if not csform.is_valid():
			if request.is_ajax():
				return HttpResponse(json.dumps({'errors': csform.errors}), 
									content_type="application/json")
		else:
			new_subj = csform.save()
			profile.subjects.add(new_subj)
			if request.is_ajax():
				return HttpResponse(json.dumps({'idsubj': new_subj.id}), content_type="application/json")
			return HttpResponseRedirect('/subjects/' + str(new_subj.id))

	future_seminars = Subject.objects.filter(
						is_seminar=True		
					).filter(
						first_date__gt = timezone.now()
					).filter(
						degrees__in = profile.degrees.all()
					).distinct().order_by('first_date')
	if request.method != "POST":
		csform = SubjectForm()
	ctx = {'profile':profile, 'seminars': future_seminars, 'form': csform, 
			'htmlname': 'seminars.html'}
	return response_ajax_or_not(request, ctx)

@login_required
def subject(request, idsubj):
	"""Devuelve la pagina con la informacion y las clases de una asignatura"""
	if request.method != 'GET' and request.method != 'POST':
		return method_not_allowed(request)

	try:
		profile = UserProfile.objects.get(user=request.user)
		subject = Subject.objects.get(id=idsubj)
	except UserProfile.DoesNotExist:
		return send_error_page(request, 'No tienes un perfil creado.')
	except Subject.DoesNotExist:
		return send_error_page(request, '#404 La asignatura a la que intentas acceder no existe.')

	error = False
	if request.method == 'POST':
		resp = sign_in_seminar(request, subject, profile)
		if request.is_ajax():
			return HttpResponse(json.dumps(resp), content_type="application/json")
		elif 'error' in resp:
			error = resp['error']

	#Para el caso en el que pida mas comentarios con ajax
	if request.is_ajax():
		if request.GET.get('idlesson') and request.GET.get('newer'):
			try:
				return more_lessons(request, int(request.GET.get('idlesson')), 
									request.GET.get('newer') == 'true')
			except ValueError:
				pass

	if subject in profile.subjects.all():
		signed = True
	else:
		signed = False
		#Solo pueden ver las asignaturas en las que estan matriculados
		if not subject.is_seminar:
			return send_error_page(request, 'No est&aacutes matriculado en ' + str(subject))
		
	lessons = subject.lesson_set.all()
	profesors = subject.userprofile_set.filter(is_student=False)
	now = timezone.now()
	today = datetime.date(now.year, now.month, now.day)
	started = subject.first_date < today#Si ha empezado True
	classes_f = my_paginator(request, 
				lessons.filter(start_time__gte=timezone.now()).order_by('end_time'),
				10)
	classes_p = my_paginator(request,
				lessons.filter(end_time__lte=timezone.now()).order_by('-start_time'),
				10)
	ctx = {'classes_f': classes_f, 'classes_p': classes_p,
			'classes_n': lessons.filter(end_time__gt=timezone.now(), 
										start_time__lt=timezone.now()),
			'profesors': profesors, 'subject': subject, 'profile':profile,
			'signed': signed, 'started': started, 'htmlname': 'subject.html'}
	if error:
		ctx['error'] = error
	return response_ajax_or_not(request, ctx)


@login_required
def sign_in_seminar(request, subject, profile):
	"""Te apunta a un seminario (si no estas apuntado) o te desapunta en caso contrario
		Devuelve un diccionario con error = error si ocurre un error o un ok = True si la
		peticion no es ajax o el diccionario para crear el objeto json para responder
		si la peticion es ajax"""
	if not subject.is_seminar:
		return {'error': 'La acci&oacute;n que intentas realizar solo se puede sobre seminarios.'}
	now = timezone.now()
	today = datetime.date(now.year, now.month, now.day)
	if subject.first_date < today:
		return {'error': 'No puedes modificar tu registro en un seminario que ya ha empezado'}
	else:
		if subject in profile.subjects.all():
			profile.subjects.remove(subject)
			signed = False
		else:
			if profile.is_student:
				if subject.max_students <= subject.n_students():
					return {'error': 'No hay plazas disponibles'}
			profile.subjects.add(subject)
			signed = True
		if request.is_ajax():
			return {'signed': signed, 'is_student':profile.is_student, 'ok': True, 
					'iduser': request.user.id, 'name': request.user.first_name + " " + 
					request.user.last_name}
		else:
			return {'ok': True}


@login_required
def subject_attendance(request, idsubj):
	"""Devuelve la pagina con la informacion y las clases de una asignatura"""
	if request.method != 'GET':
		return method_not_allowed(request)

	try:
		profile = request.user.userprofile
		if profile.is_student:
			send_error_page(request, 'Solo los profesores tienen acceso.')
		subject = Subject.objects.get(id=idsubj)
		if not subject in profile.subjects.all():
			return send_error_page(request, 'No tienes acceso a esta informaci&oacute;n.')
	except UserProfile.DoesNotExist:
		return send_error_page(request, 'No tienes un perfil creado.')
	except Subject.DoesNotExist:
		return send_error_page(request, 'La asignatura con id ' + str(idsubj) + ' no existe.')
	
	students = subject.userprofile_set.filter(is_student=True)
	lessons = subject.lesson_set.filter(end_time__lte = timezone.now())
	n_lessons = lessons.count()
	checkins = CheckIn.objects.filter(lesson__in = lessons)
	students_info = []
	for student in students:
		if n_lessons > 0:
			n_checkins = checkins.filter(user=student.user).count()
			percent = round(100.0 * n_checkins / n_lessons,2)
		else:
			percent = 0
		students_info.append({'id': student.user.id, 'percent': percent,
				'name': student.user.first_name + ' ' + student.user.last_name,
				'dni': student.dni})
		
	ctx = {'students': students_info, 'subject': subject, 'htmlname': 'subject_attendance.html'}
	return response_ajax_or_not(request, ctx)


@login_required
def subject_edit(request, idsubj):
	"""Devuelve la pagina para editar o eliminar una asignatura"""
	if request.method != 'GET' and request.method != 'POST':
		return method_not_allowed(request)

	try:
		subject = Subject.objects.get(id=idsubj)
		if subject.creator != request.user:
			return send_error_page(request, 'Solo el creador de la asignatura puede editarla.')
	except Subject.DoesNotExist:
		return send_error_page(request, 'La asignatura con id ' + str(idsubj) + ' no existe.')

	if request.method == 'POST':
		if request.POST.get("action", default='edit') == 'delete':
			subject.delete()
			if request.is_ajax():
				return HttpResponse(json.dumps({'deleted': True, 'redirect': '/subjects'}),
									content_type="application/json")
			return HttpResponseRedirect('/subjects')

		sform = SubjectForm(request.POST, instance=subject)
		if not sform.is_valid():
			if request.is_ajax():
				return HttpResponse(json.dumps({'errors': sform.errors}), 
									content_type="application/json")
		else:
			sform.save()
			if request.is_ajax():
				return HttpResponse(json.dumps({'ok': True}), content_type="application/json")
	
	if request.method != 'POST':
		sform = SubjectForm(instance=subject)
	ctx = {'subject': subject, 'form': sform, 'htmlname': 'subject_edit.html'}
	return response_ajax_or_not(request, ctx)


@login_required
def create_class(request, idsubj):
	"""Devuelve la pagina para crear una clase"""
	if request.method != 'GET' and request.method != 'POST':
		return method_not_allowed(request)

	try:
		profile = request.user.userprofile
		if profile.is_student:
			return send_error_page(request, 'Solo los profesores tienen acceso.')
		subject = profile.subjects.get(id=idsubj)
	except UserProfile.DoesNotExist:
		return send_error_page(request, 'No tienes un perfil creado.')
	except Subject.DoesNotExist:
		return send_error_page(request, 'No eres profesor de la asignatura con id ' + str(idsubj))

	if request.method == 'POST':
		lesson = Lesson(is_extra=True, subject=subject)
		lform = ExtraLessonForm(request.POST, instance=lesson)
		if not lform.is_valid():
			if request.is_ajax():
				return HttpResponse(json.dumps({'errors': lform.errors}), 
									content_type="application/json")
		else:
			lesson = lform.save()
			if request.is_ajax():
				return HttpResponse(json.dumps({'ok': True, 'redirect': '/class/' + str(lesson.id)}), 
									content_type="application/json")
			return HttpResponseRedirect('/class/' + str(lesson.id))
	
	if request.method != 'POST':
		lform = ExtraLessonForm()
	ctx = {'subject': subject, 'form': lform, 'htmlname': 'new_class.html'}
	return response_ajax_or_not(request, ctx)


def edit_class(request, idlesson):
	"""Devuelve la pagina para editar o eliminar una clase"""
	if request.method != 'GET' and request.method != 'POST':
		return method_not_allowed(request)

	try:
		profile = request.user.userprofile
		if profile.is_student:
			return send_error_page(request, 'Solo los profesores tienen acceso.')
		lesson = Lesson.objects.get(id=idlesson)
		if lesson.start_time < timezone.now():
			return send_error_page(request, 'No se pueden editar clases antiguas.')
		if lesson.subject not in profile.subjects.all():
			return send_error_page(request, 'Tienes que ser profesor de la asignatura para editarla.')
	except UserProfile.DoesNotExist:
		return send_error_page(request, 'No tienes un perfil creado.')
	except Lesson.DoesNotExist:
		return send_error_page(request, 'No existe ninguna clase con id ' + str(idlesson))

	if request.method == 'POST':
		if request.POST.get("action", default='edit') == 'delete':
			if lesson.is_extra:
				url_redirect = '/subjects/' + str(lesson.subject.id)
				lesson.delete()
				if request.is_ajax():
					return HttpResponse(json.dumps({'deleted': True, 'redirect': url_redirect}),
										content_type="application/json")
				return HttpResponseRedirect(url_redirect)
			else:
				return send_error_page(request, 'Solo se pueden eliminar clases extras')

		lform = ExtraLessonForm(request.POST, instance=lesson)
		if not lform.is_valid():
			if request.is_ajax():
				return HttpResponse(json.dumps({'errors': lform.errors}), 
									content_type="application/json")
		else:
			lform.save()
			if request.is_ajax():
				return HttpResponse(json.dumps({'ok': True}), content_type="application/json")
	
	if request.method != 'POST':
		lform = ExtraLessonForm(instance=lesson)
	print lesson.is_extra
	ctx = {'lesson': lesson, 'form': lform, 'htmlname': 'class_edit.html'}
	return response_ajax_or_not(request, ctx)

########################################################
# Funciones para solicitar mas elementos de algun tipo #
########################################################

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
		except (ForumComment.DoesNotExist, LessonComment.DoesNotExist):
			resp = {'comments': [], 'idcomment': 0, 'newer': True}
			return HttpResponse(json.dumps(resp), content_type="application/json")
		current_date = comment.date
	else: #Para el caso en el que no hubiese ningun mensaje en la pagina
		current_date = timezone.now() - datetime.timedelta(days=1)
		

	if idlesson > 0:
		try:
			lesson = Lesson.objects.get(id=idlesson)
			profile = request.user.userprofile
			if not lesson.subject in profile.subjects.all():
				resp = {'comments': [], 'idcomment': 0, 'newer': True}
				return HttpResponse(json.dumps(resp), content_type="application/json")
		except (ForumComment.DoesNotExist, Lesson.DoesNotExist, UserProfile.DoesNotExist):
			resp = {'comments': [], 'idcomment': 0, 'newer': True}
			return HttpResponse(json.dumps(resp), content_type="application/json")
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
	resp = {'comments':html, 'newer':newer, 'idcomment':idcomment, 'idlesson':idlesson}
	return HttpResponse(json.dumps(resp), content_type="application/json")


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
	resp = {'lessons': html, 'newer': newer, 'idlesson': idlesson}
	return HttpResponse(json.dumps(resp), content_type="application/json")

