from django.db import models
from django.contrib.auth.models import User

class Degree(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __unicode__(self):
		return self.name

class Subject(models.Model):
	name = models.CharField(max_length=100)
	degree = models.ForeignKey(Degree)
	
	class Meta:
		unique_together = ("name", "degree")
	
	def __unicode__(self):
		return u"%s %s" % (self.name, self.degree)

class Room(models.Model):
	room = models.CharField(max_length=20)
	building = models.CharField(max_length=20)
	centre_longitude = models.IntegerField()
	centre_latitude = models.IntegerField()
	radius = models.IntegerField()

	class Meta:
		unique_together = ("room", "building")

	def __unicode__(self):
		return u"room %i" % (self.id)

class UserProfile(models.Model):
	user = models.CharField(max_length=20) #models.OneToOneField(User)
	description = models.CharField(max_length=200, blank=True)
	subjects = models.ManyToManyField(Subject, blank=True)
	
	def __unicode__(self):
		return self.user

class StudentProfile(UserProfile):
	degree = models.ForeignKey(Degree)
	start_date = models.DateField() #cuando comenzo los estudios
	
class TeacherProfile(UserProfile):
	degrees = models.ManyToManyField(Degree, blank=True) #en los que imparte clase
	#TODO si se introduce una clase(+profesor) se debe poner el degree si no estaba
	
	

