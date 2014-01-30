from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.template import loader, Context
from forms import ReviewClassForm, ProfileEditionForm

from django.utils.datastructures import MultiValueDictKeyError


@dajaxice_register(method='GET')
def profile(request, iduser):
	if request.method == "GET":
		templ = loader.get_template('profile.html')
		cont = Context({'user': {'name':iduser, 'student': False, 'id':iduser}, 
						'classes': [{'id':'idclase1', 'name':'clase1'}, {'id':'idclase2', 'name':'clase2'}],
						'form': ProfileEditionForm()})
		html = templ.render(cont)
		return simplejson.dumps({'#mainbody':html, 'url': '/profile/view/'+iduser})
	else:
		return simplejson.dumps({'error':'Metodo ' + request.method + ' no soportado'})

@dajaxice_register(method='POST')#quitar POSTs si son por defecto
def process_class(request,form):#TODO mirar el campo class del form
	if request.method == "POST":
		return simplejson.dumps({'deleteFromDOM':['#xc_'+form['idclass']]})
	else:
		return simplejson.dumps({'error':'Metodo ' + request.method + ' no soportado'})


