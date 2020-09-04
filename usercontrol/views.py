from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.http import HttpResponse
from django.template import loader 
from django.views import generic
from django.urls import reverse_lazy


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.views.generic import View, TemplateView 
from product.models import Product
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserForm, UserLoginForm, RTUserForm
from django.template import loader 
from django.views.generic.list import ListView
from django.contrib import messages

from customer.models import Customer, SaleInvoiceItem, Payment, SaleInvoice
from django.core.paginator import Paginator

from django.utils import timezone
import csv

import xlwt


def auth_logout(request):
  logout(request)
  return redirect('usercontrol:login')


# User Login from the browser for the end user 
class UserLoginView(View):
	form_class = UserLoginForm
	template_name = 'registration/login.html'
	
	def get(self, request):

		form = self.form_class(None)
		return render(request, self.template_name, {'form':form})	
		
	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		username = request.POST['username']
		password = request.POST['password']
	
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('MainView:main_view_index')
		else:
			return render(request, self.template_name, {'form':form})


# User Login from the browser for the end user 
class UserFormView(View):
	form_class = RTUserForm
	template_name = 'registration/registration_form.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form':form})	
		
	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():
			user = form.save(commit=False) 
			username = form.cleaned_data['username']  
			data = User.objects.filter(username=username)
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()
			# return user objects if credentials are corrects 
			user = authenticate(username = username, password = password)
			if user is not None: 
				if user.is_active: 
					login(request, user) 
					return redirect('usercontrol:index') 
		return render(request, self.template_name, {'form':form}) 


class IndexView(generic.ListView):
	template_name =  'index.html'
	context_object_name = 'all_product'
	paginate_by = 3

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get_queryset(self):
		return Product.objects.filter(is_status=True).order_by('-created_at')


class ListUserView(SuccessMessageMixin, generic.ListView):
	template_name =  'userprofile/list_user.html'
	context_object_name = 'list_user'
	paginate_by = 30

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get_queryset(self):
		data = User.objects.filter()
		return data

class ListUserInvoice(generic.ListView): 
	
	template_name =  'userprofile/user_invoice.html'
	context_object_name = 'all_user_invoices'
	paginate_by = 5

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get(self, request, *args, **kwargs):
		page_num = 100
		if self.kwargs['pk']:
			pk = self.kwargs['pk']
			data = SaleInvoice.objects.filter(user = pk, is_status=True).order_by('-created_at')

			paginator = Paginator(data, page_num) # Show 25 contacts per page
			page = request.GET.get('page')
			contacts = paginator.get_page(page)
			return render(request, self.template_name, {'user_id':pk, 'all_invoices':contacts, 'paginator_num':page_num, 'all_data':data })



class SearchListUserInvoice(generic.ListView):
	model = SaleInvoice
	template_name = 'userprofile/search_user_invoice.html'
	context_object_name = 'all_invoices'
	# paginate_by = 5
	
	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
	

	def get(self, request, *args, **kwargs):

		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]
		user_id = self.request.GET['user_id']
		f_date = self.request.GET['start_date']
		s_date = self.request.GET['end_date']

		#  Check date formate
		#  Check date formate
		fd = f_date.split()
		ed = s_date.split()
		if len(fd) > 1 and len(ed) >1:
			s_d = fd[0]
			s_m = fd[1]
			s_y = fd[2]

			for i in month:
				s_m = i[str(s_m)]

			e_d = ed[0]
			e_m = ed[1]
			e_y = ed[2]

			for i in month:
				e_m = i[str(e_m)]
			is_date = s_y+'-'+s_m+'-'+s_d+' 01:00:00'
			ie_date = e_y+'-'+e_m+'-'+e_d+' 23:59:00'
		
			data = SaleInvoice.objects.filter(user=user_id, created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at') 
			return render(request, self.template_name, {'all_invoices':data, 'start_date':f_date, 'end_date':s_date, 'user_id':user_id})
		else: 
			data = {}
			
			return render(request, self.template_name, {'all_invoices':data, 'start_date':0, 'end_date':0, 'user_id':user_id})
			
class ExportListInvoiceView(generic.ListView):
	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get(self, request, *args, **kwargs):

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="users.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Users')

	    # Sheet header, first row
		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold = True


		columns = ['No', 'Invoice No', 'Seller', 'Total product', 'Date', ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		user_id = self.kwargs['pk']
		rows = SaleInvoice.objects.filter(user=user_id, is_status=True).order_by('-created_at')
		icount = 0
		n = 0 

		for i in rows:
			all_rows = []
			n += 1
			invoice_number = i.invoice_number
			full_name = i.user.first_name + '-' + i.user.last_name
			created = i.created_at

			if i.sale_invoice.all(): 
				mycount = i.sale_invoice.count()
			else:
				mycount = icount 

			all_rows = [n, invoice_number, full_name, mycount, str(created)]
			col_num = 0
			for index in all_rows:
		
				ws.write(n, col_num, index, font_style)
				col_num +=1
			

		wb.save(response)
		return response


class ExportSearchListInvoiceView(generic.ListView):
	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get(self, request, *args, **kwargs):
		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]
		
		user_id = self.kwargs['pk']
		f_date = self.kwargs['start_date']
		s_date = self.kwargs['end_date']

		#  Check date formate
		#  Check date formate
		fd = f_date.split()
		ed = s_date.split()
		if len(fd) > 1 and len(ed) >1:
			s_d = fd[0]
			s_m = fd[1]
			s_y = fd[2]

			for i in month:
				s_m = i[str(s_m)]

			e_d = ed[0]
			e_m = ed[1]
			e_y = ed[2]

			for i in month:
				e_m = i[str(e_m)]
			is_date = s_y+'-'+s_m+'-'+s_d+' 01:00:00'
			ie_date = e_y+'-'+e_m+'-'+e_d+' 23:59:00'



		if len(fd) > 1 and len(ed) >1:
			rows = SaleInvoice.objects.filter(user=user_id, created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at')
		
		else:
			rows = SaleInvoice.objects.filter(user=user_id, is_status=True).order_by('-created_at')


		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="users.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('User_search_invoice')

	    # Sheet header, first row
		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold = True


		columns = ['No', 'Invoice No', 'Seller', 'Total product', 'Date', ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		icount = 0
		n = 0 

		for i in rows:
			all_rows = []
			n += 1
			invoice_number = i.invoice_number
			full_name = i.user.first_name + '-' + i.user.last_name
			created = i.created_at

			if i.sale_invoice.all(): 
				mycount = i.sale_invoice.count()
			else:
				mycount = icount 

			all_rows = [n, invoice_number, full_name, mycount, str(created)]
			col_num = 0
			for index in all_rows:
				
				ws.write(n, col_num, index, font_style)
				col_num +=1
		wb.save(response)
		return response


import datetime
class AllUserInvoiceView(generic.ListView):
	template_name =  'userprofile/all_user_invoice.html'
	context_object_name = 'all_user_invoices'

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get(self, request, *args, **kwargs):

		today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
		today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)


		page_num = 50
		data = SaleInvoice.objects.filter(created_at__range=(today_min, today_max), is_status=True).order_by('-created_at')
		paginator = Paginator(data, page_num) # Show 25 contacts per page
		page = request.GET.get('page')
		contacts = paginator.get_page(page)
		return render(request, self.template_name, {'all_invoices':contacts, 'paginator_num':page_num, 'all_data':data })


class SearchAllUserInvoiceView(generic.ListView):

	template_name =  'userprofile/search_all_user_invoice.html'
	context_object_name = 'all_user_invoices'
	paginate_by = 5

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get(self, request, *args, **kwargs):


		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]
		key_term = self.request.GET['q']
		f_date = self.request.GET['start_date']
		s_date = self.request.GET['end_date']

		#  Check date formate
		#  Check date formate
		fd = f_date.split()
		ed = s_date.split()
		if len(fd) > 1 and len(ed) >1:
			s_d = fd[0]
			s_m = fd[1]
			s_y = fd[2]

			for i in month:
				s_m = i[str(s_m)]

			e_d = ed[0]
			e_m = ed[1]
			e_y = ed[2]

			for i in month:
				e_m = i[str(e_m)]
			is_date = s_y+'-'+s_m+'-'+s_d+' 01:00:00'
			ie_date = e_y+'-'+e_m+'-'+e_d+' 23:59:00'

			if key_term: 
				data =  SaleInvoice.objects.filter(invoice_number=key_term, created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at') 
				return render(request, self.template_name, {'all_invoices':data, 'start_date':f_date, 'end_date':s_date, 'key_term':key_term})
			else:
				data = SaleInvoice.objects.filter(created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at') 
				return render(request, self.template_name, {'all_invoices':data, 'start_date':f_date, 'end_date':s_date, 'key_term':'0101'})
		
		else: 
			data = SaleInvoice.objects.filter(invoice_number=key_term, is_status=True).order_by('-created_at')
			
			return render(request, self.template_name, {'all_invoices':data, 'start_date':0, 'end_date':0, 'key_term':key_term})


class ExportAllUserInvoiceView(generic.ListView):

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get(self, request, *args, **kwargs):

		today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
		today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="export_all_user_invoice.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Users')

	    # Sheet header, first row
		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold = True


		columns = ['No', 'Invoice No', 'Seller', 'Total product', 'Date', ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)
		rows = SaleInvoice.objects.filter(created_at__range=(today_min, today_max), is_status=True).order_by('-created_at')
		icount = 0
		n = 0 

		for i in rows:
			all_rows = []
			n += 1
			invoice_number = i.invoice_number
			full_name = i.user.first_name + '-' + i.user.last_name
			created = i.created_at

			if i.sale_invoice.all(): 
				mycount = i.sale_invoice.count()
			else:
				mycount = icount 

			all_rows = [n, invoice_number, full_name, mycount, str(created)]
			col_num = 0
			for index in all_rows:
			
				ws.write(n, col_num, index, font_style)
				col_num +=1

		wb.save(response)
		return response

class ExportAllSearchUserInvoiceView(generic.ListView):
	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)	
		
	def get(self, request, *args, **kwargs):
		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]
		
		key_term = self.kwargs['key_term']
		f_date = self.kwargs['start_date']
		s_date = self.kwargs['end_date']

		#  Check date formate
		#  Check date formate
		fd = f_date.split()
		ed = s_date.split()
		if len(fd) > 1 and len(ed) >1:
			s_d = fd[0]
			s_m = fd[1]
			s_y = fd[2]

			for i in month:
				s_m = i[str(s_m)]

			e_d = ed[0]
			e_m = ed[1]
			e_y = ed[2]

			for i in month:
				e_m = i[str(e_m)]
			is_date = s_y+'-'+s_m+'-'+s_d+' 01:00:00'
			ie_date = e_y+'-'+e_m+'-'+e_d+' 23:59:00'



		if len(fd) > 1 and len(ed) >1:
			s_d = fd[0]
			s_m = fd[1]
			s_y = fd[2]

			for i in month:
				s_m = i[str(s_m)]

			e_d = ed[0]
			e_m = ed[1]
			e_y = ed[2]

			for i in month:
				e_m = i[str(e_m)]
			is_date = s_y+'-'+s_m+'-'+s_d+' 01:00:00'
			ie_date = e_y+'-'+e_m+'-'+e_d+' 23:59:00'

			if key_term !='0101' and key_term !='': 
				rows =  SaleInvoice.objects.filter(invoice_number=key_term, created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at') 
			else:
				rows = SaleInvoice.objects.filter(created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at') 
		
		else: 
			rows = SaleInvoice.objects.filter(invoice_number=key_term, is_status=True).order_by('-created_at')
			
		
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="search_inovices.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('User_search_invoice')

	    # Sheet header, first row
		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold = True


		columns = ['No', 'Invoice No', 'Seller', 'Total product', 'Date', ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		icount = 0
		n = 0 

		for i in rows:
			all_rows = []
			n += 1
			invoice_number = i.invoice_number
			full_name = i.user.first_name + '-' + i.user.last_name
			created = i.created_at

			if i.sale_invoice.all(): 
				mycount = i.sale_invoice.count()
			else:
				mycount = icount 

			all_rows = [n, invoice_number, full_name, mycount, str(created)]
			col_num = 0
			for index in all_rows:
				ws.write(n, col_num, index, font_style)
				col_num +=1
		wb.save(response)
		return response




