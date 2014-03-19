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

from ajax_views_bridge import get_class_ctx, get_subject_ctx, get_checkin_ctx, process_class_post, get_seminars_ctx, process_seminars_post, process_subject_post, get_subject_attendance_ctx, get_subject_edit_ctx, process_subject_edit_post

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
		return wrongMethodJson(request)"""


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
	if request.is_ajax:
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

