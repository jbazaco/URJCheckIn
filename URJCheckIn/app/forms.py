from django import forms

class ReviewClassForm(forms.Form):
	mark = forms.IntegerField(min_value=0, max_value=5, widget=forms.TextInput(attrs={
			'required':'required','type':'number', 'min':1, 'max':'5', 'value':'3', 'step':'1'}))
	comment = forms.CharField(max_length=150, required=False)

class ProfileEditionForm(forms.Form):
	name = forms.CharField(max_length=30,  widget=forms.TextInput(attrs={'disabled':'disabled'}))
											#solo puede modificarlo el admin #TODO
	age = forms.IntegerField(min_value=17, max_value=80, widget=forms.TextInput(attrs={
			'required':'required','type':'number', 'min':17, 'max':'80', 'step':'1'}))
	#TODO poner el resto de campos
