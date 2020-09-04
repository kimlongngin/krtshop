from django.shortcuts import render, get_object_or_404
from django.template import loader 
from django.views import generic 
from django.views.generic.edit import CreateView, UpdateView, DeleteView 


from django.shortcuts import render, redirect 
# from django.contrib.auth import authenticate, login 
from django.views.generic import View 

from .models import Product
