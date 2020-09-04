
import io
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.http import HttpResponse, JsonResponse, FileResponse

from django.template import loader 
from django.views import generic
from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.views.generic import View, TemplateView 
from product.models import Product, Promotion, ProductCategory, StockLocation, ProductInStock
from customer.models import Customer, SaleInvoiceItem, Payment, SaleInvoice

from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.template import loader 
from django.views.generic.list import ListView
from django.contrib import messages
from django.core.paginator import Paginator
from django.core import serializers
import json
from datetime import date, datetime, timedelta, time
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from django.db.models import Count, Sum
from reportlab.lib.units import cm


import datetime

from django.contrib.admin.models import LogEntry, ADDITION
class SellHistoryView(generic.ListView):
	template_name = 'sell/sell_history.html'
	context_object_name = 'all_history'
	paginate_by = 30

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
		today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
		data =LogEntry.objects.select_related().filter(action_time__range=(today_min, today_max)).order_by('-action_time')
		if data: 
			return data 
		else:
			data =LogEntry.objects.select_related().filter().order_by('-action_time')
		return data



def increment_invoice_number():
	last_invoice = SaleInvoice.objects.all().order_by('id').last()
	if not last_invoice:
		return 'INV000001'
	width = 6
	invoice_number = last_invoice.invoice_number
	invoice_int = int(invoice_number.split('INV')[-1])
	new_invoice_int = invoice_int + 1
	formatted = (width - len(str(new_invoice_int))) * "0" + str(new_invoice_int)
	new_invoice_int = 'INV' + str(formatted)
	return str(new_invoice_int)


class SaleView(SuccessMessageMixin, generic.ListView):
	template_name = 'sell/sale.html'
	context_object_name = 'all_categories'
	paginate_by = 500
	

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)
		
	def get(self, request, *args, **kwargs):
		today = date.today()
		user = request.user

		invoice_number = increment_invoice_number()
		customer = Customer.objects.filter(is_status=True).order_by('-full_name')
		data = ProductCategory.objects.filter(is_status=True).order_by('-created_at')
		
		products = Product.objects.filter(is_status=True).order_by('-created_at')  
		today_sale = SaleInvoice.objects.filter(is_status=True, created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)		
		Location_Id = StockLocation.objects.filter(controller=user, is_status=True)

		all_product_stock = []
		product_stock = 0
		total_product_sale = 0
		product_left = 0

		if products:
			for i in products:
				product_stock = 0
				total_product_sale = 0
				product_left = 0
				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 
						else:
							product_stock = product_stock + p.amount

				if i.sale_invoice_item_product.all():
					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit

					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
					
					all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
					
				else:
					if product_stock > 0:
						all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
						
					else:
						all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
		
		all_sales = []
		total = 0
		is_payment = 0
		if today_sale:
			for i in today_sale:
				if i.sale_invoice.all():
					for j in i.sale_invoice.all():
						if int(j.discount > 0): 
							sub_total = j.unit * j.unit_price 
							# discount = (sub_total * j.discount)/100
							discount = j.discount * j.unit_price
							itotal = sub_total - discount
							total = total + itotal
						else:
							sub_total = j.unit * j.unit_price 
							total = total + sub_total

				#  GET data from Payment table
				pay_amount = 0
				receive_amount = 0
				if i.payment_invoice.all():
					is_payment = 1
					for p in i.payment_invoice.all():
						pay_amount = p.pay_amount
						receive_amount = p.receive_amount
				else:
					is_payment = 0
				# all_sales.append({"pay_amount":pay_amount, "receive_amount":receive_amount, "itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":full_name, "customer":customer_name, "created_at": date_time})	
				all_sales.append({"is_payment":is_payment, "pay_amount":pay_amount, "receive_amount":receive_amount, "itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":i.user, "customer":i.customer, "created_at":i.created_at})	
				total = 0
				
		return render(request, self.template_name, {'all_product_stock': all_product_stock, 'sale_today':all_sales, 'all_customers':customer, 'all_categories': data, 'all_products':products, 'invoice_number': invoice_number, 'user':user}) 


def filter_category(request):
	if request.is_ajax():
		id = request.GET['myid']
		
		products = Product.objects.filter(product_category__id = id, is_status=True).order_by('-created_at')
		all_product_stock = []
		product_stock=0
		total_product_sale = 0
		product_left = 0

		
		if products:
			for i in products:
				product_stock = 0
				total_product_sale = 0
				product_left = 0
				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 

						else:
							product_stock = product_stock + p.amount

				if i.sale_invoice_item_product.all():
					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit

					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
					
					all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
					
				else:
					if product_stock > 0:
						all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						
					else:
						all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						



		return HttpResponse(json.dumps(all_product_stock), content_type="application/json")

		# data = serializers.serialize('json', Product.objects.filter(product_category__id = id, is_status=True).order_by('-created_at') )
		# return HttpResponse(data, content_type="application/json")	
	else:
		return HttpResponse("<h1> Welcome !!! </h1>")

def filter_product(request):

	if request.is_ajax():
		key_term = request.GET['key_term']

		products = Product.objects.filter(name__contains=key_term.strip(), is_status=True) | Product.objects.filter(product_number = key_term.strip(), is_status=True) | Product.objects.filter(serial_number=key_term.strip(), is_status=True)
		all_product_stock = []
		product_stock=0
		total_product_sale = 0
		product_left = 0
		
		
		if products:
			for i in products:
				product_stock = 0
				total_product_sale = 0
				product_left = 0
				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 

						else:
							product_stock = product_stock + p.amount

				if i.sale_invoice_item_product.all():
					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit

					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
					
					all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
					
				else:
					if product_stock > 0:
						all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						
					else:
						all_product_stock.append({'id':i.id, 'name':i.name, 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						
		return HttpResponse(json.dumps(all_product_stock), content_type="application/json")
		
		# stock = serializers.serialize('json', all_product_stock)
		# return HttpResponse(stock, content_type="application/json")
		

		# data = serializers.serialize('json', Product.objects.filter(name__contains=key_term, is_status=True) | Product.objects.filter(product_number = key_term, is_status=True) | Product.objects.filter(serial_number=key_term, is_status=True))
		# return HttpResponse({'result':data, 'covert_object':stock }, content_type="application/json")
	else:
		return HttpResponse("<h1> Welcome !!! </h1>")

def filter_customer(request):

	if request.is_ajax():
		key_term = request.GET['key_term']
		data = serializers.serialize('json', Customer.objects.filter(full_name__contains=key_term.strip(),  is_status=True).order_by('full_name') | Customer.objects.filter(email__contains=key_term.strip(),  is_status=True).order_by('full_name') | Customer.objects.filter(phone_number__contains=key_term.strip(),  is_status=True).order_by('full_name'))
		
		return HttpResponse(data, content_type="application/json")
		
	else:
		return HttpResponse("<h1> Welcome !!! </h1>")

def make_invoice_payment(request):

	if request.is_ajax():
		invoice_no = request.GET['myinvoice_no']
		client_key = request.GET['client_key']
		user = request.user
		sale_product = request.GET['sale_item']
		data_product = json.loads(sale_product) # Extract array objects 
		is_payment = 0
		
		# print('sell product')
		# print(sale_product)

		# Check customer
		try:
			s_customer = Customer.objects.get(pk = client_key)
		except Customer.DoesNotExist:
			# mydata['data'] = 'Customer does not exist!'
			return HttpResponse({'data':'Customer does not exist!'}, content_type="application/json")
		
		# Check exist of sale invoice items
		try:
			s_invoice = SaleInvoice.objects.get(invoice_number=invoice_no, is_status=True)
		except SaleInvoice.DoesNotExist:
			Binvoice = SaleInvoice(invoice_number = invoice_no, user=user, customer = s_customer, description="Auto save from front end.")
			Binvoice.save()
		n_invoice = SaleInvoice.objects.get(invoice_number=invoice_no, is_status=True)

		if n_invoice:
			
			# Incase the same Invoice_ID multiople save, so First delete it and then save the last one.
			SaleInvoiceItem.objects.filter(invoice=n_invoice, is_status=True).delete()
			for i in data_product:
				p_id = i["Id"]
				try:
					s_product = Product.objects.get(id=p_id, is_status=True)
				except Product.DoesNotExist:
					SaleInvoice.objects.filter(invoice_number=invoice_no).delete()
					return HttpResponse("Product number does not exist")

				p_unit = i["Unit"]
				p_price = i["Price"]
				p_special_price = i["Special_price"]
				p_discount = i["Discount"]
			
				if s_product:
					if float(p_special_price) > 0:
						b_sale_item = SaleInvoiceItem(invoice=n_invoice, product=s_product, unit=p_unit, unit_price = p_special_price, discount=p_discount, description="Auto save item.")
						b_sale_item.save()
					else:
						b_sale_item = SaleInvoiceItem(invoice=n_invoice, product=s_product, unit=p_unit, unit_price = p_price, discount=p_discount, description="Auto save item.")
						b_sale_item.save() 

			
			sc = SaleInvoiceItem.objects.filter(invoice=n_invoice, is_status=True)
			if sc.count() > 0:
				try:
					Payment.objects.filter(invoice=n_invoice, is_status=True).delete()
				except Payment.DoesNotExist:
					print("Error delete payment")

				total_amount = request.GET['total_amount']
				discount = request.GET['discount']
				pay_amount = request.GET['pay_amount']
				receive_amount = request.GET['receive_amount']
				remain = request.GET['remain']
				if float(remain) > 0:
					b_payment = Payment(invoice=n_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain =remain, pay_status = 'OWE')
					b_payment.save()
				else:
					b_payment = Payment(invoice=n_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain =remain,  pay_status = 'FULL')
					b_payment.save()
			else:
				SaleInvoiceItem.objects.filter(invoice=n_invoice, is_status=True).delete()
				return HttpResponse("Please save invoice item first.")


		#  Select all sale today to display on the sale page.
		today = date.today()
		today_sale = SaleInvoice.objects.filter(is_status=True, created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)
		

		products = Product.objects.filter(is_status=True).order_by('-created_at')  
		today_sale = SaleInvoice.objects.filter(is_status=True, created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)		
		Location_Id = StockLocation.objects.filter(controller=user, is_status=True)

		all_product_stock = []
		product_stock = 0
		total_product_sale = 0
		product_left = 0

		
		if products:
			for i in products:
				product_stock = 0
				total_product_sale = 0
				product_left = 0
				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 

						else:
							product_stock = product_stock + p.amount

				if i.sale_invoice_item_product.all():
					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit

					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
					
					all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
					
				else:
					if product_stock > 0:
						all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						
					else:
						all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
		
		all_sales = []
		total = 0
		if today_sale:
			for i in today_sale:
				
				if i.sale_invoice.all():
					for j in i.sale_invoice.all():
						if int(j.discount > 0): 
							sub_total = j.unit * j.unit_price  
							# discount = (sub_total * j.discount)/100 
							discount = j.discount * j.unit_price
							print('each discount: ', j.discount, discount)


							itotal = sub_total - discount 
							total = total + itotal 
						else: 
							sub_total = j.unit * j.unit_price 
							total = total + sub_total
				


				full_name = i.user.first_name + '' + i.user.last_name
				customer_name = i.customer.full_name
				date_time = str(i.created_at)

				#  GET data from Payment table
				pay_amount = 0
				receive_amount = 0
				if i.payment_invoice.all():
					is_payment = 1
					for p in i.payment_invoice.all():
						pay_amount = p.pay_amount
						receive_amount = p.receive_amount
				else: 
					is_payment = 0

				all_sales.append({"is_payment": is_payment, "pay_amount":pay_amount, "receive_amount":receive_amount, "itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":full_name, "customer":customer_name, "created_at": date_time})	
				total = 0
		return HttpResponse(json.dumps({'result': all_sales, 'all_products':all_product_stock}), content_type="application/json")
		
	else:
		return HttpResponse(json.dumps({'result': 'Payment unsuccess, please recheck your list.'}), content_type="application/json")


@csrf_protect
def save_order_product_list(request):

	if request.is_ajax():
		invoice_no = request.GET['invoice_no']
		client_key = request.GET['client_key']
		user = request.user
		sale_product = request.GET['sale_item']

		data_product = json.loads(sale_product)
		
		s_customer = ''
		s_invoice = ''
		# Check customer
		try:
			s_customer = Customer.objects.get(pk = client_key)
		except Customer.DoesNotExist:
			# mydata['data'] = 'Customer does not exist!'
			return HttpResponse({'data':'Customer does not exist!'}, content_type="application/json")
		
		# Check exist of sale invoice items
		try:
			s_invoice = SaleInvoice.objects.get(invoice_number=invoice_no, is_status=True)
		except SaleInvoice.DoesNotExist:
			Binvoice = SaleInvoice(invoice_number = invoice_no, user=user, customer = s_customer, description="Save")
			Binvoice.save()

		if s_invoice:
			SaleInvoice.objects.filter(invoice_number=invoice_no, is_status=True).update(invoice_number = invoice_no, user=user, customer = s_customer, description="Update")
		

		n_invoice = SaleInvoice.objects.get(invoice_number=invoice_no, is_status=True)
		if n_invoice:

			# Incase the same Invoice_ID multiople save, so First delete it and then save the last one.
			SaleInvoiceItem.objects.filter(invoice=n_invoice, is_status=True).delete()

			for i in data_product:
				p_id = i["Id"]
				try:
					s_product = Product.objects.get(id=p_id, is_status=True)
				except Product.DoesNotExist:
					SaleInvoice.objects.filter(invoice_number=invoice_no).delete()
					return HttpResponse("Product number does not exist")

				p_unit = i["Unit"]
				p_price = i["Price"]
				p_special_price = i["Special_price"]
				p_discount = i["Discount"]


				if s_product:
					
					if float(p_special_price) > 0:
						b_sale_item = SaleInvoiceItem(invoice=n_invoice, product=s_product, unit=p_unit, unit_price = p_special_price, discount=p_discount, description="Auto save item.")
						b_sale_item.save()
					else:
						b_sale_item = SaleInvoiceItem(invoice=n_invoice, product=s_product, unit=p_unit, unit_price = p_price, discount=p_discount, description="Auto save item.")
						b_sale_item.save() 
		today = date.today()
		today_sale = SaleInvoice.objects.filter(is_status=True, created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)
		

		products = Product.objects.filter(is_status=True).order_by('-created_at')  
		Location_Id = StockLocation.objects.filter(controller=user, is_status=True)

		all_product_stock = []
		product_stock = 0
		total_product_sale = 0
		product_left = 0

		
		if products:
			for i in products:
				product_stock = 0
				total_product_sale = 0
				product_left = 0
				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 

						else:
							product_stock = product_stock + p.amount

				if i.sale_invoice_item_product.all():
					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit

					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
					
					all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
					
				else:
					if product_stock > 0:
						all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						
					else:
						all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })


		all_sales = []
		total = 0
		is_payment = 0
		if today_sale:
			for i in today_sale:
				if i.sale_invoice.all():
					for j in i.sale_invoice.all():
						if int(j.discount > 0): 
							sub_total = j.unit * j.unit_price 
							# discount = (sub_total * j.discount)/100
							discount = j.discount * j.unit_price 
							itotal = sub_total - discount
							total = total + itotal
						else:
							sub_total = j.unit * j.unit_price 
							total = total + sub_total

				full_name = i.user.first_name + '' + i.user.last_name
				customer_name = i.customer.full_name
				date_time = str(i.created_at)

				#  GET data from Payment table
				pay_amount = 0
				receive_amount = 0
				if i.payment_invoice.all():
					for p in i.payment_invoice.all():
						pay_amount = p.pay_amount
						receive_amount = p.receive_amount

					is_payment = 1
				else: 
					is_payment = 0

				all_sales.append({"is_payment":is_payment, "pay_amount":pay_amount, "receive_amount":receive_amount, "itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":full_name, "customer":customer_name, "created_at": date_time})	
				total = 0
				# all_sales.append({"itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":full_name, "customer":customer_name, "created_at": date_time})			

		# data = serializers.serialize('json', {'result': all_sales})
		# print(data)
		return HttpResponse(json.dumps({'result': all_sales, 'all_products':all_product_stock}), content_type="application/json")
		
	else:
		return HttpResponse("<h1> Welcome !!! </h1>")


def cancel_selling(request):
	myinvoice_no = ''
	if request.is_ajax():
		invoice_no = request.GET['invoice_no']
		
		if invoice_no:
			try:
				SaleInvoice.objects.filter(invoice_number=invoice_no, is_status=True).delete()
			except Product.DoesNotExist:
				return HttpResponse(json.dumps({'result': 'Invoice number does not exist.'}), content_type="application/json")

			today = date.today()
			today_sale = SaleInvoice.objects.filter(is_status=True, created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)
			products = Product.objects.filter(is_status=True).order_by('-created_at')  
		
			all_product_stock = []
			product_stock = 0
			total_product_sale = 0
			product_left = 0
			
			if products:
				for i in products:
					product_stock = 0
					total_product_sale = 0
					product_left = 0
					if i.product_in_stock.all():
						# check product in stock
						for p in i.product_in_stock.all():
							if p.unit > 0:
								product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 

							else:
								product_stock = product_stock + p.amount

					if i.sale_invoice_item_product.all():
						for item in i.sale_invoice_item_product.all():
							total_product_sale = total_product_sale + item.unit

						product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
						
						all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						
					else:
						if product_stock > 0:
							all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
							
						else:
							all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })

			all_sales = []
			total = 0
			is_payment = 0
			if today_sale:
				for i in today_sale:
					if i.sale_invoice.all():
						for j in i.sale_invoice.all():
							if int(j.discount > 0): 
								sub_total = j.unit * j.unit_price 
								discount = (sub_total * j.discount)/100
								itotal = sub_total - discount
								total = total + itotal
							else:
								sub_total = j.unit * j.unit_price 
								total = total + sub_total

					full_name = i.user.first_name + '' + i.user.last_name
					customer_name = i.customer.full_name
					date_time = str(i.created_at)

					#  GET data from Payment table
					pay_amount = 0
					receive_amount = 0
					if i.payment_invoice.all():
						for p in i.payment_invoice.all():
							pay_amount = p.pay_amount
							receive_amount = p.receive_amount
						is_payment = 1
					else: 
						is_payment = 0
					all_sales.append({"is_payment":is_payment, "pay_amount":pay_amount, "receive_amount":receive_amount, "itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":full_name, "customer":customer_name, "created_at": date_time})	
					total = 0
			myinvoice_no = increment_invoice_number()

			return HttpResponse(json.dumps({'result': all_sales, 'all_products':all_product_stock, 'invoice_no':myinvoice_no}), content_type="application/json")

		return HttpResponse(json.dumps({'result': 'Unsuccess selling.'}), content_type="application/json")

	return HttpResponse(json.dumps({'result': 'Unsuccess selling.'}), content_type="application/json")

def check_invoice_product_list(request):
	myinvoice_no = ''
	if request.is_ajax():
		invoice_no = request.GET['invoice_no']
		try:
			s_invoice = SaleInvoice.objects.get(invoice_number=invoice_no, is_status=True)
			myinvoice_no = increment_invoice_number()
		except SaleInvoice.DoesNotExist:
			return HttpResponse(json.dumps({'result': 'please save invoice first.'}), content_type="application/json")  
		
		return HttpResponse(json.dumps({'result': 'Invoice already saved to list.', 'invoice_no':myinvoice_no}), content_type="application/json")
	else:
		return HttpResponse('<h3> Hello world! </h3>')


def update_order(request):

	objsale = []
	if request.is_ajax():
		invoice_no = request.GET['invoice_no']

		try:
			n_invoice = SaleInvoice.objects.get(invoice_number=invoice_no, is_status=True)

			objSale = SaleInvoiceItem.objects.filter(invoice=n_invoice, is_status=True)

			'''var id = data[i].fields.product;
			var unit = data[i].fields.unit;
			var price = data[i].fields.unit_price;
			var discount = data[i].fields.discount;
			var price_per_unit = price * unit;'''

			b_payment = 0 # 0 is doesn't has in table, but 1 has in stock

			try: 
				Payment.objects.get(invoice=n_invoice)
				b_payment = 1
			except Payment.DoesNotExist:
				b_payment = 0
			
			for i in objSale: 
				pro_id = ''
				pro_name = ''
				if i.product: 
					pro_id = i.product.id
					pro_name = i.product.name
				unit = i.unit
				price =i.unit_price 
				discount = i.discount 
				objsale.append({'product_id':pro_id, 'product_name':pro_name, 'unit':unit, 'unit_price':price, 'discount':discount})

		
			# invoice_id = serializers.serialize('json', n_invoice)
			data = serializers.serialize('json', SaleInvoiceItem.objects.filter(invoice=n_invoice, is_status=True))

			return HttpResponse(json.dumps({'result':objsale, 'is_payment':b_payment }),content_type="application/json")

			# return HttpResponse(data)

		except SaleInvoice.DoesNotExist:
			return HttpResponse(json.dumps({'result': 'This invoice number does not have in list.'}), content_type="application/json")  
		
	else:
		return HttpResponse('<h3> Update producted. </h3>')

def delete_invoice(request):
	myinvoice_no = ''
	if request.is_ajax():
		invoice_no = request.GET['invoice_no']
		try:
			SaleInvoice.objects.filter(invoice_number=invoice_no, is_status=True).delete()
		except SaleInvoice.DoesNotExist:
			return HttpResponse("Invoice doesn't exist.")

		today = date.today()
		today_sale = SaleInvoice.objects.filter(is_status=True, created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)
		products = Product.objects.filter(is_status=True).order_by('-created_at')  
	
		all_product_stock = []
		product_stock = 0
		total_product_sale = 0
		product_left = 0
			
		if products:
			for i in products:
				product_stock = 0
				total_product_sale = 0
				product_left = 0
				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 

						else:
							product_stock = product_stock + p.amount

				if i.sale_invoice_item_product.all():
					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit

					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
					
					all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
					
				else:
					if product_stock > 0:
						all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })
						
					else:
						all_product_stock.append({'id':i.id, 'name':str(i.name), 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image.url, 'price': i.price, 'special_price':i.special_price })

			all_sales = []
			total = 0
			is_payment = 0
			if today_sale:
				for i in today_sale:
					if i.sale_invoice.all():
						for j in i.sale_invoice.all():
							if int(j.discount > 0): 
								sub_total = j.unit * j.unit_price 
								discount = (sub_total * j.discount)/100
								itotal = sub_total - discount
								total = total + itotal
							else:
								sub_total = j.unit * j.unit_price 
								total = total + sub_total

					full_name = i.user.first_name + '' + i.user.last_name
					customer_name = i.customer.full_name
					date_time = str(i.created_at)

					#  GET data from Payment table
					pay_amount = 0
					receive_amount = 0
					if i.payment_invoice.all():
						for p in i.payment_invoice.all():
							pay_amount = p.pay_amount
							receive_amount = p.receive_amount
						is_payment = 1
					else: 
						is_payment = 0
					all_sales.append({"is_payment":is_payment, "pay_amount":pay_amount, "receive_amount":receive_amount, "itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":full_name, "customer":customer_name, "created_at": date_time})	
					total = 0

			myinvoice_no = increment_invoice_number()
			return HttpResponse(json.dumps({'result': all_sales, 'all_products':all_product_stock, 'invoice_no':myinvoice_no}), content_type="application/json")

		return HttpResponse(json.dumps({'result': 'Delete unsucessful.'}), content_type="application/json")

	return HttpResponse(json.dumps({'result': 'Delete unsucessful.'}), content_type="application/json")


def sub_make_invoice_payment(request):
	if request.is_ajax():
		invoice_no = request.GET['invoice_no']
		payment_sales = []
		total = 0
		is_payment = 0

		invoice = invoice_no
		total_amount = 0
		discount = 0
		pay_amount = 0
		receive_amount = 0
		remain = 0
		pay_status = ''

		try:
			d_invoice = SaleInvoice.objects.get(invoice_number=str(invoice_no), is_status=True)
			d_payment = Payment.objects.filter(invoice=d_invoice, is_status=True )
			if d_payment:
				for i in d_payment:
					total_amount = i.total_amount
					discount = i.discount
					pay_amount = i.pay_amount
					receive_amount = i.receive_amount
					remain = i.remain
					pay_status = i.pay_status

				payment_sales.append({'invoice':invoice_no, 'total_amount':total_amount, 'discount':discount, 'pay_amount':pay_amount, 'receive_amount':receive_amount, 'remain':remain, 'pay_status': pay_status})

			else:
				d_saleitem = SaleInvoiceItem.objects.filter(invoice=d_invoice, is_status=True)

				if d_saleitem: 
					for i in d_saleitem:
						if int(i.discount > 0): 
							sub_total = i.unit * i.unit_price 
							# discount = (sub_total * i.discount)/100
							discount = i.discount * i.unit_price  
							itotal = sub_total - discount
							total = total + itotal
						else:
							sub_total = i.unit * i.unit_price 
							total = total + sub_total

					payment_sales.append({'invoice':invoice_no, 'total_amount':total, 'discount':0, 'pay_amount':total, 'receive_amount':0, 'remain':0, 'pay_status': ''})
		
			return HttpResponse(json.dumps({'result':payment_sales}), content_type="application/json")

		except SaleInvoice.DoesNotExist:
			return HttpResponse("Invoice doesn't exist.")
	else:
		return HttpResponse('Reject payment.')


def sub_make_payment(request):
	if request.is_ajax():
		invoice_no = request.GET['invoice_no']
		total_amount = request.GET['total_amount']
		discount = request.GET['discount']
		pay_amount = request.GET['pay_amount']
		receive_amount = request.GET['receive_amount']
		remain = request.GET['remain']
		
		try:
			d_invoice = SaleInvoice.objects.get(invoice_number=str(invoice_no), is_status=True)
			sc = SaleInvoiceItem.objects.filter(invoice=d_invoice, is_status=True)
			
			if sc.count() > 0:
				try:
					Payment.objects.filter(invoice=d_invoice, is_status=True).delete()
				except Payment.DoesNotExist:
					HttpResponse("Payment doesn't exist.")

				if float(remain) > 0:
					b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain =remain, pay_status = 'OWE')
					b_payment.save()
				else:
					b_payment = Payment(invoice=d_invoice, total_amount = total_amount, discount = discount, pay_amount = pay_amount, receive_amount = receive_amount, remain =remain,  pay_status = 'FULL')
					b_payment.save()
			else:
				return HttpResponse("Please re-check invoice item first.")

		except SaleInvoice.DoesNotExist:
			return HttpResponse("Invoice doesn't exist.")

		today = date.today()
		today_sale = SaleInvoice.objects.filter(is_status=True, created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)

		all_sales = []
		total = 0
		is_payment = 0
		if today_sale:
			for i in today_sale:
				if i.sale_invoice.all():
					for j in i.sale_invoice.all():
						if int(j.discount > 0): 
							sub_total = j.unit * j.unit_price 
							discount = (sub_total * j.discount)/100
							itotal = sub_total - discount
							total = total + itotal
						else:
							sub_total = j.unit * j.unit_price 
							total = total + sub_total

				full_name = i.user.first_name + '' + i.user.last_name
				customer_name = i.customer.full_name
				date_time = str(i.created_at)

				#  GET data from Payment table
				pay_amount = 0
				receive_amount = 0
				if i.payment_invoice.all():
					is_payment = 1
					for p in i.payment_invoice.all():
						pay_amount = p.pay_amount
						receive_amount = p.receive_amount
				else: 
					is_payment = 0
				all_sales.append({"is_payment":is_payment, "pay_amount":pay_amount, "receive_amount":receive_amount, "itotal":total, "id":i.id, "invoice_id":i.invoice_number, "user":full_name, "customer":customer_name, "created_at": date_time})	
				is_payment = 0
				total = 0
		myinvoice_no = increment_invoice_number()
		return HttpResponse(json.dumps({'result': all_sales, 'invoice_no':myinvoice_no}), content_type="application/json")
		# return HttpResponse(json.dumps({'result': 'Success payment'}), content_type="application/json")
	else:
		return HttpResponse(json.dumps({'result': 'error payment at server side.'}), content_type="application/json")


from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import pink, black, red, blue, green
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

sample_style_sheet = getSampleStyleSheet()
# if you want to see all the sample styles, this prints them
sample_style_sheet.list()


class RotatedImage(Image):
 
    def wrap(self, availWidth, availHeight):
        height, width = Image.wrap(self, availHeight, availWidth)
        return width, height
 
    def draw(self):
        self.canv.rotate(0)
        Image.draw(self)


class print_report(View):
	template_name='sell/print_report.html'
	product_sale = []
	@method_decorator(login_required(''))


	def get(self, request, *args, **kwargs):

		if self.kwargs['invoice_id']:
			invoice_no = self.kwargs['invoice_id']
			full_name = ''
			customer_name = ''
			unit = 0
			prince = 0
			discount = 0
			total = 0
			sub_total = 0
			igrand_total = 0


			grand_total = 0
			grand_discount = 0
			grand_pay_amount = 0
			grand_receive_amount = 0
			grand_remain = 0

			styles = getSampleStyleSheet()
			
			# container for the 'Flowable' objects
			elements = []
			response = HttpResponse(content_type='application/pdf')  
			response['Content-Disposition'] = 'attachment; filename="file.pdf"'  

			my_doc = SimpleDocTemplate('report.pdf', topMargin=0)


			pdf_buffer = BytesIO()
			my_doc = SimpleDocTemplate(pdf_buffer)
			flowables = []
			my_doc.build(flowables)


			# table head
			t_no = Paragraph(''' 
				<b>No<font color=white></font></b>
			 ''',  sample_style_sheet["BodyText"]) 
			t_product = Paragraph(''' 
				<b>Product<font color=white></font></b>
			 ''', sample_style_sheet["BodyText"])
			t_qty = Paragraph(''' 
				<b>Qty<font color=white></font></b>
			 ''', sample_style_sheet["BodyText"])
			t_unit = Paragraph(''' 
				<b>Unit<font color=white></font></b>
			 ''', sample_style_sheet["BodyText"])
			t_unit_price = Paragraph(''' 
				<b>Unit Price<font color=white></font></b>
			 ''', sample_style_sheet["BodyText"])
			t_discount = Paragraph(''' 
				<b>Free(Unit)<font color=white></font></b>
			 ''', sample_style_sheet["BodyText"])
			t_subtotal = Paragraph(''' 
				<b>Subtotal <font color=white></font></b>
			 ''',sample_style_sheet["BodyText"])
			t_total = Paragraph(''' 
				<b>Total<font color=white></font></b>
			 ''',sample_style_sheet["BodyText"])


			# Table body
			data= [[t_no, t_product, t_qty, t_unit_price, t_discount,  t_subtotal, t_total]]

			seller = request.user.first_name + ' ' + request.user.last_name
			d_invoice = SaleInvoice.objects.filter(invoice_number=str(invoice_no), is_status=True)
			n = 1
			product_name = ''
			for i in d_invoice: 
				full_name = i.user.first_name + '  ' + i.user.last_name
				customer_name = i.customer.full_name
				customer_contact = i.customer.phone_number
				customer_address = i.customer.address
				if i.sale_invoice.all():
					for j in i.sale_invoice.all():
						
						unit = j.unit
						price = j.unit_price
						discount = j.discount
						product_name = j.product
						my_grand_total = unit * price
						if discount > 0:
							unit_total = unit * price
							# dis_price = (unit_total * discount) / 100
							dis_price = price * discount
							sub_total = unit_total - dis_price  
							total = total + sub_total
						else:
							sub_total = unit * price
							total = total + sub_total

						igrand_total = igrand_total + my_grand_total
						data.append([n, product_name, unit, '$'+str(price)[:4], ' '+str(discount), '$'+str(igrand_total)[:4], '$'+str(sub_total)[:4]])
						n = n + 1

				if i.payment_invoice.all():
					for p in i.payment_invoice.all():
						grand_total = p.total_amount
						grand_discount = p.discount
						grand_pay_amount = p.pay_amount
						grand_receive_amount = p.receive_amount
						grand_remain = p.remain
				else:
					grand_total = total
					grand_discount = 0
					grand_pay_amount = total
					grand_receive_amount = 0
					grand_remain = total


			today = date.today()
			day = today.day
			month = today.month
			year = today.year
			spacing = 20

			# title of company
			p_title_of_company = Paragraph(''' 
				<para align=left><b> <font color=blue size=18> KR SKIN CARE </font></b></para>
			 ''',  sample_style_sheet["Heading1"])

			style_right = ParagraphStyle(name='right', parent=styles['Normal'], alignment=TA_RIGHT)
			orden = ParagraphStyle('orden')
			orden.leading = 14
			Story=[]
			t_right = ['Invoice No :'+ str(t_no)]

			# Customer Address
			p_customer_address = Paragraph(''' 
				<para align=left><b>ADDRESS: </b><i>''' + str(customer_address)+ '''</i><font color=black size=18></font></para>
			 ''',  sample_style_sheet["BodyText"])

			I = Image('MainView/static/image/user.png',100, 70)
		
			encabezado = [[I, p_title_of_company,  '']]
			tabla_encabezado = Table(encabezado, colWidths=[4 * cm, 11 * cm, 4 * cm])
			tabla_encabezado.setStyle(TableStyle(
	            [
	                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
	                ('VALIGN', (0, 0), (1, 0), 'CENTER'),
	            ]
        	))

			# Logo and TITLE
			tbl_head_data_title = [
			    [Paragraph(str(I), styles["Normal"]), Paragraph("<para align=center><b> <font color=blue size=18> KR SKIN CARE </font></b></para>", style_right)]
			]

			t_invoice_head_title = Table(tbl_head_data_title)

			# Invoice head title left and right
			tbl_head_data = [
			    [Paragraph("<br/><b>Address:</b> VengSreng Street, BE7 House, PreyLvea Village, ChomChao Commune, PorSenChey District, Phnom Penh City.", styles["Normal"]), Paragraph("<b>Invoice No:</b> <font color=red size=14>"+str(invoice_no) +"</font><br/><b>Tell: </b>077924447/095896565/081896565 <br/> <b>Day:</b> <i> "+ str(day) +" </i> <b>Month:</b> <i>"+ str(month) +" </i><b>Year:</b> <i>"+ str(year) +"</i>", style_right)]
			]
			t_invoice_head = Table(tbl_head_data)

			# title of Invoice
			p_title = Paragraph(''' 
				<para align=center><b><font color=blue size=18> Invoice</font></b></para>
			 ''',  sample_style_sheet["Heading1"])
			p_invoice_no = Paragraph('''
				<para align=center>'''+ str(invoice_no) +'''<br/><br/></para>
				''',sample_style_sheet['BodyText'])

			# Customer Name
			p_customer_name = Paragraph(''' 
				<para align=left><b>CUSTOMER NAME: </b><i>''' + str(customer_name)+ ''', ''' + str(customer_contact) + '''</i><font color=black size=18></font></para>
			 ''',  sample_style_sheet["BodyText"])

	
			flowables.append(tabla_encabezado)
			
			flowables.append(t_invoice_head)
			flowables.append(p_customer_name)
			flowables.append(p_customer_address)
			flowables.append(p_title)

			t=Table(data, rowHeights=1 * cm, style=[
			 ('GRID',(1,0),(-2,-2),1, colors.lavender),
			 ('BOX',(0,0),(1,-1),0,colors.lavender),
			 ('LINEABOVE',(1,2),(-2,2),0,colors.lavender),
			 ('LINEBEFORE',(2,1),(2,-2),0,colors.lavender),
			 # ('BACKGROUND', (0, 0), (0, 1), colors.pink),
			 # ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
			 # ('BACKGROUND', (2, 2), (2, 3), colors.orange),
			 ('BOX',(0,0),(-1,-1),0,colors.lavender),
			 ('GRID',(0,0),(-1,-1),1,colors.lavender),
			 ('VALIGN',(3,0),(3,0),'BOTTOM'),
			 ('BACKGROUND',(3,0),(3,0),colors.lavender),
			 ('BACKGROUND',(1,0),(1,0),colors.lavender),
			 ('BACKGROUND',(2,0),(2,0),colors.lavender),
			 ('BACKGROUND',(4,0),(4,0),colors.lavender),
			 ('BACKGROUND',(5,0),(5,0),colors.lavender),
			 ('BACKGROUND',(6,0),(6,0),colors.lavender),
			 ('BACKGROUND',(0,0),(0,0),colors.lavender),
			 # ('BACKGROUND',(3,1),(3,1),colors.khaki),
			 # ('ALIGN',(3,1),(3,1),'CENTER'),
			 # ('BACKGROUND',(3,2),(3,2),colors.beige),
			 # ('ALIGN',(3,2),(3,2),'LEFT'),
			])

			t._argW[3]=1.5*inch
			flowables.append(t)

			# Payment description
			t_grand_total = Paragraph(''' 
				<b>Grand Total: <font color=red></font></b><p>$'''+ str(grand_total) +'''</p>
			 ''',sample_style_sheet["BodyText"])
			t_grand_discount = Paragraph(''' 
				<b>Discount: <font color=red></font></b>'''+ str(grand_discount) +'''%</p>
			 ''',sample_style_sheet["BodyText"])
			t_grand_pay_amount = Paragraph(''' 
				<b>Pay amount: <font color=red></font></b>$'''+ str(grand_pay_amount) +'''</p>
			 ''',sample_style_sheet["BodyText"])
			t_grand_receive_amount = Paragraph(''' 
				<b>Receive amount: <font color=red></font></b>$'''+ str(grand_receive_amount) +'''</p>
			 ''',sample_style_sheet["BodyText"])
			t_grand_remain = Paragraph(''' 
				<b>Remaining: <font color=red></font></b>$'''+ str(grand_remain) +'''</p>
			 ''',sample_style_sheet["BodyText"])

			# Invoice head title left and right
			tbl_footer = [
			    [Paragraph("<b>Grand total: <font color=red></font></b><p>$"+ str(grand_total)[:4] 
			    	+"</p><br/><b>Discount: <font color=red></font></b><p>"+ str(grand_discount) +"%</p>"
			    	"<br/> <b>Pay amount: <font color=red></font></b><p>$"+ str(grand_pay_amount)[:4] +"</p>"
			    	+"<br/><b>Receive amount: <font color=red></font></b><p>$"+ str(grand_receive_amount)[:4] +"</p>"
			    	+"<br/><b>Remaining: <font color=red></font></b>$<p>"+ str(grand_remain)[:4] +"</p><br/><br/><br/><br/>", style_right)]
			]
			
			t_invoice_footer = Table(tbl_footer)
			flowables.append(t_invoice_footer)
			tbl_footer_fake = [
			    [Paragraph(" ", styles["Normal"]), Paragraph(" ", styles["Normal"]), Paragraph("<i>"+ str(full_name) + "</i>", style_right)]
			]
			i_tbl_footer_fake = Table(tbl_footer_fake)
			flowables.append(i_tbl_footer_fake)

			tbl_footer_dash = [
			    [Paragraph("<b>________________</b>", styles["Normal"]), Paragraph("<b>________________</b>", styles["Normal"]), Paragraph("<b>________________</b>", style_right)]
			]
			i_tbl_footer_dash = Table(tbl_footer_dash)
			flowables.append(i_tbl_footer_dash)
			tbl_footer_left_right_justify = [
			    [Paragraph("<b>Customer</b>", styles["Normal"]), Paragraph("<b>Deliver</b>", styles["Normal"]), Paragraph("<b>Seller</b>", style_right)]
			]
			i_tbl_footer_left_right_justify = Table(tbl_footer_left_right_justify)
			flowables.append(i_tbl_footer_left_right_justify)
			grand_total = 0
			my_doc.build(flowables)
			
		    # FileResponse sets the Content-Disposition header so that browsers
		    # present the option to save the file.
			pdf_value = pdf_buffer.getvalue()
			pdf_buffer.close()
			return HttpResponse(pdf_value, content_type='application/pdf')

