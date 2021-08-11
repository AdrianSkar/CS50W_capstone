from django import forms

from .models import *

class EntryForm(forms.ModelForm):
	CHOICES = (
		('HTML', 'HTML'),
		('CSS', 'CSS'),
		('JS', 'JavaScript'),
		('PY', 'Python'),
		('GIT', 'Git'),
	)

	name = forms.CharField(
		label = 'Title:',
		widget = forms.TextInput(
			attrs = {
				'class': 'form-control m-2 mb-2 w-75'
			}
		),
		max_length = '70'
	)
	language = forms.ChoiceField(
		label = 'Language:',
		widget = forms.Select(
			attrs = {
				'class': 'form-select m-2 mb-2 w-75'
			}
		),
		choices = CHOICES
	)

	class Meta:
		model= Entry
		fields= ['name', 'language']

class SiteForm(forms.ModelForm):
	url = forms.URLField(
		label = 'Url:',
		widget = forms.TextInput(
			attrs = {
				'class': 'form-control m-2'
				}
			)
		)
	name = forms.CharField(
		label = 'Name:',
		widget = forms.TextInput(
			attrs = {
				'class': 'form-control m-2'
			}
		),
		max_length = '30'
	)

	class Meta:
		model= Site
		fields= ['name', 'url']
		
class NoteForm(forms.ModelForm):
	content = forms.CharField(
		label = 'Content:',
		widget = forms.Textarea(
			attrs = {
				'rows': 3,
				'class': 'form-control m-2'
				}
			),
		max_length = '3000'
		)
	title = forms.CharField(
		label = 'Title:',
		widget = forms.TextInput(
			attrs = {
				'class': 'form-control m-2'
			}
		),
		max_length = '30'
	)

	class Meta:
		model= Note
		fields= ['title', 'content']