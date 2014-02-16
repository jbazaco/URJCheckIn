from django import forms

class ReviewClassForm(forms.Form):
	mark = forms.IntegerField(min_value=0, max_value=5, widget=forms.TextInput(attrs={
			'required':'required','type':'number', 'min':1, 'max':'5', 'value':'3', 'step':'1'}))
	comment = forms.CharField(max_length=150, required=False)

class ProfileEditionForm(forms.Form):
	age = forms.IntegerField(min_value=17, max_value=80, widget=forms.TextInput(attrs={
			'required':'required','type':'number', 'min':17, 'max':'80', 'step':'1'}))
	description = forms.CharField(max_length=200, widget=forms.Textarea)
	#TODO poner el resto de campos


#Formulario poner clase la asignatura seleccionable pasando un array de las asignaturas disponibles
#si se elige desde la pagina de una asignatura se pone el campo fijo (o no?)
class AddClassForm(forms.Form):
	reason =  forms.CharField(max_length=200)
	#subject = selecionable
	#date =
	#mas campos
	
#Formulario para crear un seminario
class CreateSeminarForm(forms.Form):
	name = forms.CharField(max_length=30)
	#degree = seleccionable (posibilidad de poner varios)
	#mas campos

#usar donde sea conveniente modelform TODO
	

