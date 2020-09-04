from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from datetime import date
from django.shortcuts import render, get_object_or_404, Http404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# from usercontrol.models import CustomUser


# from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# class CustomUserCreationForm(UserCreationForm):

#     class Meta(UserCreationForm):
#         model = CustomUser
#         fields = ('username', 'email')

# class CustomUserChangeForm(UserChangeForm):

#     class Meta(UserChangeForm):
#         model = CustomUser
#         fields = ('username', 'email')



class RTUserForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter username'}), required=False)
	first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter first name'}), required=False)
	last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter last name'}), required=False)
	email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'example@mail.com'}), required=False)
	phone_number = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'015000000'}), required=False)
	password = forms.CharField(widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Enter password'}), required=False)
	confirm_password = forms.CharField(widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Enter password'}), required=False)

	class Meta: 
		model = User
		fields =['username', 'first_name', 'last_name', 'email', 'phone_number', 'password', 'confirm_password']

	def clean_username(self):
		if self.cleaned_data['username'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['username']
	def clean_first_name(self):
		if self.cleaned_data['first_name'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['first_name']
	def clean_last_name(self):
		if self.cleaned_data['last_name'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['last_name']
	
	
	def clean_email(self):
		if self.cleaned_data['email'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		email = self.cleaned_data['email']
		try:
			mt = validate_email(email)
		except:
			raise forms.ValidationError("Email is not in correct format")
		return email
	def clean_phone_number(self):
		if self.cleaned_data['phone_number'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		phone_number = self.cleaned_data['phone_number']
		return phone_number

	def clean_password(self):
		if self.cleaned_data['password'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['password']
		
	def clean_confirm_password(self):
		if self.cleaned_data['confirm_password'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		pas= self.cleaned_data['password']
		cpas= self.cleaned_data['confirm_password']
		MIN_LENGHT = 8
		if pas and cpas:
			if pas != cpas:
				raise forms.ValidationError("password and confirm password not matched")
			else:
				if len(pas) < MIN_LENGHT:
					raise forms.ValidationError("password should have atleast 8 character")

class UserForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter username'}), required=False)
	first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter first name'}), required=False)
	last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter last name'}), required=False)
	email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'example@mail.com'}), required=False)
	phone_number = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'015000000'}), required=False)
	password = forms.CharField(widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Enter password'}), required=False)
	confirm_password = forms.CharField(widget = forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Enter password'}), required=False)

	class Meta: 
		model = User
		fields =['username', 'first_name', 'last_name', 'email', 'phone_number', 'password', 'confirm_password']

	def clean_username(self):
		if self.cleaned_data['username'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['username']
	def clean_first_name(self):
		if self.cleaned_data['first_name'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['first_name']
	def clean_last_name(self):
		if self.cleaned_data['last_name'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['last_name']
	
	
	def clean_email(self):
		if self.cleaned_data['email'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		email = self.cleaned_data['email']
		try:
			mt = validate_email(email)
		except:
			raise forms.ValidationError("Email is not in correct format")
		return email
	def clean_phone_number(self):
		if self.cleaned_data['phone_number'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		phone_number = self.cleaned_data['phone_number']
		return phone_number

	def clean_password(self):
		if self.cleaned_data['password'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		return self.cleaned_data['password']
		
	def clean_confirm_password(self):
		if self.cleaned_data['confirm_password'].strip() == '':
			raise forms.ValidationError('This field cannot be blank!')
		pas= self.cleaned_data['password']
		cpas= self.cleaned_data['confirm_password']
		MIN_LENGHT = 8
		if pas and cpas:
			if pas != cpas:
				raise forms.ValidationError("password and confirm password not matched")
			else:
				if len(pas) < MIN_LENGHT:
					raise forms.ValidationError("password should have atleast 8 character")

class UserLoginForm(forms.ModelForm):
	username = forms.CharField(widget = forms.TextInput)
	password = forms.CharField(widget = forms.PasswordInput)

	class Meta: 
		model = User
		fields =['username', 'password']

