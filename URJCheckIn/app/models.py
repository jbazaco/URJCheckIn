from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

WEEK_DAYS = (
	('Mon', 'Monday'),
	('Tue', 'Tuesday'),
	('Wed', 'Wednesday'),
	('Thu', 'Thursday'),
	('Fri', 'Friday'),
	('Sat', 'Saturday'),
	('Sun', 'Sunday')
)

class Degree(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name='nombre')
	code = models.CharField(max_length=6, unique=True, verbose_name='codigo')

	class Meta:
		verbose_name='grado'

	def __unicode__(self):
		return self.code


class Subject(models.Model):
	name = models.CharField(max_length=100, verbose_name='nombre')
	degree = models.ForeignKey(Degree, verbose_name='grado')#TODO una asignatura/seminario para varios grados
	n_students = models.PositiveIntegerField(verbose_name='num. estudiantes', default=0)
	first_date = models.DateField(verbose_name='fecha de inicio')
	last_date = models.DateField(verbose_name='fecha de finalizacion')
	is_seminar = models.BooleanField(verbose_name='es seminario', default=False)

	class Meta:
		verbose_name = 'asignatura'
		unique_together = ("name", "degree")
	
	def __unicode__(self):
		return u"%s %s" % (self.name, self.degree)

	def clean(self):
		super(Subject, self).clean()
		if self.first_date and self.last_date:
			if (self.first_date > self.last_date):
				raise ValidationError('First_date can not be greater than last_date')


class Room(models.Model):
	room = models.CharField(max_length=20, verbose_name='aula')
	building = models.CharField(max_length=20, verbose_name='edificio')
	centre_longitude = models.IntegerField(verbose_name='centro longitud')
	centre_latitude = models.IntegerField(verbose_name='centro latitud')
	radius = models.IntegerField(verbose_name='radio')

	class Meta:
		verbose_name='aula'
		unique_together = ("room", "building")

	def __unicode__(self):
		return u"Aula %i" % (self.id)


class UserProfile(models.Model):
	user = models.OneToOneField(User, verbose_name='usuario')
	#TODO NIF Unique
	photo = models.ImageField(upload_to='profile_photos', blank=True)#Poner una por defecto (la tipica silueta)
	description = models.TextField(max_length=200, blank=True, verbose_name='descripcion')
	subjects = models.ManyToManyField(Subject, blank=True, verbose_name='asignatura')
	degrees = models.ManyToManyField(Degree, blank=True, verbose_name='grados')
	#TODO si se introduce una asignatura(+profesor) se debe poner el degree si no estaba
	is_student = models.BooleanField(default=True, verbose_name='es alumno')
	age = models.PositiveIntegerField(validators=[MinValueValidator(17), MaxValueValidator(100)], verbose_name='edad', blank=True)
	#TODO quizas mejor poner como grupo de usuario

	class Meta:
		verbose_name='perfil de usuario'
		verbose_name_plural='perfiles de usuario'
	
	def __unicode__(self):
		return u"Perfil de %s" % (self.user)
	

class Lesson(models.Model):
	start_time =  models.DateTimeField(verbose_name='hora de inicio')
	end_time = models.DateTimeField(verbose_name='hora de finalizacion')
	subject = models.ForeignKey(Subject, verbose_name='asignatura')
	room =	models.ForeignKey(Room, verbose_name='aula')#TODO on_delete funcion para buscar otra aula
	#No se si poner profesor o todos los de la asignatura
	
	class Meta:
		verbose_name='clase'

	def __unicode__(self):
		return u"Clase de %s" % (self.subject)
	
	def clean(self):
		super(Lesson, self).clean()
		if self.start_time and self.end_time:
			if self.start_time >= self.end_time:
				raise ValidationError('End_time must me greater than start_time')
			#Para evitar solapamiento de clases
			lesson_same_time = Lesson.objects.exclude(
						start_time__gte=self.end_time
					).exclude(
						end_time__lte=self.start_time
					)
			try:
				if lesson_same_time.filter(subject=self.subject).count() > 0:
					raise ValidationError('The lesson can not coincide with \
											another of the same subject')
				if lesson_same_time.filter(room=self.room).count() > 0:
					raise ValidationError('The lesson can not coincide with \
											another in the same room')
			except (Subject.DoesNotExist, Room.DoesNotExist):
				pass



class CheckIn(models.Model):
	user = models.ForeignKey(User, verbose_name='usuario')
	lesson = models.ForeignKey(Lesson, verbose_name='clase')
	mark = models.PositiveIntegerField(validators=[MaxValueValidator(5)], verbose_name='puntuacion', blank=True)
	comment = models.TextField(max_length=250, verbose_name='comentario', blank=True)

	class Meta:
		unique_together = ("user", "lesson")

	def __unicode__(self):
		return u"Checkin de %s" % (self.lesson)


class LessonComment(models.Model):
	user = models.ForeignKey(User, verbose_name='usuario')
	lesson = models.ForeignKey(Lesson, verbose_name='clase')
	date =  models.DateTimeField(default=timezone.now, verbose_name='hora')
	comment = models.TextField(max_length=250, verbose_name='comentario')
	
	class Meta:
		verbose_name='comentario en clase'
		verbose_name_plural='comentarios en clase'

	def __unicode__(self):
		return u"Comentario de %s" % (self.lesson)


class ForumComment(models.Model):
	user = models.ForeignKey(User, verbose_name='usuario')
	comment = models.TextField(max_length=150, verbose_name='comentario')
	date =  models.DateTimeField(default=timezone.now, verbose_name='hora')

	class Meta:
		verbose_name='comentario del foro'
		verbose_name_plural='comentarios del foro'

	def __unicode__(self):
		return u"Comentario %i" % (self.id)


class TimeTable(models.Model):#TODO poner con minuscula la segunda t cuando haga cambios en la BD
	subject = models.ForeignKey(Subject, verbose_name='asignatura')
	day = models.CharField(max_length=3, choices=WEEK_DAYS)
	start_time =  models.TimeField(verbose_name='hora de inicio')
	end_time = models.TimeField(verbose_name='hora de finalizacion')
	room =	models.ForeignKey(Room, verbose_name='aula')#TODO on_delete decidir que hago
	#Posible solucion poner edificio por si el aula no esta disponible
	#TODO No se si poner profesor o nada y que sean todos los de la asignatura
	
	class Meta:
		verbose_name='horario'

	def __unicode__(self):
		return u"Horario de %s" % (self.subject)

	def clean(self):
		super(TimeTable, self).clean()
		if self.start_time and self.end_time and self.day:
			if (self.start_time >= self.end_time):
				raise ValidationError('End_time must me greater than start_time')
			#Para evitar solapamiento de clases
			timetables_same_time = TimeTable.objects.filter(
							day=self.day
						).exclude(
							start_time__gte=self.end_time
						).exclude(
							end_time__lte=self.start_time
						)
			try:
				if timetables_same_time.filter(subject=self.subject).count() > 0:
					raise ValidationError('The timetable can not coincide with \
											another of the same subject')
				if timetables_same_time.filter(room=self.room).count() > 0:
					raise ValidationError('The timetable can not coincide with \
											another in the same room')
			except (Subject.DoesNotExist, Room.DoesNotExist):
				pass



