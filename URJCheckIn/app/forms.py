from django import forms
from models import Degree, Subject

class ReviewClassForm(forms.Form):
	mark = forms.IntegerField(min_value=0, max_value=5, widget=forms.TextInput(attrs={
			'required':'required','type':'number', 'min':1, 'max':'5', 'value':'3', 'step':'1'}))
	comment = forms.CharField(max_length=150, required=False, widget=forms.Textarea(attrs={
			'maxlength':'150', 'class': 'form-control', 'rows': '3'}))

class ProfileEditionForm(forms.Form):
	age = forms.IntegerField(min_value=17, max_value=80, widget=forms.TextInput(attrs={
			'required':'required','type':'number', 'min':17, 'max':'80', 'step':'1'}))
	description = forms.CharField(max_length=200, widget=forms.Textarea(attrs={
			'maxlength':'200', 'class': 'form-control', 'rows': '3'}))
	#TODO poner el resto de campos


#Formulario poner clase la asignatura seleccionable pasando un array de las asignaturas disponibles
#si se elige desde la pagina de una asignatura se pone el campo fijo (o no?)
class AddClassForm(forms.Form):
	reason =  forms.CharField(max_length=200)
	#subject = selecionable
	#date =
	#mas campos
	
#Formulario para crear un Subject (no incluye el campo is_seminar)
class SubjectForm(forms.ModelForm):
	class Meta:
		model = Subject
		fields = ('name', 'degrees', 'first_date', 'last_date', 'max_students', 'description')
		widgets = {
			'name': forms.TextInput(attrs={'required':'required'}),
			'first_date': forms.TextInput(attrs={'type': 'date', 'required': 'required',
										'placeholder':'AAAA-MM-DD'}),
			'last_date': forms.TextInput(attrs={'type': 'date', 'required': 'required',
										 'placeholder':'AAAA-MM-DD'}),
			'max_students': forms.TextInput(attrs={'required':'required','type':'number', 
											'min':0, 'step':'1'}),
			'description': forms.Textarea(attrs={'maxlength':'200', 'class': 'form-control',
												 'rows': '3', 'required':'required'}),
		}
	

