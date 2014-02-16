from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.template import loader, RequestContext
from forms import ReviewClassForm, ProfileEditionForm

from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required

from models import UserProfile, ForumComment
from django.contrib.auth.models import User

#Por ahora todas las funciones estan incompletas, hay que terminarlas cuando este la BD

@dajaxice_register(method='GET')
@login_required
def profile(request, iduser):
	"""Devuelve el contenido de la pagina de perfil"""
	if request.method == "GET":
		templ = loader.get_template('profile.html')
		try:
			profile = UserProfile.objects.get(user=User.objects.get(id=iduser))#if user
		except (UserProfile.DoesNotExist, User.DoesNotExist):			
			return not_found(request, "/profile/view/"+iduser)
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
		cont = RequestContext(request, {'form': ReviewClassForm()})
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
		templ = loader.get_template('subjects.html')
		cont = RequestContext(request, {'subjects':[{'name':'subject1', 'id':'111'}, {'name':'subject2', 'id':'222'}]})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects'})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def subject(request, idsubj):
	"""Devuelve el contenido de la pagina de la asignatura indicada en idsubj"""
	if request.method == "GET":
		templ = loader.get_template('subject.html')
		cont = RequestContext(request, {'classes':[{'name':'class1', 'id':'111'}, {'name':'class2', 'id':'222'}]})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/subjects/'+str(idsubj)})
	else:
		return wrongMethodJson(request)

@dajaxice_register(method='GET')
@login_required
def class_info(request, idclass):
	"""Devuelve el contenido de la pagina de la asignatura indicada en idsubj"""
	if request.method == "GET":
		html = loader.get_template('class.html').render(RequestContext(request, {}))
		return simplejson.dumps({'#mainbody':html, 'url': '/class/'+str(idclass)})
	else:
		return wrongMethodJson(request)

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
		print comment
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

