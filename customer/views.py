from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.http import HttpResponse
from django.template import loader 
from django.views import generic
from django.urls import reverse_lazy


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.views.generic import View, TemplateView 
from product.models import Product, Promotion, ProductCategory
from customer.models import Customer, SaleInvoiceItem, Payment, SaleInvoice

from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.template import loader 
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView 

from django.contrib import messages
from django.core.paginator import Paginator

import xlwt


class IndexView(SuccessMessageMixin, generic.ListView):
	template_name = 'customer/index.html'
	context_object_name = 'all_customer'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
		
	def get_queryset(self):
		return Customer.objects.filter(is_status=True).order_by('-created_at')
	
class CustomerDetailView(SuccessMessageMixin, generic.ListView):
	template_name = 'customer/detail.html'
	context_object_name = 'detail_customers'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
	
	@method_decorator(login_required(''))
	def get(self, request, *args, **kwargs):

		if self.kwargs['full_name']:
			try:
				page_num = 101
				c_id = Customer.objects.get(full_name=self.kwargs['full_name'].strip(), is_status=True)

				data = SaleInvoice.objects.filter(customer=c_id, is_status=True).order_by('-created_at')[:100]  
				paginator = Paginator(data, page_num) # Show 25 contacts per page
				page = request.GET.get('page')
				contacts = paginator.get_page(page)
				return render(request, self.template_name, {'all_invoices':contacts, 'name': self.kwargs['full_name'].strip(), 'paginator_num':page_num, 'all_data':data })

			except Customer.DoesNotExist:
				raise Http404(" Data does not exist")
		else:
			raise Http404("Please check your data again.")

class SearchCustomerInvoice(generic.ListView):
	template_name = 'customer/search_customer_invoice.html'
	context_object_name = 'detail_customers'


	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
	
	@method_decorator(login_required(''))
	def get(self, request, *args, **kwargs):

		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]
		full_name = self.request.GET['full_name']

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
		
			try:
				c_id = Customer.objects.get(full_name=full_name.strip(), is_status=True)

				data = SaleInvoice.objects.filter(customer=c_id, created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at') 
				return render(request, self.template_name, {'all_invoices':data, 'start_date':f_date, 'end_date':s_date, 'full_name':full_name})
			
			except Customer.DoesNotExist:
				raise Http404(" Data does not exist")
		else: 
			data = {}
			return render(request, self.template_name, {'all_invoices':data, 'start_date':0, 'end_date':0, 'full_name':full_name})


class ExportSearchCustomerInvoice(generic.ListView):
	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
	
	@method_decorator(login_required(''))
	def get(self, request, *args, **kwargs):
		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]
		
		full_name = self.kwargs['full_name']
		f_date = self.kwargs['start_date']
		s_date = self.kwargs['end_date']
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


		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="customer_invoice.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Users')

	    # Sheet header, first row
		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		columns = ['No', 'Invoice No', 'Seller', 'Total product', 'Date', ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)


		try: 
			c_id = Customer.objects.get(full_name=self.kwargs['full_name'].strip(), is_status=True)

			if len(fd) > 1 and len(ed) >1:
				rows = SaleInvoice.objects.filter(customer=c_id, created_at__range=(is_date, ie_date), is_status=True).order_by('-created_at')
			
			else:
				rows = SaleInvoice.objects.filter(customer=c_id, is_status=True).order_by('-created_at')
		except Customer.DoesNotExist:
			raise Http404(" Data does not exist")

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



class ExportCustomerInvoiceView(generic.ListView):

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
	
	@method_decorator(login_required(''))
	def get(self, request, *args, **kwargs):
		name = self.kwargs['full_name']
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="customer_invoice.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Users')

	    # Sheet header, first row
		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		columns = ['No', 'Invoice No', 'Seller', 'Total product', 'Date', ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		c_id = Customer.objects.get(full_name=self.kwargs['full_name'].strip(), is_status=True)
		rows = SaleInvoice.objects.filter(customer=c_id, is_status=True).order_by('-created_at')[:100]  

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



class ListInvoiceDetailView(SuccessMessageMixin, generic.ListView):
	template_name = 'customer/list_invoice_detail.html'
	context_object_name = 'list_invoices'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):

		all_sales = []
		grand_total = 0
		product_name = ''
		product_number = ''
		product_image = ''
		qty = 0
		unit = 0
		discount = 0
		

		if self.kwargs['invoice_no']:
			try:

				d_invoice = SaleInvoice.objects.filter(invoice_number = self.kwargs['invoice_no'], is_status=True)
				full_name = ''
				phone_number = ''
				address = ''
				if d_invoice: 
					for i in d_invoice:
						full_name = i.customer.full_name
						phone_number = i.customer.phone_number
						address = i.customer.address


				# Select related field between SaleInvoice with SaleInvoiceItem by "invoice and invoice_number"
				data = SaleInvoiceItem.objects.filter(invoice__invoice_number=self.kwargs['invoice_no'], is_status=True)
				if data:
					for i in data:
						sub_total = 0
						product_name = i.product.name
						product_number = i.product.product_number
						product_image = i.product.default_image
						unit = i.unit
						unit_price = i.unit_price
						discount = i.discount

						if i.discount:
							my_total = unit_price * unit
							# mydiscount = (my_total * discount) / 100
							mydiscount = discount * unit_price
							sub_total = my_total - mydiscount
						else:
							sub_total = unit_price * unit

						grand_total = grand_total + sub_total
						all_sales.append({'product_name': product_name, 'product_number': product_number, 'product_image':product_image, 'unit':unit, 'unit_price':unit_price, 'discount':discount, 'sub_total':sub_total})

				
				pays = Payment.objects.filter(invoice__invoice_number=self.kwargs['invoice_no'], is_status=True)

				all_pays = []

				total_pay = 0
				remaining = 0
				if pays:
					for p in pays:
					
						if p.discount: 
							p_d = (p.total_amount * p.discount)/100
							total_pay = p.total_amount - p_d

						remaining = p.remain

						all_pays.append({ 'total_amount': p.total_amount, 'discount':p.discount, 'pay_amount':total_pay, 'receive_amount':p.receive_amount, 'remaining':remaining })
							

				remain = grand_total - total_pay

				return render(request, self.template_name, {'all_pays':all_pays, 'all_sales': all_sales, 'remain':remain, 'pays':total_pay, 'full_name':full_name, 'grand_total': grand_total, 'list_invoices':data, 'invoice_no':self.kwargs['invoice_no'], 'phone_number':phone_number , 'address':address})
			except SaleInvoiceItem.DoesNotExist:
				raise Http404(" Data does not exist")
		else:
			raise Http404("Please check your data again.")


class ListClient(View):
	template_name = 'customer/list_client.html'

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)


	def get(self, request):
		q = request.GET['q']
		page_num = 1
		
		data = Customer.objects.filter(full_name__contains=q.strip(), is_status=True) | Customer.objects.filter(email__contains=q.strip(), is_status=True) | Customer.objects.filter(phone_number__contains=q.strip(), is_status=True)
		paginator = Paginator(data, page_num) # Show 25 contacts per page
		page = request.GET.get('page')
		contacts = paginator.get_page(page)

		return render(request, self.template_name, {'all_customer':contacts, 'full_name':q.strip(), 'paginator_num':page_num, 'all_data':data })



class CompansateRemaining(SuccessMessageMixin, generic.ListView):
	template_name = 'customer/owepay.html'
	context_object_name = 'all_customer'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		if self.kwargs['invoice_no']:
			inv = SaleInvoice.objects.get(invoice_number=self.kwargs['invoice_no'], is_status=True)
			data = Payment.objects.filter(invoice = inv, is_status=True).order_by('-created_at')
			return render(request, self.template_name, {'all_pays':data, 'invoice_no': self.kwargs['invoice_no']})
		else: 
			return HttpResponse('<h3> This invoice number not exist in database. </h3>')


class MakePayment(SuccessMessageMixin, View):

	template_name = 'customer/owe.html'
	context_object_name = 'all_customer'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	@method_decorator(login_required(''))
	def post(self, request):
		success_message = "Pay successfully."
		if request.method == 'POST':

			invoice_no = request.POST.get('invoice_no')
			total_amount = float(request.POST.get('itotal_amount'))
			discount = float(request.POST.get('discount'))
			pay_amount = float(request.POST.get('ipay_amount'))
			receive_amount = request.POST.get('receive_amount')
			remaining = float(request.POST.get('iremain'))

			if receive_amount == '' or receive_amount == 0:
				receive_amount = 0
			if pay_amount == '' or pay_amount == 0:
				pay_amount = 0

			if discount == '' or discount == 0:
				discount = 0.0


			try:
				d_invoice = SaleInvoice.objects.get(invoice_number=str(invoice_no), is_status=True)
				sc = SaleInvoiceItem.objects.filter(invoice=d_invoice, is_status=True)
				if sc.count() > 0:
					try:
						Payment.objects.filter(invoice=d_invoice, is_status=True).delete()
						# Payment.objects.filter(invoice=d_invoice, is_status=True)
					except Payment.DoesNotExist:
						HttpResponse("Payment doesn't exist.")
			except SaleInvoice.DoesNotExist:
				HttpResponse("This invoice doesn't exist.")

			try:
				try:
					if float(remaining) > 0:
						b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain=remaining, pay_status = 'OWE')
						b_payment.save()
					else:
						b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain=remaining, pay_status = 'FULL')
						b_payment.save()
					return redirect('customer:owe_list')
				except ValueError:
					if int(remaining) > 0:
						b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain=remaining, pay_status = 'OWE')
						b_payment.save()
					else:
						b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain=remaining, pay_status = 'FULL')
						b_payment.save()
					return redirect('customer:owe_list')

				# return super(OweClient, self).get(request, *args, **kwargs)
			except Payment.DoesNotExist:
				return HttpResponse('<div style="text-alight:center;"><h4><code> Payment not exist. </code></h4></div>')

		else:
			return HttpResponse('<div style="text-alight:center;"><h4><code> Invalid form. </code></h4></div>')
	
	def get_success_url(self):

		data = Payment.objects.filter(pay_status='OWE', is_status=True).order_by('-created_at')
		return data
		

class OweClient(SuccessMessageMixin, generic.ListView):

	template_name = 'customer/owe.html'
	context_object_name = 'all_customer'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		data = Payment.objects.filter(pay_status='OWE', is_status=True).order_by('-created_at')
		return data

from datetime import tzinfo, timedelta, datetime

class OweListSearch(SuccessMessageMixin, generic.ListView):

	template_name = 'customer/own_list_search.html'
	context_object_name = 'all_customer'
	#paginate_by = 1


	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
	

	def get_queryset(self):

		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]

		q = self.request.GET['q']
		f_date = self.request.GET['start_date']
		s_date = self.request.GET['end_date']

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
			is_date = s_y+'-'+s_m+'-'+s_d
			ie_date = e_y+'-'+e_m+'-'+e_d

			if q:
				data = Payment.objects.filter(invoice__invoice_number__contains=q.strip(), is_status=True, pay_status='OWE').order_by('-created_at') | Payment.objects.filter(invoice__customer__full_name__contains=q.strip(), created_at__range=(is_date, ie_date), is_status=True, pay_status='OWE').order_by('-created_at')  | Payment.objects.filter(invoice__customer__email__contains=q.strip(), created_at__range=(is_date, ie_date), is_status=True, pay_status='OWE').order_by('-created_at') | Payment.objects.filter(invoice__customer__phone_number__contains=q.strip(), created_at__range=(is_date, ie_date), is_status=True, pay_status='OWE').order_by('-created_at')
				return data
			else:

				data = Payment.objects.filter(created_at__range=(is_date, ie_date), is_status=True, pay_status='OWE').order_by('-created_at') 
				return data
		else:
			if q:
				data = Payment.objects.filter(invoice__invoice_number__contains=q.strip(), is_status=True, pay_status='OWE').order_by('-created_at') | Payment.objects.filter(invoice__customer__full_name__contains=q.strip(), is_status=True, pay_status='OWE') | Payment.objects.filter(invoice__customer__email__contains=q.strip(), is_status=True, pay_status='OWE') | Payment.objects.filter(invoice__customer__phone_number__contains=q.strip(), is_status=True, pay_status='OWE').order_by('-created_at')
				return data
			else:
				data = Payment.objects.filter(is_status=True, pay_status='OWE').order_by('-created_at') 
				return data
			
class SaveList(SuccessMessageMixin, generic.ListView):
	template_name = 'customer/save_list.html'
	context_object_name = 'all_customer'
	paginate_by = 50

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		data = SaleInvoice.objects.filter(payment_invoice = None,  is_status=True).order_by('-created_at')
		return data
		

class DeleteSave(SuccessMessageMixin, DeleteView):
	model = SaleInvoice 
	success_message = " Deleted successfully!"
	success_url = reverse_lazy('customer:save_list')
	template_name = 'customer/delete_save.html'

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	@method_decorator(login_required(''))
	def get(self, request, *args, **kwargs):
		objEx= SaleInvoice.objects.filter(id=self.kwargs['pk'], is_status=True)
		if objEx.count()<=0:
			return HttpResponse('<h4><code> This object not exist in the list. </code></h4>')
		self.object = self.get_object()
		return super(DeleteSave, self).get(request, *args, **kwargs)	

class SearchSaveList(SuccessMessageMixin, generic.ListView):

	template_name = 'customer/search_save_list.html'
	context_object_name = 'all_customer'
	#paginate_by = 1


	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):

		month = [{'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12' }]
		q = self.request.GET['q']
		f_date = self.request.GET['start_date']
		s_date = self.request.GET['end_date']

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
			is_date = s_y+'-'+s_m+'-'+s_d
			ie_date = e_y+'-'+e_m+'-'+e_d

			if q:
		
				data = SaleInvoice.objects.filter(invoice_number__contains=q.strip(), is_status=True, payment_invoice = None) | SaleInvoice.objects.filter(customer__full_name__contains=q.strip(), created_at__range=(is_date, ie_date), is_status=True, payment_invoice = None).order_by('-created_at')  | SaleInvoice.objects.filter(customer__email__contains=q.strip(), created_at__range=(is_date, ie_date), is_status=True, payment_invoice = None).order_by('-created_at') | SaleInvoice.objects.filter(customer__phone_number__contains=q.strip(), created_at__range=(is_date, ie_date), is_status=True, payment_invoice = None).order_by('-created_at')
				return data
			else:

				data = SaleInvoice.objects.filter(created_at__range=(is_date, ie_date), is_status=True, payment_invoice = None).order_by('-created_at') 
				return data

		else:
			if q:
				data = SaleInvoice.objects.filter(invoice_number__contains=q.strip(), is_status=True, payment_invoice = None) | SaleInvoice.objects.filter(customer__full_name__contains=q.strip(), is_status=True, payment_invoice = None) | SaleInvoice.objects.filter(customer__email__contains=q.strip(), is_status=True, payment_invoice = None) | SaleInvoice.objects.filter(customer__phone_number__contains=q.strip(), is_status=True, payment_invoice = None).order_by('-created_at')
				print(data)
				return data
			else:
				data = SaleInvoice.objects.filter(is_status=True, payment_invoice = None).order_by('-created_at') 
				return data


class PaymentSaveView(SuccessMessageMixin, generic.ListView):
	model = SaleInvoice
	template_name = 'customer/save_payment.html'
	context_object_name = 'all_customer'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		myid = self.kwargs['invoice_no']
		try:
			inv = SaleInvoice.objects.get(invoice_number=myid)
		except SaleInvoice.DoesNotExist:
			return HttpResponse('<div style="text-alight:center;"> This invoce not exist in database. </div>')
		data = SaleInvoiceItem.objects.filter(invoice = inv)

		total_amount = 0 
		discount = 0
		pay_amount = 0
		receive_amount = 0 
		remain = 0

		all_sale = []

		for i in data:
			sub_total = 0
			unit = i.unit
			unit_price = i.unit_price
			if i.discount:
				mytotal = unit_price * unit
				# mydiscount = (mytotal * i.discount)/100
				mydiscount = i.discount * unit_price
				sub_total = mytotal - mydiscount
				total_amount = total_amount + sub_total
			else:
				sub_total = unit_price * unit
				total_amount = total_amount + sub_total

		all_sale.append({'total_amount':total_amount, 'discount':discount, 'pay_amount':total_amount, 'receive_amount': receive_amount, 'remain':total_amount})

		return render(request, self.template_name, {'all_customer':all_sale, 'invoice_no':myid})

class MakeSavePayment(SuccessMessageMixin, View):
	context_object_name = 'all_customer'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	@method_decorator(login_required(''))
	def post(self, request):
		success_message = "Pay successfully."
		if request.method == 'POST':

			invoice_no = request.POST.get('invoice_no')
			total_amount = request.POST.get('itotal_amount')
			discount = request.POST.get('discount')
			pay_amount = request.POST.get('ipay_amount')
			receive_amount = request.POST.get('receive_amount')
			remaining = request.POST.get('iremain')
			try:
				d_invoice = SaleInvoice.objects.get(invoice_number=str(invoice_no), is_status=True)
				sc = SaleInvoiceItem.objects.filter(invoice=d_invoice, is_status=True)
				if sc.count() > 0:
					try:
						Payment.objects.filter(invoice=d_invoice, is_status=True).delete()
						# Payment.objects.filter(invoice=d_invoice, is_status=True)
					except Payment.DoesNotExist:
						HttpResponse("Payment doesn't exist.")
			except SaleInvoice.DoesNotExist:
				HttpResponse("This invoice doesn't exist.")

			try:
				if float(remaining) > 0:
					b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain=remaining, pay_status = 'OWE')
					b_payment.save()
				else:
					b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain=remaining, pay_status = 'FULL')
					b_payment.save()
				return redirect('customer:save_list')
				# return super(OweClient, self).get(request, *args, **kwargs)
			except Payment.DoesNotExist:
				return HttpResponse('<div style="text-alight:center;"><h4><code> Payment not exist. </code></h4></div>')

		else:
			return HttpResponse('<div style="text-alight:center;"><h4><code> Invalid form. </code></h4></div>')


