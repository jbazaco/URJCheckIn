# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone, formats
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.conf import settings
import os
from django.db.models.signals import post_save, pre_save
import datetime
import random
import pytz
import random

WEEK_DAYS = (
    ('0', 'Lunes'),
    ('1', 'Martes'),
    ('2', 'Miércoles'),
    ('3', 'Jueves'),
    ('4', 'Viernes'),
    ('5', 'Sábado'),
    ('6', 'Domingo')
)

class Degree(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='nombre')
    code = models.CharField(max_length=6, unique=True, verbose_name='código')

    class Meta:
        verbose_name = 'grado'

    def __unicode__(self):
        return self.code

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='nombre')
    degrees = models.ManyToManyField(Degree, verbose_name='grados')
    first_date = models.DateField(verbose_name='fecha de inicio')
    last_date = models.DateField(verbose_name='fecha de finalización')
    is_seminar = models.BooleanField(verbose_name='es seminario',
                                     default=False)
    #util para seminarios, se puede dejar a 0 para clases
    max_students = models.PositiveIntegerField(verbose_name='plazas',
                                                default=0)
    description = models.TextField(max_length=200, blank=True,
                                    verbose_name='descripción')
    creator = models.ForeignKey(User, verbose_name='creador')

    class Meta:
        verbose_name = 'asignatura'
    
    def __unicode__(self):
        return u"%s" % (self.name)

    def clean(self):
        super(Subject, self).clean()
        if self.first_date and self.last_date:
            if (self.first_date > self.last_date):
                raise ValidationError('La fecha de inicio no puede ser ' +
                                      'posterior a la de finalización')

    def n_students(self):
        return self.userprofile_set.filter(is_student=True).count()

    def percent_prof_attend(self):
        n_lesson_done = self.lesson_set.filter(done=True).count()
        n_lesson_past = self.lesson_set.filter(
                                            end_time__lt = timezone.now()
                                        ).count()
        if n_lesson_past < 1:
            return 0
        return round(100.0*n_lesson_done/n_lesson_past, 2)

    def percent_stud_attend(self):
        """
        Devuelve el porcentaje de asistencia de los alumnos a la
        asignatura
        """
        n_lessons_done = self.lesson_set.filter(done=True).count()
        #El total de checkins que podria haber es el numero de clases dadas por
        # el numero de estudiantes de la asignatura
        n_div = self.n_students()*n_lessons_done
        n_checks = CheckIn.objects.filter(user__userprofile__is_student=True, 
                                          lesson__subject=self,
                                          lesson__done=True).count()
        if n_div < 1:
            return 0
        return round(100.0*n_checks/n_div, 2)

    def avg_mark(self):
        """
        Devuelve la valoracion media de la asignatura, teniendo en
        cuenta todas las clases realizadas
        """
        lessons = self.lesson_set.filter(done=True)
        if not lessons:
            return 3
        mark = 0
        for lesson in lessons:
            mark += lesson.avg_mark()
        return round(mark/lessons.count(), 2)

    def subject_state(self):
        """
        Devuelve un string 'actual', 'antigua', 'futura' en suncion de
        si es una asignatura que se esta impartiendo ahora, ya se ha 
        impartido o se impartira en el futuro, respectivamente
        """
        today = datetime.date.today()
        if self.last_date < today:
            return 'antigua'
        elif self.first_date > today:
            return 'futura'
        else:
            return 'actual'
    subject_state.short_description = 'estado'
    
            


class Building(models.Model):
    building = models.CharField(max_length=30, verbose_name='edificio',
                                unique=True)

    class Meta:
        verbose_name = 'edificio'

    def __unicode__(self):
        return u"Edificio %s" % (self.building)


class Room(models.Model):
    room = models.CharField(max_length=20, verbose_name='aula')
    building = models.ForeignKey(Building, verbose_name='edificio')
    centre_longitude = models.FloatField(verbose_name='centro longitud')
    centre_latitude = models.FloatField(verbose_name='centro latitud')
    radius = models.IntegerField(verbose_name='radio')

    class Meta:
        verbose_name = 'aula'
        unique_together = ("room", "building")

    def __unicode__(self):
        return u"Aula %s, %s" % (self.room, self.building)


def user_image_path(instance, filename):
    """
    Si ya habia una imagen de perfil del usuario la elimina y devuelve
    como nombre /profile_photos/ + instance.user.id
    """
    name = 'profile_photos/' + str(instance.user.id)
    remove_if_exists(name)
    return name

def remove_if_exists(name):
    """
    Elimina el fichero de nombre name en la ruta MEDIA_ROOT, si existe
    Devuelve True si existia y False si no existia
    """
    fullname = settings.MEDIA_ROOT + name
    if os.path.exists(fullname):
        os.remove(fullname)
        return True
    return False


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name='usuario')
    photo = models.ImageField(upload_to=user_image_path, blank=True)
    description = models.TextField(max_length=200, blank=True,
                                   verbose_name='descripción')
    subjects = models.ManyToManyField(Subject, blank=True,
                                      verbose_name='asignatura')
    degrees = models.ManyToManyField(Degree, blank=True, verbose_name='grados')
    is_student = models.BooleanField(default=True, verbose_name='es alumno')
    age = models.PositiveIntegerField(validators=[MinValueValidator(17),
                    MaxValueValidator(100)], verbose_name='edad', blank=True)
    dni = models.CharField(max_length=20, verbose_name='DNI', unique=True)    
    show_email = models.BooleanField(default=False,
                                    verbose_name='mostrar email')

    class Meta:
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuario'
        permissions = (('can_see_statistics', 'Can see statistics'),
                       ('can_see_codes', 'Can see codes'),) 
    
    def __unicode__(self):
        return u"Perfil de %s" % (self.user)

    def clean(self):
        super(UserProfile, self).clean()
        if self.description:
            self.description = self.description.strip()



def get_rand_string():
    """Devuelve un string de 20 caracteres aleatorios"""
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in\
                    range(20))

class Lesson(models.Model):
    start_time =  models.DateTimeField(verbose_name='hora de inicio')
    end_time = models.DateTimeField(verbose_name='hora de finalización')
    subject = models.ForeignKey(Subject, verbose_name='asignatura')
    room =    models.ForeignKey(Room, verbose_name='aula')
    #TODO on_delete funcion para buscar otra aula
    is_extra = models.BooleanField(default=False,
                                   verbose_name='es clase extra')
    done = models.BooleanField(verbose_name='realizada', default=False)
    codeword = models.CharField(max_length=20, verbose_name='código',
                                default=get_rand_string)
    students_counted = models.PositiveIntegerField(
                                default=0, verbose_name='alumnos contados')
    
    class Meta:
        verbose_name = 'clase'

    def __unicode__(self):
        return u"Clase de %s (%s)" % (self.subject, 
                formats.date_format(timezone.localtime(self.start_time),
                                    "SHORT_DATETIME_FORMAT"))
    
    def clean(self):
        super(Lesson, self).clean()
        if self.start_time and self.end_time:
            if self.start_time < timezone.now():
                raise ValidationError('La hora de inicio debe ser posterior ' +
                                      'a este momento')
            if self.start_time >= self.end_time:
                raise ValidationError('La hora de finalización debe ser ' +
                                      'posterior a la de inicio')
            #Para evitar solapamiento de clases
            lesson_same_time = Lesson.objects.exclude(
                        start_time__gte=self.end_time
                    ).exclude(
                        end_time__lte=self.start_time
                    ).exclude(
                        id=self.id
                    )
            if timezone.localtime(self.start_time).date() != timezone.\
                                            localtime(self.end_time).date():
                raise ValidationError('No se pueden crear clases que se ' +
                                      'desarrollen en más de un día')
                
            try:
                if lesson_same_time.filter(subject=self.subject):
                    raise ValidationError('La clase no puede solaparse con ' +
                                          'otra de la misma asignatura')
                if lesson_same_time.filter(room=self.room):
                    raise ValidationError('La clase no puede solaparse con ' +
                                          'otra en el mismo aula')
            except (Subject.DoesNotExist, Room.DoesNotExist):
                pass

    def n_stud_checkin(self):
        """
        Devuelve el numero de estudiantes que hicieron check in en la
        clase
        """
        return self.checkin_set.filter(
                                        user__userprofile__is_student=True
                                    ).count()

    def checkin_percent(self):
        """
        Devuelve el porcentaje de estudiantes que hicieron check in en
        la clase (en relacion a los alumnos de la asignatura)
        """
        n_students = self.subject.n_students()
        if n_students > 0:
            n_checkin = self.n_stud_checkin()
            return round(100.0*n_checkin/n_students, 2)
        else:
            return 100

    def avg_mark(self):
        """Devuelve la valoracion media de la clase"""
        checkins = self.checkin_set.filter(user__userprofile__is_student=True)
        if not checkins:
            return 3
        mark = checkins.aggregate(Avg('mark'))['mark__avg']
        return round(mark, 2)

class AdminTask(models.Model):
    user = models.ForeignKey(User, verbose_name='usuario')
    ask = models.TextField(max_length=500, verbose_name='petición')
    url = models.TextField(max_length=200, verbose_name='url del problema',
                           blank=True)
    time = models.DateTimeField(default=timezone.now, verbose_name='hora')
    done = models.BooleanField(verbose_name='gestionada', default=False)
    solver = models.ForeignKey(User, verbose_name='gestionada por', blank=True,
                               null=True, related_name='solved_task',
                               limit_choices_to={'is_staff': True})
    answer = models.TextField(max_length=500, verbose_name='respuesta',
                              blank=True)

    class Meta:
        verbose_name = 'tarea de administración'
        verbose_name_plural = 'tareas de administración'

    def __unicode__(self):
        return u"Petición de %s" % (self.user)

class CheckIn(models.Model):
    user = models.ForeignKey(User, verbose_name='usuario')
    lesson = models.ForeignKey(Lesson, verbose_name='clase')
    mark = models.PositiveIntegerField(validators=[MaxValueValidator(5)],
                                       verbose_name='puntuación', blank=True)
    longitude = models.FloatField(verbose_name='longitud', blank=True,
                                  null=True)
    latitude = models.FloatField(verbose_name='latitud', blank=True, null=True)
    codeword = models.CharField(max_length=20, verbose_name='codigo',
                                blank=True)
    comment = models.TextField(max_length=250, verbose_name='comentario',
                               blank=True)
    time = models.DateTimeField(default=timezone.now, verbose_name='hora')

    class Meta:
        unique_together = ("user", "lesson")

    def __unicode__(self):
        return u"Checkin de %s" % (self.lesson)
    
    def clean(self):
        super(CheckIn, self).clean()
        if not (self.codeword or self.longitude):
            raise ValidationError('Tienes que enviar el código o tu ' +
                                  'localización para hacer CheckIn')
        if self.codeword:
            if self.codeword != self.lesson.codeword:
                raise ValidationError('Ese código no se corresponde con el ' +
                                      'de la clase actual')


def check_lesson_done(sender, instance, **kwargs):
    """
    Si el checkin es realizado por un profesor pone lesson.done = True
    """
    try:
        profile = instance.user.userprofile
        if not profile.is_student:
            lesson = instance.lesson
            lesson.done = True
            lesson.save()
    except UserProfile.DoesNotExist:
        pass
post_save.connect(check_lesson_done, sender=CheckIn)


class LessonComment(models.Model):
    user = models.ForeignKey(User, verbose_name='usuario')
    lesson = models.ForeignKey(Lesson, verbose_name='clase')
    date =  models.DateTimeField(default=timezone.now, verbose_name='hora')
    comment = models.TextField(max_length=250, verbose_name='comentario')
    
    class Meta:
        verbose_name = 'comentario en clase'
        verbose_name_plural = 'comentarios en clase'

    def __unicode__(self):
        return u"Comentario de %s" % (self.lesson)


class ForumComment(models.Model):
    user = models.ForeignKey(User, verbose_name='usuario')
    comment = models.TextField(max_length=150, verbose_name='comentario')
    date =  models.DateTimeField(default=timezone.now, verbose_name='hora')

    class Meta:
        verbose_name = 'comentario del foro'
        verbose_name_plural = 'comentarios del foro'

    def __unicode__(self):
        return u"Comentario %i" % (self.id)


class Timetable(models.Model):
    subject = models.ForeignKey(Subject, verbose_name='asignatura')
    day = models.CharField(max_length=3, choices=WEEK_DAYS)
    start_time =  models.TimeField(verbose_name='hora de inicio')
    end_time = models.TimeField(verbose_name='hora de finalización')
    room = models.ForeignKey(Room, verbose_name='aula')
    #TODO on_delete decidir que hago
    #Posible solucion poner edificio por si el aula no esta disponible
    
    class Meta:
        verbose_name = 'horario'

    def __unicode__(self):
        return u"Horario de %s" % (self.subject)

    def clean(self):
        super(Timetable, self).clean()
        if self.start_time and self.end_time and self.day:
            if (self.start_time >= self.end_time):
                raise ValidationError('La hora de finalización debe ser ' +
                                      'posterior a la de inicio')
            #Para evitar solapamiento de clases
            timetables_same_time = Timetable.objects.filter(
                            day=self.day
                        ).exclude(
                            start_time__gte=self.end_time
                        ).exclude(
                            end_time__lte=self.start_time
                        ).exclude(
                            id=self.id
                        )
            try:
                if self.subject:
                    #Se comprueba si tiene 'name' para el caso en que se cree
                    # el Timetable a la vez que la Subject y en la creacion de
                    # la Subject haya errores
                    if self.subject.name:
                        if timetables_same_time.filter(subject=self.subject):
                            raise ValidationError('El horario no puede ' +
                                                  'solaparse con otro ' +
                                                  'de la misma asignatura')
                        if timetables_same_time.filter(room=self.room, 
                            subject__last_date__gte=self.subject.first_date,
                            subject__first_date__lte=self.subject.last_date):
                            raise ValidationError('El horario no puede ' +
                                                  'solaparse con otro ' +
                                                  'en el mismo aula')
                        
            except (Subject.DoesNotExist, Room.DoesNotExist):
                pass


def get_first_lesson_date(timetable):
    """
    Devuelve el primer dia de clase de una asignatura para un horario
    dado
    El primer dia sera el menor dia que cumpla las siguientes
    condiciones:
    - El dia de la semana debe ser el indicado en el timetable
    - El dia es mayor que hoy
    - El dia es mayor o igual que el dia en que comienza la asignatuta 
    """
    first_date = timetable.subject.first_date # se va calculando aqui el dia a
                                              #partir del cual se crean clases
    today = datetime.date.today()
    if first_date <= today:
        first_date = today + datetime.timedelta(days=1)
    first_dayweek = first_date.weekday()
    dayweek = int(timetable.day)

    if first_dayweek > dayweek:
        first_date += datetime.timedelta(days=7)
    return first_date + datetime.timedelta(days=(dayweek-first_dayweek))

def create_lesson(start_datetime, end_datetime, room, subject):
    """
    Crea una clase para la asignatura subject desde start_datetime hasta
    end_datetime
    -En caso de existir ya una clase de la asignatura en esa franja
    horaria no se creara
    -En caso de estar ocupada el aula se buscara una libre en ese
    edificio y si no la hay no se creara
    """
    lessons_now = Lesson.objects.filter(start_time__lte = end_datetime, 
                                        end_time__gte = start_datetime)
    #Si ya hay una clase de la asignatura
    if lessons_now.filter(subject = subject).exists():
        pass
    #Si ya hay una clase en ese aula busca otro aula en el edificio
    elif lessons_now.filter(room = room).exists():
        new_room = get_free_room(start_datetime, end_datetime, room.building)
        if new_room:#si no hay aula libre a esa hora no se crea la clase 
            Lesson(start_time=start_datetime, end_time = end_datetime,
                   subject = subject, room = new_room).save()
    else:
        Lesson(start_time=start_datetime, end_time = end_datetime,
               subject = subject, room = room).save()
#TODO def delete_timetable_lessons(timetable):
#    """Elimina las clases posteriores al momento actual que coincidan 
#    exactamente con el horario del timetable recibido"""
#    lessons = Lesson.objects.filter(subject=timetable.subject,
#                                   start_time__gte=timezone.now())
#    print lessons[0].start_time.hour
#    print timetable.start_time

def create_timetable_lessons(sender, instance, **kwargs):
    #TODO eliminar y modificar---->post_____.connect()
    """
    Crea clases de la asignatura instance.subject en los dias
    instance.day durante el periodo de la asignatuta
    Funcion pensada para ser llamada despues de guardar un Timetable
    """
    date = get_first_lesson_date(instance)
    #TODO if instance.pk:
    #    old_timetable = Timetable.objects.get(id=instance.id)
    #    delete_timetable_lessons(old_timetable)

    last_date = instance.subject.last_date
    current_tz = str(timezone.get_current_timezone())
    start_datetime_n = datetime.datetime(date.year, date.month, date.day,
                                         instance.start_time.hour,
                                         instance.start_time.minute)
    start_datetime = pytz.timezone(current_tz).localize(start_datetime_n,
                                                        is_dst=None)
    end_datetime_n = datetime.datetime(date.year, date.month, date.day,
                                       instance.end_time.hour,
                                       instance.end_time.minute)
    end_datetime = pytz.timezone(current_tz).localize(end_datetime_n,
                                                      is_dst=None)

    room = instance.room
    subject = instance.subject
    while start_datetime.date() <= last_date:
        create_lesson(start_datetime, end_datetime, room, subject)
        start_datetime += datetime.timedelta(days=7)
        end_datetime += datetime.timedelta(days=7)
    
pre_save.connect(create_timetable_lessons, sender=Timetable)


def get_free_room(start_time, end_time, building):
    """
    Devuelve un aula libre en el edificio building desde start_time
    hasta end_time
    """
    rooms = Room.objects.filter(building=building)
    n_rooms = rooms.count()
    #Para no recorrerlas en orden, ya que si fuesen en orden se irian ocupando
    #las primeras y a medida que aumentasen las clases creadas habria que
    #recorrer muchas hasta dar con un aula libre
    rand_pos = random.sample(range(n_rooms), n_rooms)
    for i in rand_pos:
        room = rooms[i]
        if not room.lesson_set.filter(start_time__lte = end_time,
                                      end_time__gte = start_time).exists():
            return room
    return None

    

