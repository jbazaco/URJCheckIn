
"""Estas funciones tienen el nombre get_XXXX_ctx y devuelven en un diccionario 
	el contexto para renderizar la plantilla XXXX.html o un diccionario {'error':'XXXX'}
	si se produce un error, siendo 'XXXX' un string describiendo el error"""
from models import UserProfile, Lesson, Subject
from django.utils import timezone

def get_class_ctx(request, idclass):
	"""Devuelve el contexto para la plantilla class.html"""
	#TODO a otro fichero en el que explique lo que devuelve
	try:
		lesson = Lesson.objects.get(id=idclass)
		try:
			profile = lesson.subject.userprofile_set.get(user=request.user)
		except UserProfile.DoesNotExist:
			return {'error': 'No est&aacutes matriculado en ' + lesson.subject}
		if (lesson.start_time > timezone.now()):
			lesson_state = 'sin realizar'
		elif (lesson.end_time < timezone.now()):
			try:
				lesson.checkin_set.get(user=request.user)
				lesson_state = 'asististe'
			except CheckIn.DoesNotExist:
				lesson_state = 'no asististe'
		else:
			lesson_state = 'imperti&eacute;ndose en este momento'#TODO comprobar tilde(safe)
		comments = lesson.lessoncomment_set.all().order_by('-date')
		profesors = lesson.subject.userprofile_set.filter(is_student=False)
		#En caso de que se asigne un profesor a una clase en vez de todos se obtendria de otra forma
	except Lesson.DoesNotExist:
		return {'error': '#404 La clase a la que intentas acceder no existe.'}
	return {'lesson':lesson, 'comments':comments, 'profile':profile, 
						'lesson_state':lesson_state, 'profesors':profesors}

def get_subject_ctx(request, idsubj):
	"""Devuelve el contexto para la plantilla class.html"""
	#TODO a otro fichero en el que explique lo que devuelve
	try:
		subject = Subject.objects.get(id=idsubj)
		try:
			profile = subject.userprofile_set.get(user=request.user)
		except UserProfile.DoesNotExist:
			return {'error': 'No est&aacutes matriculado en ' + subject}
		#TODO lessons = subject.lesson_set.filter(date__gte = start, date__lte = end)
		lessons = subject.lesson_set.all()#TODO cambiar por la linea anterior
		profesors = subject.userprofile_set.filter(is_student=False)
	except Subject.DoesNotExist:
		return {'error': '#404 La asignatura a la que intentas acceder no existe.'}
	return {'classes_f': lessons.filter(start_time__gt=timezone.now()),
			'classes_p': lessons.filter(end_time__lt=timezone.now()),
			'classes_n': lessons.filter(end_time__gt=timezone.now(), 
										start_time__lt=timezone.now()),
			'profesors': profesors, 'subject': subject}

