from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.template import loader, RequestContext
from forms import ReviewClassForm, ProfileEditionForm

from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required

from models import UserProfile, ForumComment, Subject, ForumComment
from django.contrib.auth.models import User

from getctx import get_class_ctx, get_subject_ctx

@dajaxice_register(method='GET')
@login_required
def profile(request, iduser):
	"""Devuelve el contenido de la pagina de perfil"""
	if request.method == "GET":
		templ = loader.get_template('profile.html')
		try:
			profile = UserProfile.objects.get(user=iduser)
		except (UserProfile.DoesNotExist, User.DoesNotExist):			
			return send_error(request,
						'El usuario con id ' + iduser + ' no tiene perfil', 
						'/profile/view/'+iduser)
		cont = RequestContext(request, {'profile': profile, 
						'classes': [{'id':'idclase1', 'name':'clase1'}, {'id':'idclase2', 'name':'clase2'}],
						'form': ProfileEditionForm()})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/profile/view/'+iduser})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')
@login_required
def update_profile(request, iduser, form):
	"""Modifica el perfil del usuario registrado"""
	if request.method == "POST":
		#comprobar user = usuarioregistrado
		pform = ProfileEditionForm(form)
		if not pform.is_valid():
			return simplejson.dumps({'errors': pform.errors});
		data = pform.cleaned_data
		return simplejson.dumps({'user':{'id': iduser, 'age':data['age'], 'description':data['description']}})#coger datos del usuario tras guardar
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')#quitar POSTs si son por defecto
@login_required
def process_class(request,form):#TODO mirar el campo class del form
	if request.method == "POST":
		return simplejson.dumps({'deleteFromDOM':['#xc_'+form['idclass']]})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def checkin(request):
	"""Devuelve la pagina para hacer check in"""
	if request.method == "GET":
		templ = loader.get_template('checkin.html')
		try:
			profile = request.user.userprofile
		except UserProfile.DoesNotExist:
			return send_error(request, 'No tienes un perfil creado.', '/checkin')
		cont = RequestContext(request, {'profile':profile, 'form': ReviewClassForm()})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/checkin'})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='POST')#quitar POSTs si son por defecto
@login_required
def process_checkin(request, form):
	""" procesa un check in"""
	if request.method == "POST":
		print form["longitude"]
		print form["latitude"]
		print form["accuracy"]
		print form["codeword"]
		return simplejson.dumps({'ok': True})
	else:
		return wrongMethodJson(request)

def wrongMethodJson(request):
	return simplejson.dumps({'error':'Metodo ' + request.method + ' no soportado'})

@dajaxice_register(method='GET')
@login_required
def subjects(request):
	"""Devuelve el contenido de la pagina de las asignaturas"""
	if request.method == "GET":
		try:
			profile = UserProfile.objects.get(user=request.user)
		except (UserProfile.DoesNotExist, User.DoesNotExist):			
			return send_error(request, 'No tienes un perfil creado.', '/subjects')
		subjects = profile.subjects.all()
		#TODO separar las que son seminarios de las que no
		templ = loader.get_template('subjects.html')
		cont = RequestContext(request, {'subjects':subjects})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects'})
	else:
		return wrongMethodJson(request)

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

@dajaxice_register(method='GET')
@login_required
def class_info(request, idclass):
	"""Devuelve el contenido de la pagina de la clase indicada en idclass"""
	if request.method == "GET":
		ctx = get_class_ctx(request, idclass)
		if ('error' in ctx):
			return send_error(request, ctx['error'], "/class/"+str(idclass))
		html = loader.get_template('class.html').render(RequestContext(request, ctx))
		return simplejson.dumps({'#mainbody':html, 'url': '/class/'+str(idclass)})
	else:
		return wrongMethodJson(request)

#TODO una funcion que mande nuevos comentarios si hay nuevos y se sigue en la pagina
@dajaxice_register(method='GET')
@login_required
def forum(request):
	"""Devuelve el contenido de la pagina del foro"""
	if request.method == "GET":
		comments = ForumComment.objects.filter().order_by('-date')[:10]
		templ = loader.get_template('forum.html')
		cont = RequestContext(request, {'comments': comments})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/forum'})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='POST')#quitar POSTs si son por defecto
@login_required
def publish_forum(request, comment):
	""" procesa un check in"""
	if request.method == "POST":
		ForumComment(comment=comment, user=request.user).save()
		return simplejson.dumps({'ok': True})
	else:
		return wrongMethodJson(request)


@dajaxice_register(method='GET')
@login_required
def home(request):
	"""Devuelve la pagina para hacer check in"""
	if request.method == "GET":
		html = loader.get_template('home.html').render(RequestContext(request, {}))
		return simplejson.dumps({'#mainbody':html, 'url': '/'})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def not_found(request, path):
	"""Devuelve una pagina que indica que la pagina solicitada no existe"""
	html = loader.get_template('404.html').render(RequestContext(request, {}))
	return simplejson.dumps({'#mainbody':html, 'url': path})

def send_error(request, error, url):
	templ = loader.get_template('error.html')
	cont = RequestContext(request, {'message':error})
	html = templ.render(cont)
	return simplejson.dumps({'#mainbody':html, 'url':url})
