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

def handle_uploaded_file(f, root):
	name = str(f)
	fullname = root + name
	while os.path.exists(fullname):
		fullname = root + get_rand_string() + name
	with open(fullname, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	return fullname

@login_required
@staff_member_required
def create_users(request):
	"""Crea usuarios y sus perfiles a partir de un fichero csv con los campos separados por ';' """
	if request.method != 'POST':
		return HttpResponseBadRequest('Wrong method')
	try:
		r_file = request.FILES['csv_users']
	except MultiValueDictKeyError:
		return HttpResponseBadRequest('Wrong form')

	fname = handle_uploaded_file(r_file,  settings.MEDIA_ROOT + 'csv/')
	with open(fname, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in reader:
			create_user(row)	
	if os.path.exists(fname):
		os.remove(fname)
	return HttpResponseRedirect('/admin/auth/user/')

def create_user(info):
	"""
		Crea un usuario si no existe, el formato de info debe ser:
		0->First_name (User)
		1->Last_name (User)
		2->Email (User)
		3->Dni (UserProfile)
		4->Degrees (UserProfile) [Con los codes de los Degrees separados por espacios si hay varios]
		5->Is_student (UserProfile) (Si=True / No=False) [realmente sera True si no pone 'No']
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
	elif dni == 'DNI':#Primera linea de la plantilla con el nombre de los campos
		return
	elif UserProfile.objects.filter(dni=dni).exists():
		return

	username = get_username(first_name, last_name)

	user = User(username=username, first_name=first_name, last_name=last_name, email=email)
	user.set_password(dni)
	user.save()
	is_student = not (info[5]=='No')#en caso de error mejor poner que es estudiante
	profile = UserProfile(user=user, dni=dni, is_student=is_student, age=100)
	profile.save()
	degrees = info[4].split()
	for d_code in degrees:
		try:
			degree =Degree.objects.get(code=d_code)
		except Degree.DoesNotExist:
			continue
		profile.degrees.add(degree)
	#TODO si email, enviar email al usuario #TODO oncreate user

def remove_accents(input_str):
	#http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
	nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
	return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def get_username(name, surname):
	"""Genera un nombre de usuario con la primera letra del nombre y el primer apellido,
		si ya existe pone un numero al final"""
	username = remove_accents((name[0:1] + surname.split()[0]).strip().lower())
	username_tmp = username
	n = 0
	while User.objects.filter(username=username).exists():
		n += 1
		username = username_tmp + str(n)
	return username

@login_required
@staff_member_required
def relate_subject_user(request, idsubj):
	"""Relaciona los usuarios cuyos DNIs aparecen en el csv con la asignatura indicada
		en la URL"""
	if request.method != 'POST':
		return HttpResponseBadRequest('Wrong method')
	try:
		r_file = request.FILES['csv_subject_users']
		subject = Subject.objects.get(id=idsubj)
	except MultiValueDictKeyError:
		return HttpResponseBadRequest('Wrong form')
	except Subject.DoesNotExist:
		return HttpResponseBadRequest('#404 The subject with id ' + str(idsubj) + ' does not exist.')

	fname = handle_uploaded_file(r_file,  settings.MEDIA_ROOT + 'csv/')
	with open(fname, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in reader:
			if row[0] != 'DNI':#Primera fila de la plantilla con el nombre del campo DNI
				try:
					profile = UserProfile.objects.get(dni=row[0])
				except UserProfile.DoesNotExist:
					continue
				profile.subjects.add(subject)
				
	if os.path.exists(fname):
		os.remove(fname)
	return HttpResponseRedirect('/admin/app/subject/')

