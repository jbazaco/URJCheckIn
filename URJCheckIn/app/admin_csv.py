from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from models import get_rand_string, UserProfile, Degree
from django.conf import settings
import os
from django.utils.datastructures import MultiValueDictKeyError
import csv
from django.contrib.auth.models import User

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
	if request.method != 'POST':
		return HttpResponseBadRequest('Wrong method')
	print "create users TODO"
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
	#if todo OK TODO
	return HttpResponseRedirect('/admin/auth/user/')

def create_user(info):
	if len(info) < 7:
		return
	elif not info[0] or not info[4]:
		return
	elif User.objects.filter(username=info[0]).exists():
		return
	elif UserProfile.objects.filter(dni=info[4]).exists():
		return
	user = User(username=info[0], first_name=info[1], last_name=info[2], email=info[3])
	user.set_password(info[4])
	user.save()
	is_student = not (info[6]=='No')#en caso de error mejor poner que es estudiante
	profile = UserProfile(user=user, dni=info[4], is_student=is_student, age=100)
	profile.save()
	degrees = info[5].split()
	for d_code in degrees:
		try:
			degree =Degree.objects.get(code=d_code)
		except Degree.DoesNotExist:
			continue
		profile.degrees.add(degree)
	#TODO si email, enviar email al usuario

