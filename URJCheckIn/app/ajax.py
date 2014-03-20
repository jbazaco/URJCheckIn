from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.template import loader, RequestContext
from forms import ReviewClassForm, ProfileEditionForm
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect

from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from models import UserProfile, ForumComment, Subject, ForumComment, CheckIn, Lesson, LessonComment
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from ajax_views_bridge import get_class_ctx, get_subject_ctx, get_checkin_ctx, get_forum_ctx, process_profile_post, get_profile_ctx, get_subjects_ctx, process_class_post, get_seminars_ctx, process_seminars_post, process_subject_post, get_subject_attendance_ctx, get_home_ctx, get_subject_edit_ctx



@dajaxice_register(method='GET')
@login_required
def subject(request, idsubj):
	"""Devuelve el contenido de la pagina de la asignatura indicada en idsubj"""
	if request.method == "GET":
		ctx = get_subject_ctx(request, idsubj)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/subjects/"+str(idsubj))
		html = loader.get_template('subject.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects/'+str(idsubj)})
	else:
		return wrongMethodJson(request)


dajaxice_register(method='GET')
@login_required
def subject_edit(request, idsubj):
	"""Devuelve el contenido de la pagina de asistencia de la asignatura indicada en idsubj"""
	if request.method == "GET":
		ctx = get_subject_edit_ctx(request, idsubj)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/subjects/"+str(idsubj)+"/edit")
		html = loader.get_template('subject_edit.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects/'+str(idsubj)+'/edit'})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')
def logout(request):
	"""Cierra sesion y devuelve el body y la url de la pagina /login"""
	auth_logout(request)
	html = loader.get_template('registration/login_body.html').render(RequestContext(request, {}))
	return simplejson.dumps({'body': html, 'url': '/login'})

#PASSWORD!!!!!!!!!

########################################################
# Funciones para solicitar mas elementos de algun tipo #
########################################################

