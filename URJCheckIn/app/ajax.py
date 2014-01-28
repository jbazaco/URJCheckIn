from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.template import loader, Context
from forms import ReviewClassForm, ProfileEditionForm

from django.template.loader import render_to_string

@dajaxice_register
def sayhello(request):
	return simplejson.dumps({'message':'Hello World'})

@dajaxice_register(method='GET')
def profile(request, iduser):#TODO, no renderiza bien...
	templ = loader.get_template('profile.html')
	cont = Context({'user': {'name':iduser, 'student': False, 'id':iduser}, 
					'classes': [{'id':'idclase1', 'name':'clase1'}, {'id':'idclase2', 'name':'clase2'}],
					'form': ProfileEditionForm()})
	html = templ.render(cont)
	return simplejson.dumps({'#mainbody':html, 'url': '/profile/view/'+iduser})
