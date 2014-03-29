from django import forms
from models import Degree, Subject, UserProfile, Lesson, CheckIn, Room
from django.forms.util import to_current_timezone

class MySplitDateTimeWidget(forms.MultiWidget):
	"""SplitDateTimeWidget pero permitiendo editar los attrs de DateInput y TimeInput por
		separado"""
	def __init__(self, attrs=None, date_attrs=None, time_attrs=None, date_format=None, time_format=None):
		widgets = (forms.DateInput(attrs=date_attrs, format=date_format),
					forms.TimeInput(attrs=time_attrs, format=time_format))
		super(MySplitDateTimeWidget, self).__init__(widgets, attrs)

	def decompress(self, value):
		if value:
			value = to_current_timezone(value)
			return [value.date(), value.time().replace(microsecond=0)]
		return [None, None]


class CheckInForm(forms.ModelForm):
	class Meta:
		model = CheckIn
		fields = ('mark', 'comment', 'longitude', 'latitude', 'codeword')
		widgets = {
			'mark': forms.TextInput(attrs={'required':'required','type':'number', 'min':1, 
											'max':'5', 'value':'3', 'step':'1'}),
			'comment': forms.Textarea(attrs={'maxlength':'250', 'class': 'form-control', 
												'rows': '3'}),
			'longitude': forms.TextInput(attrs={'hidden': 'hidden'}),
			'latitude': forms.TextInput(attrs={'hidden': 'hidden'}),
		}


class ProfileEditionForm(forms.ModelForm):
	#TODO poner el resto de campos
	class Meta:
		model = UserProfile
		fields = ('age', 'description')
		widgets = {
			'age': forms.TextInput(attrs={'required':'required','type':'number', 
											'min':17, 'max':'100', 'step':'1'}),
			'description': forms.Textarea(attrs={'maxlength':'200', 'class': 'form-control', 
												'rows': '3'}),
		}

#Formulario para que un profesor cree una Lesson
class ExtraLessonForm(forms.ModelForm):
	class Meta:
		model = Lesson
		fields = ('start_time', 'end_time', 'room')
		widgets = {
			'start_time': MySplitDateTimeWidget(date_attrs={'type': 'date', 'required': 'required', 'placeholder':'AAAA-MM-DD'}, time_attrs={'type': 'time', 'required': 'required', 'placeholder':'HH:MM'}),
			'end_time': MySplitDateTimeWidget(date_attrs={'type': 'date', 'required': 'required', 'placeholder':'AAAA-MM-DD'}, time_attrs={'type': 'time', 'required': 'required', 'placeholder':'HH:MM'}),
		}
	
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
	
#Formulario para editar la foto de perfil
class ProfileImageForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ('photo',)

#Formulario para filtrar las asignaturas mostradas en el control de asignaturas
class ControlFilterForm(forms.Form):
	subject = forms.CharField(required=False, widget=forms.TextInput(attrs={
												'placeholder':'asignatura'}))
	degree = forms.CharField(required=False, widget=forms.TextInput(attrs={
												'placeholder':'grado'}))
	professor_0 = forms.CharField(required=False, widget=forms.TextInput(attrs={
												'placeholder':'nombre profesor'}))
	professor_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={
												'placeholder':'apellido profesor'}))
	subject_type = forms.ChoiceField(choices=(
											('', 'Seminarios y asignaturas'),
											('Sem', 'Seminario'),
											('Subj', 'Asignatura'),
									), required=False)
	order = forms.ChoiceField(choices=(
										('name', 'Nombre'),
										('first_date', 'Fecha de inicio'),
										('last_date', 'Fecha de fin'),
									))
	order_reverse = forms.BooleanField(required=False)


#Formulario para filtrar los codigos de las clases
class CodesFilterForm(forms.Form):#TODO poner margen de horas
	day = forms.DateField(widget=forms.TextInput(attrs={'placeholder':'AAAA-MM-DD',
							'required':'required', 'type':'date'}))
	building = forms.CharField(required=False, widget=forms.TextInput(attrs={
							'placeholder':'edificio'}))
	room = forms.ModelChoiceField(required=False, queryset=Room.objects.all(), 
							empty_label="cualquiera")
	subject_type = forms.ChoiceField(choices=(
											('', 'Seminarios y asignaturas'),
											('Sem', 'Seminario'),
											('Subj', 'Asignatura'),
									), required=False)
	
