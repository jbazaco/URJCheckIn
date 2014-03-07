"""Las funciones con el nombre process_XXXX_post procesan los cambios de los post sobre 
	la pagina XXXX
	
	Las funciones con el nombre get_XXXX_ctx y devuelven en un diccionario 
	el contexto para renderizar la plantilla XXXX.html o un diccionario {'error':'XXXX'}
	si se produce un error, siendo 'XXXX' un string describiendo el error"""
from models import UserProfile, Lesson, Subject, CheckIn, LessonComment
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from forms import ProfileEditionForm, ReviewClassForm

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
		comments = lesson.lessoncomment_set.all().order_by('-date')
		profesors = lesson.subject.userprofile_set.filter(is_student=False)
		#En caso de que se asigne un profesor a una clase en vez de todos se obtendria de otra forma
	except Lesson.DoesNotExist:
		return {'error': '#404 La clase a la que intentas acceder no existe.'}
	return {'lesson':lesson, 'comments':comments, 'profile':profile, 
						'lesson_state':lesson_state, 'profesors':profesors}

def get_subject_ctx(request, idsubj):
	"""Devuelve el contexto para la plantilla class.html"""
	try:
		subject = Subject.objects.get(id=idsubj)
		try:
			profile = subject.userprofile_set.get(user=request.user)
		except UserProfile.DoesNotExist:
			return {'error': 'No est&aacutes matriculado en ' + subject}
		lessons = subject.lesson_set.all()
		profesors = subject.userprofile_set.filter(is_student=False)
	except Subject.DoesNotExist:
		return {'error': '#404 La asignatura a la que intentas acceder no existe.'}
	return {'classes_f': lessons.filter(start_time__gte=timezone.now()),
			'classes_p': lessons.filter(end_time__lte=timezone.now()).order_by('-start_time'),
			'classes_n': lessons.filter(end_time__gt=timezone.now(), 
										start_time__lt=timezone.now()),
			'profesors': profesors, 'subject': subject}

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
	except (UserProfile.DoesNotExist, User.DoesNotExist):			
		return {'error': 'No tienes un perfil creado.'}
	subjects = profile.subjects.all()
	return {'subjects':subjects.filter(is_seminar=False), 
			'seminars':subjects.filter(is_seminar=True)}

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

def process_class_post(form, user, idclass):
	"""Procesa un POST sobre una clase, pudiendo ser de diferentes tipos"""
	try:
		action = form.__getitem__("action")
		if action in action_class:
			return action_class[action](form, user, idclass)
	except MultiValueDictKeyError:
		pass
	return {'error': 'Formulario incorrecto'}

"""Funciones para procesar las clases"""
#TODO
def delete_class(form, user, idclass):
	"""Elimina una clase si lo solicita el usuario que la creo"""
	#Comprobar que esta la clase y que se puede borrar, si no informar del error
	print "delete!"
	return {'error': 'funcion sin hacer'}

#TODO
def uncheck_class(form, user, idclass):
	"""El usuario que lo solicita deja de estar suscrito a esa clase(solo para seminarios)"""
	print "uncheck!"
	return {'error': 'funcion sin hacer'}

def comment_class(form, user, idclass):
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
		lesson.subject.userprofile_set.get(user=user)
	except UserProfile.DoesNotExist:
		return {'error': 'No tienes permisos para comentar en esta clase'}

	LessonComment(comment=comment, user=user, lesson=lesson).save()
	return {'ok': True}

action_class = {'delete': delete_class,
				'uncheck': uncheck_class,
				'comment': comment_class,
				#'check': check_class,
}


