from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from customer.models import SaleInvoice
from datetime import date
from django.shortcuts import render, get_object_or_404, Http404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



class SaleInvoiceForm(ModelForm): 
	def __init__(self, *args, **kwargs): 
		super(SaleInvoiceForm, self).__init__(*args, **kwargs)                       
		self.fields['user'].disabled = True	
		
	class Meta:
		fields = ['user']
		model = SaleInvoice

