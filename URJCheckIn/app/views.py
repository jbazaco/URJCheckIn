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
from django.db import IntegrityError

WEEK_DAYS_BUT_SUNDAY = ['Lunes', 'Martes', 'Mi&eacute;rcoles', 'Jueves', 'Viernes', 'S&aacute;bado']

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

def not_found(request):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	if request.is_ajax():
		html = loader.get_template('404.html').render(RequestContext(request, {}))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', {'htmlname': '404.html'},
			context_instance=RequestContext(request))

def send_error_page(request, error):
	"""Devuelve una pagina de error"""
	if request.is_ajax():
		html = loader.get_template('error.html').render(RequestContext(request, {'message':error}))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', {'htmlname': 'error.html',
				'message': error}, context_instance=RequestContext(request))

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
	if request.is_ajax():
		html = loader.get_template('home.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


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
	if request.is_ajax():
		html = loader.get_template('checkin.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


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
			pform = ProfileEditionForm(request.POST)
			if not pform.is_valid():
				if request.is_ajax():
					return HttpResponse(json.dumps({'errors': pform.errors}), 
										content_type="application/json")
			else:
				data = pform.cleaned_data
				profile.age = data['age']
				profile.description = data['description']
				profile.save()
				if request.is_ajax():
					resp = {'user':{'age':data['age'], 'description':data['description']}}
					#coger datos del usuario tras guardar TODO cambiar esto y el js TODO
					return HttpResponse(json.dumps(resp), content_type="application/json")
		else:
			return send_error_page(request, 
						'Est&aacute;s intentando cambiar un perfil distinto del tuyo')

	ctx = {'profile': profile, 'form': ProfileEditionForm(), 'htmlname': 'profile.html'}
	if request.is_ajax():
		html = loader.get_template('profile.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	if request.method == "POST":
		if pform.errors:
			ctx['errors'] = pform.errors
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))

#TODO##########################################################
"""@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request, form):
	""Metodo de django.contrib.auth adaptado a ajax""
	if request.method == "POST":
		pform = PasswordChangeForm(user=request.user, data=form)
		if pform.is_valid():
			pform.save()
			return simplejson.dumps({'ok': True})
		else:
			return simplejson.dumps({'errors': pform.errors})
	else:
		return wrongMethodJson(request)
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import logout as auth_logout
@dajaxice_register(method='POST')
def logout(request):
	""Cierra sesion y devuelve el body y la url de la pagina /login""
	auth_logout(request)
	html = loader.get_template('registration/login_body.html').render(RequestContext(request, {}))
	return simplejson.dumps({'body': html, 'url': '/login'})
"""


#TODO
@login_required
def profile_img(request, user):
	"""Devuelve la foto de perfil del usuario user"""
	return render_to_response('main.html', {'htmlname': '404.html'},
		context_instance=RequestContext(request))


@login_required
def process_class(request, idclass):#TODO que solo se pueda comentar (editar y borrar en /class/id/edit)
	"""Procesa las peticiones sobre una clase o seminario"""
	if request.method == "POST":
		try:
			action = request.POST.__getitem__("action")
			if action in action_class:
				resp = action_class[action](request, request.POST, idclass)
				if request.is_ajax():
					return HttpResponse(json.dumps(resp), content_type="application/json")
			else:
				error = 'La acci&oacute;n que intentas realizar no existe'
				if request.is_ajax():
					return HttpResponse(json.dumps({'error': error}), content_type="application/json")
		except MultiValueDictKeyError:
			error = 'Formulario incorrecto'
			if request.is_ajax():
				return HttpResponse(json.dumps({'error': error}), content_type="application/json")
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
	try:
		lesson = Lesson.objects.get(id=idclass)
		try:
			profile = lesson.subject.userprofile_set.get(user=request.user)
		except UserProfile.DoesNotExist:
			return send_error_page(request, 'No est&aacutes matriculado en ' + str(lesson.subject))
		if (lesson.start_time > timezone.now()):
			lesson_state = 'sin realizar'
		elif (lesson.end_time < timezone.now()):
			try:
				lesson.checkin_set.get(user=request.user)
				lesson_state = 'asististe'
			except CheckIn.DoesNotExist:
				lesson_state = 'no asististe'
		else:
			lesson_state = 'imperti&eacute;ndose en este momento'
		all_comments = lesson.lessoncomment_set.all().order_by('-date')
		comments = my_paginator(request, all_comments, 10)
		profesors = lesson.subject.userprofile_set.filter(is_student=False)
		#En caso de que se asigne un profesor a una clase en vez de todos se obtendria de otra forma
	except Lesson.DoesNotExist:
		return send_error_page(request, '#404 La clase a la que intentas acceder no existe.')
	ctx = {'lesson':lesson, 'comments':comments, 'profile':profile, 
						'lesson_state':lesson_state, 'profesors':profesors}
	if  not profile.is_student and lesson_state != "sin realizar":
		opinions = lesson.checkin_set.filter(user__userprofile__is_student=True)
		ctx['opinions'] = opinions
	ctx['htmlname'] = 'class.html'
	if request.is_ajax():
		html = loader.get_template('class.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))

"""Funciones para procesar las clases"""
#TODO
def delete_class(request, form, idclass):
	"""Elimina una clase si lo solicita el usuario que la creo"""
	#Comprobar que esta la clase y que se puede borrar, si no informar del error
	print "delete!"
	return {'error': 'funcion sin hacer'}

def comment_class(request, form, idclass):
	"""Guarda un comentario de una clase"""
	try:
		comment = form.__getitem__("comment")
		comment = comment[:250]
	except MultiValueDictKeyError:
		return {'error': 'Formulario para comentar incorrecto'}

	try:
		lesson = Lesson.objects.get(id=idclass)
	except Lesson.DoesNotExist:
		return {'error': 'La clase en la que comentas no existe'}
	try:
		lesson.subject.userprofile_set.get(user=request.user)
	except UserProfile.DoesNotExist:
		return {'error': 'No tienes permisos para comentar en esta clase'}

	new_comment = LessonComment(comment=comment, user=request.user, lesson=lesson)
	new_comment.save()
	html = loader.get_template('pieces/comments.html').render(RequestContext(
												request, {'comments': [new_comment]}))
	return {'ok': True, 'comment': html, 'idcomment': new_comment.id, 'idlesson':idclass}

action_class = {'delete': delete_class,
				'comment': comment_class,
}


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
		qd = request.POST
		try:
			comment = qd.__getitem__("comment")
		except MultiValueDictKeyError:
			return HttpResponseBadRequest()
		comment = comment[:150] #si el comentario tiene mas de 150 caracteres se corta
		new_comment = ForumComment(comment=comment, user=request.user)
		new_comment.save()
		if request.is_ajax():
			html = loader.get_template('pieces/comments.html').render(RequestContext(
												request, {'comments': [new_comment]}))
			resp = {'ok': True, 'comment': html, 'idcomment': new_comment.id}
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
	if request.is_ajax():
		html = loader.get_template('forum.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


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
	if request.is_ajax():
		html = loader.get_template('subjects.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))
	

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
	if request.method == "POST":
		form = csform
	else:
		form = SubjectForm()
	ctx = {'profile':profile, 'seminars': future_seminars, 'form': form, 
			'htmlname': 'seminars.html'}
	if request.is_ajax():
		html = loader.get_template('seminars.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))

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
		if not subject.is_seminar:
			return send_error_page(request, 
					'La acci&oacute;n que intentas realizar solo se puede sobre seminarios.')
		
		now = timezone.now()
		today = datetime.date(now.year, now.month, now.day)
		if subject.first_date < today:
			error = 'No puedes modificar tu registro en un seminario que ya ha empezado'
			if request.is_ajax():
				return HttpResponse(json.dumps(resp), content_type="application/json")
		else:
			if subject in profile.subjects.all():
				profile.subjects.remove(subject)
				signed = False
			else:
				if profile.is_student:
					print subject.n_students()
					if subject.max_students <= subject.n_students():
						error = 'No hay plazas disponibles'
						if request.is_ajax():
							return HttpResponse(json.dumps({'error': error}), 
												content_type="application/json")
				if not error:
					profile.subjects.add(subject)
					signed = True
			if request.is_ajax():
				resp = {'signed': signed, 'is_student':profile.is_student, 'ok': True, 
						'iduser': request.user.id, 'name': request.user.first_name + " " + 
						request.user.last_name}
				return HttpResponse(json.dumps(resp), content_type="application/json")

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
	if request.is_ajax():
		html = loader.get_template('subject.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	if error:
		ctx['error'] = error
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))



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
				'name': student.user.first_name + ' ' + student.user.last_name})
		
	ctx = {'students': students_info, 'subject': subject, 'htmlname': 'subject_attendance.html'}
	if request.is_ajax():
		html = loader.get_template('subject_attendance.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


@login_required
def subject_edit(request, idsubj):
	"""Devuelve la pagina para editar/eliminar una asignatura y para crear nuevas
		clases"""
	if request.method != 'GET' and request.method != 'POST':
		return method_not_allowed(request)


	try:
		profile = request.user.userprofile
		if profile.is_student:
			return send_error_page(request, 'Solo los profesores tienen acceso.')
		subject = Subject.objects.get(id=idsubj)
		if not subject in profile.subjects.all():
			return send_error_page(request, 'No tienes acceso a esta informaci&oacute;n.')
	except UserProfile.DoesNotExist:
		return send_error_page(request, 'No tienes un perfil creado.')
	except Subject.DoesNotExist:
		return send_error_page(request, 'La asignatura con id ' + str(idsubj) + ' no existe.')


	errors = False
	if request.method == 'POST':
		pass #TODO#########################################
	
	
	form = SubjectForm(instance=subject)
	ctx = {'subject': subject, 'form': form, 'htmlname': 'subject_edit.html'}
	if request.is_ajax():
		html = loader.get_template('subject_edit.html').render(RequestContext(request, ctx))
		resp = {'#mainbody':html, 'url': request.get_full_path()}
		return HttpResponse(json.dumps(resp), content_type="application/json")
	return render_to_response('main.html', ctx, context_instance=RequestContext(request))


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
		current_date = timezone.now() - timedelta(days=1)
		

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

