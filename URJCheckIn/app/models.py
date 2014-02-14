from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator

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
	name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
	code = models.CharField(max_length=6, unique=True, verbose_name='Codigo')

	class Meta:
		verbose_name='Grado'

	def __unicode__(self):
		return self.code


class Subject(models.Model):
	name = models.CharField(max_length=100, verbose_name='Nombre')
	degree = models.ForeignKey(Degree, verbose_name='Grado')
	n_students = models.PositiveIntegerField(verbose_name='Num. estudiantes', default=0)
	first_date = models.DateField(verbose_name='Fecha de inicio')
	last_date = models.DateField(verbose_name='Fecha de finalizacion')

	class Meta:
		verbose_name='Asignatura'
		unique_together = ("name", "degree")
	
	def __unicode__(self):
		return u"%s %s" % (self.name, self.degree)


class Room(models.Model):
	room = models.CharField(max_length=20, verbose_name='Aula')
	building = models.CharField(max_length=20, verbose_name='Edificio')
	centre_longitude = models.IntegerField(verbose_name='Centro Longitud')
	centre_latitude = models.IntegerField(verbose_name='Centro Latitud')
	radius = models.IntegerField(verbose_name='Radio')

	class Meta:
		verbose_name='Aula'
		unique_together = ("room", "building")

	def __unicode__(self):
		return u"aula %i" % (self.id)


class UserProfile(models.Model):
	user = models.OneToOneField(User, verbose_name='Usuario')
	#TODO photo = models.ImageField()
	description = models.TextField(max_length=200, blank=True, verbose_name='Descripcion')
	subjects = models.ManyToManyField(Subject, blank=True, verbose_name='Asignatura')

	class Meta:
		abstract = True
	
	def __unicode__(self):
		return u"Perfil de %s" % (self.user)


class StudentProfile(UserProfile):
	degree = models.ForeignKey(Degree, verbose_name='Grado')
	start_date = models.DateField(verbose_name='Fecha de inicio') #cuando comenzo los estudios

	class Meta:
		verbose_name='Perfil de estudiante'
		verbose_name_plural='Perfiles de estudiantes'
	

class TeacherProfile(UserProfile):
	degrees = models.ManyToManyField(Degree, blank=True, verbose_name='Grado') #en los que imparte clase
	#TODO si se introduce una clase(+profesor) se debe poner el degree si no estaba
	class Meta:
		verbose_name='Perfil de profesor'
		verbose_name_plural='Perfiles de profesores'


class Lesson(models.Model):
	start_time =  models.DateTimeField(verbose_name='Hora de inicio')
	end_time = models.DateTimeField(verbose_name='Hora de finalizacion')
	subject = models.ForeignKey(Subject, verbose_name='Asignatura')
	room =	models.ForeignKey(Room, verbose_name='Aula')
	#No se si poner profesor o todos los de la asignatura
	
	class Meta:
		verbose_name='Clase'

	def __unicode__(self):
		return u"Clase de %s" % (self.subject)


class CheckIn(models.Model):
	user = models.ForeignKey(User, verbose_name='Usuario')
	lesson = models.ForeignKey(Lesson, verbose_name='Clase')
	mark = models.PositiveIntegerField(validators=[MaxValueValidator(5)], verbose_name='Puntuacion', blank=True)
	comment = models.TextField(max_length=250, verbose_name='Comentario', blank=True)

	def __unicode__(self):
		return u"Checkin de %s" % (self.lesson)


class LessonComment(models.Model):
	user = models.ForeignKey(User, verbose_name='Usuario')
	lesson = models.ForeignKey(Lesson, verbose_name='Clase')
	date =  models.DateTimeField(default=timezone.now(), verbose_name='Hora')
	comment = models.TextField(max_length=250, verbose_name='Comentario')
	
	class Meta:
		verbose_name='Comentario en clase'
		verbose_name_plural='Comentarios en clase'

	def __unicode__(self):
		return u"Comentario de %s" % (self.lesson)


class ForumComment(models.Model):
	user = models.ForeignKey(User, verbose_name='Usuario')
	comment = models.TextField(max_length=150, verbose_name='Comentario')
	date =  models.DateTimeField(default=timezone.now(), verbose_name='Hora')

	class Meta:
		verbose_name='Comentario del foro'
		verbose_name_plural='Comentarios del foro'

	def __unicode__(self):
		return u"Comentario %i" % (self.id)


class TimeTable(models.Model):
	subject = models.ForeignKey(Subject, verbose_name='Asignatura')
	day = models.CharField(max_length=3, choices=WEEK_DAYS)
	start_time =  models.TimeField(verbose_name='Hora de inicio')
	end_time = models.TimeField(verbose_name='Hora de finalizacion')
	room =	models.ForeignKey(Room, verbose_name='Aula')
	#No se si poner profesor o todos los de la asignatura
	
	class Meta:
		verbose_name='Horario'

	def __unicode__(self):
		return u"Horario de %s" % (self.subject)




