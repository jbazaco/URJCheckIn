"""Las funciones con el nombre process_XXXX_post procesan los cambios de los post sobre 
	la pagina XXXX
	
	Las funciones con el nombre get_XXXX_ctx y devuelven en un diccionario 
	el contexto para renderizar la plantilla XXXX.html o un diccionario {'error':'XXXX'}
	si se produce un error, siendo 'XXXX' un string describiendo el error"""
from models import UserProfile, Lesson, Subject, CheckIn, LessonComment, ForumComment
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from forms import ProfileEditionForm, ReviewClassForm, CreateSeminarForm
from dateutil import parser
from django.core.exceptions import ValidationError
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader, RequestContext

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

def get_forum_ctx(request):
	"""Devuelve el contexto para la plantilla forum.html"""
	comments =  ForumComment.objects.all().order_by('-date')
	return {'comments': my_paginator(request, comments, 10) }

def get_class_ctx(request, idclass):
	"""Devuelve el contexto para la plantilla class.html"""
	try:
		lesson = Lesson.objects.get(id=idclass)
		try:
			profile = lesson.subject.userprofile_set.get(user=request.user)
		except UserProfile.DoesNotExist:
			return {'error': 'No est&aacutes matriculado en ' + str(lesson.subject)}
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
		return {'error': '#404 La clase a la que intentas acceder no existe.'}
	ctx = {'lesson':lesson, 'comments':comments, 'profile':profile, 
						'lesson_state':lesson_state, 'profesors':profesors}
	if  not profile.is_student and lesson_state != "sin realizar":
		opinions = lesson.checkin_set.filter(user__userprofile__is_student=True)
		ctx['opinions'] = opinions
	return ctx

def get_subject_ctx(request, idsubj):
	"""Devuelve el contexto para la plantilla subject.html"""
	try:
		profile = UserProfile.objects.get(user=request.user)
		subject = Subject.objects.get(id=idsubj)
	except UserProfile.DoesNotExist:
		return {'error': 'No tienes un perfil creado.'}
	except Subject.DoesNotExist:
		return {'error': '#404 La asignatura a la que intentas acceder no existe.'}


	if subject in profile.subjects.all():
		signed = True
	else:
		signed = False
		#Solo pueden ver las asignaturas en las que estan matriculados
		if not subject.is_seminar:
			return {'error': 'No est&aacutes matriculado en ' + str(subject)}
		
	lessons = subject.lesson_set.all()
	profesors = subject.userprofile_set.filter(is_student=False)
	now = timezone.now()
	today = datetime.date(now.year, now.month, now.day)
	started = subject.first_date < today#Si ha empezado True
	#TODO devolver solo 10 clases de cada
	return {'classes_f': lessons.filter(start_time__gte=timezone.now()),
			'classes_p': lessons.filter(end_time__lte=timezone.now()).order_by('-start_time'),
			'classes_n': lessons.filter(end_time__gt=timezone.now(), 
										start_time__lt=timezone.now()),
			'profesors': profesors, 'subject': subject, 'profile':profile,
			'signed': signed, 'started': started}

def get_subject_attendance_ctx(request, idsubj):
	"""Devuelve el contexto para la plantilla subject_attendance.html"""
	try:
		profile = request.user.userprofile
		if profile.is_student:
			return {'error': 'Solo los profesores tienen acceso.'}
		subject = Subject.objects.get(id=idsubj)
		if not subject in profile.subjects.all():
			return {'error': 'No tienes acceso a esta informaci&oacute;n.'}
	except UserProfile.DoesNotExist:
		return {'error': 'No tienes un perfil creado.'}
	except Subject.DoesNotExist:
		return {'error': 'La asignatura con id ' + str(idsubj) + ' no existe.'}
	
	students = subject.userprofile_set.filter(is_student=True)
	lessons = subject.lesson_set.filter(end_time__lte = timezone.now())
	n_lessons = lessons.count()
	checkins = CheckIn.objects.filter(lesson__in = lessons)
	students_info = []
	for student in students:
		n_checkins = checkins.filter(user=student.user).count()
		students_info.append({
					'id': student.id,
					'name': student.user.first_name + ' ' + student.user.last_name,
					'percent': round(100.0 * n_checkins / n_lessons,2)
		})
		
	return {'students': students_info, 'subject': subject}
	


def get_checkin_ctx(request):
	"""Devuelve el contexto para la plantilla class.html"""
	try:
		profile = request.user.userprofile
	except UserProfile.DoesNotExist:
		return {'error': 'No tienes un perfil creado.'}
	
	subjects = profile.subjects.all()
	return {'htmlname': 'checkin.html', 'form': ReviewClassForm(), 
			'profile':profile, 'subjects':subjects}

def get_profile_ctx(request, iduser):
	"""Devuelve el contexto para la plantilla profile.html"""
	try:
		profile = UserProfile.objects.get(user=iduser)
	except UserProfile.DoesNotExist:			
		return {'error': 'El usuario con id ' + iduser + ' no tiene perfil'}
	return {'profile': profile, 'form': ProfileEditionForm()}

def get_subjects_ctx(request):
	"""Devuelve el contexto para la plantilla subjects.html"""
	try:
		profile = UserProfile.objects.get(user=request.user)
	except UserProfile.DoesNotExist:			
		return {'error': 'No tienes un perfil creado.'}
	subjects = profile.subjects.all()
	return {'subjects':subjects.filter(is_seminar=False), 
			'seminars':subjects.filter(is_seminar=True)}

def get_seminars_ctx(request):
	"""Devuelve el contexto para la plantilla subjects.html"""
	try:
		profile = UserProfile.objects.get(user=request.user)
	except UserProfile.DoesNotExist:			
		return {'error': 'No tienes un perfil creado.'}
	future_seminars = Subject.objects.filter(
							is_seminar=True		
						).filter(
							first_date__gt = timezone.now()
						).filter(
							degrees__in = profile.degrees.all()
						).distinct().order_by('first_date')


	return {'profile':profile, 'seminars': future_seminars, 'form': CreateSeminarForm()}

def process_profile_post(form, user):
	"""Modifica el perfil del usuario user a partir de la informacion del formulario form"""
	pform = ProfileEditionForm(form)
	if not pform.is_valid():
		return {'errors': pform.errors}
	data = pform.cleaned_data
	try:
		profile = UserProfile.objects.get(user=user)
	except UserProfile.DoesNotExist:
		return {'errors': ['No tienes un perfil creado.']}#TODO Pone en el alert '0:No tienes...'
	profile.age = data['age']
	profile.description = data['description']
	profile.save()
	return {'user':{'id': user.id, 'age':data['age'], 'description':data['description']}}#coger datos del usuario tras guardar TODO cambiar esto y el js

def process_subject_post(idsubj, user):
	"""Pone un seminario en los subjects de un usuario o se lo quita si ya lo tiene"""
	try:
		profile = UserProfile.objects.get(user=user)
		subject = Subject.objects.get(id=idsubj, is_seminar=True)
	except UserProfile.DoesNotExist:
		return {'error': 'No tienes un perfil creado.'}
	except Subject.DoesNotExist:
		return {'error': 'No existe ning&uacute;n seminario con el id ' + str(idsubj)}

	now = timezone.now()
	today = datetime.date(now.year, now.month, now.day)
	if subject.first_date < today:
		return {'error': 'No puedes modificar tu registro en un seminario que ya ha empezado'}

	if subject in profile.subjects.all():
		profile.subjects.remove(subject)
		signed = False
	else:
		if profile.is_student:
			if subject.max_students >= subject.n_students:
				return {'error': 'No hay plazas disponibles'}
		profile.subjects.add(subject)
		signed = True
	return {'signed': signed, 'is_student':profile.is_student, 
			'ok': True, 'iduser': user.id, 
			'name': user.first_name + " " + user.last_name}


def process_seminars_post(form, user):
	"""Procesa un POST para la creacion de un seminario"""
	try:
		profile = UserProfile.objects.get(user=user)
		if profile.is_student:
			return {'errors': ['Los estudiantes no pueden crear seminarios']}
	except UserProfile.DoesNotExist:
		return {'errors': ['No tienes un perfil creado.']}
		
	#first_date = parser.parse(form.__getitem__("first_date"))
	csform = CreateSeminarForm(form)
	if not csform.is_valid():
		return {'errors': csform.errors}
	data = csform.cleaned_data
	new_subj = Subject(name=data['name'], is_seminar=True, 
					first_date=data['first_date'], last_date=data['last_date'],
					max_students=data['max_students'], description=data['description'],
					creator=user)
	try:
		new_subj.clean()#Save no lo llama, asi que hay que llamarlo
	except ValidationError, e:
		#TODO mostrar error sin el ['u'
		return {'errors': [str(e)]}
	new_subj.save()
	for degree in data['degrees']:
		new_subj.degrees.add(degree)
	profile.subjects.add(new_subj)
	return {'idsubj': new_subj.id}


def process_class_post(request, form, idclass):
	"""Procesa un POST sobre una clase, pudiendo ser de diferentes tipos"""
	try:
		action = form.__getitem__("action")
		if action in action_class:
			return action_class[action](request, form, idclass)
	except MultiValueDictKeyError:
		pass
	return {'error': 'Formulario incorrecto'}

"""Funciones para procesar las clases"""
#TODO
def delete_class(request, form, user, idclass):
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
				#'check': check_class,
}


