from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from datetime import date
from django.shortcuts import render, get_object_or_404, Http404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from product.models import Product



class ProductSearchForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name, ID, Code'}), required=True)
	
	class Meta: 
		model = Product
		fields =['name']

	def clean_username(self):
		if self.cleaned_data['name'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['name']
	
	