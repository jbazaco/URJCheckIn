# -*- encoding: utf-8 -*-
from django import forms
from models import (Subject, UserProfile, Lesson, CheckIn, Room,
                    Building, AdminTask)
from django.forms.util import to_current_timezone, timezone
import datetime
from django.contrib.auth.models import User

class MySplitDateTimeWidget(forms.MultiWidget):
    """
    SplitDateTimeWidget pero permitiendo editar los attrs de 
    DateInput y TimeInput por separado
    """
    def __init__(self, attrs=None, date_attrs=None, time_attrs=None,
                 date_format=None, time_format=None):
        widgets = (forms.DateInput(attrs=date_attrs, format=date_format),
                   forms.TimeInput(attrs=time_attrs, format=time_format))
        super(MySplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]


class CheckInForm(forms.ModelForm):
    """Formulario para realizar el check in"""
    class Meta:
        model = CheckIn
        fields = ('mark', 'comment', 'longitude', 'latitude', 'codeword')
        widgets = {
            'mark': forms.TextInput(attrs={
                'required':'required', 'type':'number', 'min':0, 'max':'5',
                'value':'3', 'step':'1', 'placeholder':'0-5'}),
            'comment': forms.Textarea(attrs={
                    'maxlength':'250', 'class': 'form-control', 'rows': '3',
                    'placeholder': '(Comentario y puntuación anónimos' +
                    ' para el profesor)'}),
            'longitude': forms.TextInput(attrs={'hidden': 'hidden'}),
            'latitude': forms.TextInput(attrs={'hidden': 'hidden'}),
        }


class ProfileEditionForm(forms.ModelForm):
    """
    Formulario para editar la edad, descripcion y la opcion de mostrar
    el email
    """
    class Meta:
        model = UserProfile
        fields = ('age', 'description', 'show_email')
        widgets = {
            'age': forms.TextInput(attrs={
                    'required':'required', 'type':'number', 'min':17,
                    'max':'100', 'step':'1'}),
            'description': forms.Textarea(attrs={
                    'maxlength':'200', 'class': 'form-control', 'rows': '3'}),
        }

class ChangeEmailForm(forms.ModelForm):
    """Formulario para modificar el email"""
    class Meta:
        model = User
        fields = ('email',)

class ExtraLessonForm(forms.ModelForm):
    """Formulario para que un profesor cree una Lesson"""
    class Meta:
        model = Lesson
        fields = ('start_time', 'end_time', 'room')
        widgets = {
            'start_time': MySplitDateTimeWidget(
                            date_attrs={'type': 'date', 'required': 'required',
                                        'placeholder':'AAAA-MM-DD'}, 
                            time_attrs={'type': 'time', 'required': 'required',
                                        'placeholder':'HH:MM'}),
            'end_time': MySplitDateTimeWidget(
                            date_attrs={'type': 'date', 'required': 'required',
                                        'placeholder':'AAAA-MM-DD'},
                            time_attrs={'type': 'time', 'required': 'required',
                                        'placeholder':'HH:MM'}),
        }
    
class SubjectForm(forms.ModelForm):
    """
    Formulario para crear un Subject (no incluye el campo is_seminar)
    """
    class Meta:
        model = Subject
        fields = ('name', 'degrees', 'first_date', 'last_date', 'max_students',
                    'description')
        widgets = {
            'name': forms.TextInput(attrs={'required':'required'}),
            'first_date': forms.TextInput(attrs={
                                'type': 'date', 'required': 'required',
                                'placeholder':'AAAA-MM-DD'}),
            'last_date': forms.TextInput(attrs={
                                'type': 'date', 'required': 'required',
                                'placeholder':'AAAA-MM-DD'}),
            'max_students': forms.TextInput(attrs={
                                'required':'required','type':'number', 'min':0,
                                'step':'1'}),
            'description': forms.Textarea(attrs={
                                'maxlength':'200','class': 'form-control',
                                'rows': '3', 'required':'required'}),
        }
    
class ProfileImageForm(forms.ModelForm):
    """Formulario para editar la foto de perfil"""
    class Meta:
        model = UserProfile
        fields = ('photo',)

class ReportForm(forms.ModelForm):
    """Formulario para reportar un problema"""
    class Meta:
        model = AdminTask
        fields = ('ask', 'url')
        widgets = {
            'ask': forms.Textarea(attrs={
                    'maxlength':'500', 'class': 'form-control', 'rows': '4',
                    'required':'required'}),
            'url': forms.TextInput(attrs={
                    'placeholder': 'url afectada (opcional)'})
        }

class ControlFilterForm(forms.Form):
    """
    Formulario para filtrar las asignaturas mostradas en el control de
    asignaturas
    """
    subject = forms.CharField(required=False, widget=forms.TextInput(attrs={
                                                'placeholder':'asignatura'}))
    degree = forms.CharField(required=False, widget=forms.TextInput(attrs={
                                                    'placeholder':'grado'}))
    professor_0 = forms.CharField(required=False,
                    widget=forms.TextInput(attrs={
                                        'placeholder':'nombre profesor'}))
    professor_1 = forms.CharField(required=False,
                    widget=forms.TextInput(attrs={
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


class CodesFilterForm(forms.Form):
    """Formulario para filtrar los codigos de las clases"""
    day = forms.DateField(required=False, widget=forms.TextInput(attrs={
                        'placeholder':'AAAA-MM-DD', 'type':'date'}))
    building = forms.ModelChoiceField(required=False,
                                      queryset=Building.objects.all(),
                                      empty_label="todos")
    room = forms.ModelChoiceField(required=False, queryset=Room.objects.all(), 
                                  empty_label="cualquiera")
    subject_type = forms.ChoiceField(choices=(
                                            ('', 'Seminarios y asignaturas'),
                                            ('Sem', 'Seminario'),
                                            ('Subj', 'Asignatura'),
                                    ), required=False)
    from_time =  forms.TimeField(widget=forms.TextInput(attrs={
                        'placeholder':'HH:MM', 'type':'time'}), required=False)
    to_time =  forms.TimeField(widget=forms.TextInput(attrs={
                        'placeholder':'HH:MM', 'type':'time'}), required=False)
    order = forms.ChoiceField(choices=(
                                    ('start_time', 'Hora de inicio'),
                                    ('room__room', 'Aula'),
                                    ('room__building__building', 'Edificio'),
                                ))
    order_reverse = forms.BooleanField(required=False)

    def clean_day(self):
        """Si day esta vacio pone el dia de hoy"""
        data = self.cleaned_data['day']
        if data:
            return data
        else:
            return datetime.date.today()
    
    def clean_from_time(self):
        """Si from_rime esta vacio pone la hora actual"""
        data = self.cleaned_data['from_time']
        if data:
            return data
        else:
            now = to_current_timezone(timezone.now())
            return datetime.time(now.hour, now.minute)

    def clean_to_time(self):
        """Si to_time esta vacio pone la ultima hora del dia"""
        data = self.cleaned_data['to_time']
        if data:
            return data
        else:
            return datetime.time.max

class FreeRoomForm(forms.Form):
    """Formulario para buscar aulas libres"""
    start_time = forms.DateTimeField(widget=MySplitDateTimeWidget(
        date_attrs={
          'type': 'date', 'required': 'required', 'placeholder':'AAAA-MM-DD'},
        time_attrs={
          'type': 'time', 'required': 'required', 'placeholder':'HH:MM'}))
    end_time = forms.DateTimeField(widget=MySplitDateTimeWidget(
        date_attrs={
          'type': 'date', 'required': 'required', 'placeholder':'AAAA-MM-DD'},
        time_attrs={
          'type': 'time', 'required': 'required', 'placeholder':'HH:MM'}))
    building = forms.ModelChoiceField(queryset=Building.objects.all())

    def clean(self):
        cleaned_data = super(FreeRoomForm, self).clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time:
            if start_time > end_time:
                raise forms.ValidationError('La fecha de inicio debe ser ' +
                                            'anterior a la de finalización')
        return cleaned_data

