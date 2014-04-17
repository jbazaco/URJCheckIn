# -*- encoding: utf-8 -*-
import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from models import get_rand_string, UserProfile, Degree, Subject
from django.conf import settings
import os
from django.utils.datastructures import MultiValueDictKeyError
import csv
from django.contrib.auth.models import User
import unicodedata
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

def handle_uploaded_file(fich, root):
    """
    Guarda el fichero fich en el directorio root utilizando el nombre de
    fich para guardarlo o poniendo ademas un string aleatorio en caso de
    que ya exista un fichero con ese nombre
    Devuelve el nombre del fichero guardado (indicando la ruta completa)
    """
    name = str(fich)
    fullname = root + name
    while os.path.exists(fullname):
        fullname = root + get_rand_string() + name
    with open(fullname, 'wb+') as destination:
        for chunk in fich.chunks():
            destination.write(chunk)
    return fullname

@login_required
@staff_member_required
def create_users(request):
    """
    Crea usuarios y sus perfiles a partir de un fichero csv con los 
    campos separados por ';'
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Wrong method')
    try:
        r_file = request.FILES['csv_users']
    except MultiValueDictKeyError:
        return HttpResponseBadRequest('Wrong form')

    fname = handle_uploaded_file(r_file,  settings.MEDIA_ROOT + 'csv/')
    try:
        with open(fname, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                create_user_and_profile(row)
    except:
        if os.path.exists(fname):
            os.remove(fname)
        return HttpResponseBadRequest('Error procesando el fichero')
    if os.path.exists(fname):
        os.remove(fname)
    return HttpResponseRedirect('/admin/auth/user/')

def create_user_and_profile(info):
    """
    Crea un usuario si no existe, el formato de info debe ser:
    0->First_name (User)
    1->Last_name (User)
    2->Email (User)
    3->Dni (UserProfile)
    4->Degrees (UserProfile) [Con los codes de los Degrees separados
        por espacios si hay varios]
    5->Is_student (UserProfile) (Si=True / No=False) [realmente sera
        True si no pone 'No']
    """
    if len(info) < 6:
        return
    else:
        first_name = info[0].strip()
        last_name = info[1].strip()
        email = info[2].strip()
        dni = info[3].strip()
    if not first_name or not last_name or not dni:
        return
    #Primera linea de la plantilla con el nombre de los campos
    elif dni == 'DNI':
        return
    elif UserProfile.objects.filter(dni=dni).exists():
        return

    user = create_user(first_name, last_name, email, dni)
    if user.email:
        #TODO poner enlace a la pagina en produccion
        #TODO poner direccion de correo del emisor en produccion
        send_mail('Bienvenido a URJCheckIn', 'Acaba de crearse una cuenta de' +
                  ' usuario para esta dirección de correo.\nLos credenciales' +
                  ' son:\n\tUsuario: ' + user.username + '\n\tContraseña: ' +
                  'Introduzca su DNI\nLe recomendamos acceder a su perfil ' +
                  'para modificar su contraseña.',
                  'from@example.com',
                  [user.email], fail_silently=False)
    #en caso de error mejor poner que es estudiante
    is_student = not (info[5]=='No')
    create_profile(user, dni, is_student, info[4].split(), 100)

def create_user(first_name, last_name, email, password):
    """
    Crea un usuario y lo devuelve. El username es generado a partir
    de first_name y last_name
    """
    username = get_username(first_name, last_name)
    user = User(username=username, first_name=first_name, last_name=last_name)
    try:
        validate_email(email)
        user.email = email
    except ValidationError:
        pass
    user.set_password(password)
    user.save()
    return user

def create_profile(user, dni, is_student, degrees, age):
    """
    Crea un perfil de usuario, con los campos user, dni, is_student,
    degrees y age
    """
    profile = UserProfile(user=user, dni=dni, is_student=is_student, age=age)
    profile.save()
    for d_code in degrees:
        try:
            degree = Degree.objects.get(code=d_code)
        except Degree.DoesNotExist:
            continue
        profile.degrees.add(degree)

def remove_accents(input_str):
    """
    Elimina los acentos de string input_str y lo devuelve
    """
    #http://stackoverflow.com/questions/517923/what-is-the-best-way-to-
    #remove-accents-in-a-python-unicode-string
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def get_username(name, surname):
    """
    Genera un nombre de usuario con la primera letra del nombre y el
    primer apellido, si ya existe pone un numero al final
    """
    username = remove_accents((name[0:1] + surname.split()[0]).strip().lower())
    username_tmp = username
    num = 0
    while User.objects.filter(username=username).exists():
        num += 1
        username = username_tmp + str(num)
    return username

@login_required
@staff_member_required
def relate_subject_user(request, idsubj):
    """
    Relaciona los usuarios cuyos DNIs aparecen en el csv con la
    asignatura indicada en la URL
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Wrong method')
    try:
        r_file = request.FILES['csv_subject_users']
        subject = Subject.objects.get(id=idsubj)
    except MultiValueDictKeyError:
        return HttpResponseBadRequest('Wrong form')
    except Subject.DoesNotExist:
        return HttpResponseBadRequest('#404 The subject with id ' + 
                                      str(idsubj) + ' does not exist.')

    fname = handle_uploaded_file(r_file,  settings.MEDIA_ROOT + 'csv/')
    try:
        with open(fname, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                #Primera fila de la plantilla con el nombre del campo DNI
                if row[0] != 'DNI':
                    try:
                        profile = UserProfile.objects.get(dni=row[0])
                    except UserProfile.DoesNotExist:
                        continue
                    profile.subjects.add(subject)
    except:
        if os.path.exists(fname):
            os.remove(fname)
        return HttpResponseBadRequest('Error procesando el fichero')
    if os.path.exists(fname):
        os.remove(fname)
    return HttpResponseRedirect('/admin/app/subject/')

