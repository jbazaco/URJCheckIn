from django import forms

class ReviewClassForm(forms.Form):
	mark = forms.IntegerField(min_value=0, max_value=5, widget=forms.TextInput(attrs={
					'required':'required','type':'number', 'min':1, 'max':'5', 'value':'3'}))
	comment = forms.CharField(max_length=150, required=False)
