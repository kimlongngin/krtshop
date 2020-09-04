# from django.shortcuts import render, redirect, get_object_or_404, Http404, render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader 
from django.views import generic
from django.urls import reverse_lazy


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.views.generic import View, TemplateView 
from product.models import Product, ProductInStock, ProductCategory
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from .forms import ProductSearchForm
from django.template import loader 
from django.views.generic.list import ListView
from django.contrib import messages
from django.http import JsonResponse

from django.core.paginator import Paginator


class RateView(View):
	def get(self, request):
		print("create")
		print('loading ajax')
		data = request.GET('productID')
		print(data)
		return HttpResponse(data)

class IndexView(SuccessMessageMixin, generic.ListView):
	template_name =  'product/index.html'
	context_object_name = 'all_product'
	paginate_by = 20

	def get_queryset(self):
		return Product.objects.filter(is_status=True).order_by('-created_at')

class DetailView(generic.DetailView):
	template_name =  'product/detail.html'

	def get(self, request, *args, **kwargs):
		# print(self.kwargs['pk'])
		
		if self.kwargs['pk']:
			try:
				data = Product.objects.filter(id=self.kwargs['pk'], is_status=True)
				if data:
					# Product.save(update_fields=["active"]) 
					ireview = data[0].review
					ireview = ireview + 1
					Product.objects.filter(id = self.kwargs['pk'] ).update(review = ireview)

				return render(request, self.template_name, {'products':data})

			except Product.DoesNotExist:
				raise Http404(" Data does not exist")
		else:
			raise Http404("Please check your data again.")


class SearchProductView(ListView):
	model = Product
	template_name = 'product/result_search.html'
	paginate_by = 100

	
	def get(self, request): 
		q = request.GET['q']
		data = Product.objects.filter(name__contains=q.strip(), is_status=True) | Product.objects.filter(product_number = q.strip(), is_status=True) | Product.objects.filter(serial_number=q.strip(), is_status=True)
		return render(request, self.template_name, {'all_product':data, 'title':q})


class ProductInStockView(SuccessMessageMixin, generic.ListView):

	model = ProductInStock
	template_name = 'product/stock_view.html'
	context_object_name = 'all_product_in_stock'
	paginate_by = 300



	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)


	def get(self, request):

		user = request.user
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
				sub_product_amount = 0
				iunit = 0

				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 
							iunit = iunit + p.unit
						else:
							product_stock = product_stock + p.amount

						sub_product_amount = sub_product_amount + p.amount
						

				if i.sale_invoice_item_product.all():

					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit
					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
				
					all_product_stock.append({'product_code': i.product_number, 'id':i.id, 'name':i.name, 'product_type':i.product_type, 'sub_amount':sub_product_amount, 'product_per_amount':i.product_type.amount, 'iunit':iunit, 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
				
				else:
					if product_stock > 0:
						all_product_stock.append({'product_code': i.product_number,'id':i.id, 'name':i.name, 'product_type':i.product_type, 'sub_amount':sub_product_amount, 'product_per_amount':i.product_type.amount, 'iunit':iunit, 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
					else:
						all_product_stock.append({'product_code': i.product_number,'id':i.id, 'name':i.name, 'product_type':i.product_type, 'sub_amount':sub_product_amount, 'product_per_amount':i.product_type.amount, 'iunit':iunit, 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
		
		return render(request, self.template_name, {'all_product_in_stock':all_product_stock})


class CategoryListView(SuccessMessageMixin, generic.ListView):
	model = ProductCategory
	template_name = 'product/category_list.html'
	context_object_name = 'all_product_category_ist'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		return ProductCategory.objects.filter(is_status=True).order_by('-created_at')
		

class CategoryProductView(SuccessMessageMixin, generic.ListView):
		
	model = ProductCategory
	template_name = 'product/category_product.html'
	context_object_name = 'all_product'
	paginate_by = 100

	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):

		if self.kwargs['pk']:
			try:
				page_num = 20
				data = Product.objects.filter(product_category=self.kwargs['pk'], is_status=True)
				paginator = Paginator(data, page_num) # Show 25 contacts per page

				page = request.GET.get('page')
				contacts = paginator.get_page(page)

				return render(request, self.template_name, {'all_product':contacts, 'cate_name': self.kwargs['cate_name'], 'paginator_num':page_num, 'all_data':data })

			except Product.DoesNotExist:
				raise Http404(" Data does not exist")
		else:
			raise Http404("Please check your data again.")


import xlwt
class ExportStock(generic.ListView):


	@method_decorator(login_required(''))
	def dispatch(self, request, *args, **kwargs):	
		return super(self.__class__, self).dispatch(request, *args, **kwargs)


	def get(self, request):


		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="stock_product.xls"'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('User_search_invoice')

	    # Sheet header, first row
		row_num = 0
		font_style = xlwt.XFStyle()
		font_style.font.bold = True


		columns = ['No', 'Code', 'Name', 'Product Type', 'Unit', 'Qty/Unit', 'Sub Product', 'Price', 'Special Price', 'Remaining',  ]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		icount = 0
		n = 0 



		user = request.user
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
				sub_product_amount = 0
				iunit = 0

				if i.product_in_stock.all():
					# check product in stock
					for p in i.product_in_stock.all():
						
						if p.unit > 0:
							product_stock = product_stock + (p.unit *i.product_type.amount) + p.amount 
							iunit = iunit + p.unit
						else:
							product_stock = product_stock + p.amount

						sub_product_amount = sub_product_amount + p.amount
						

				if i.sale_invoice_item_product.all():

					for item in i.sale_invoice_item_product.all():
						total_product_sale = total_product_sale + item.unit
					product_left = product_stock - total_product_sale # calculate product that sale in saleproductitem model
				
					all_product_stock.append({'product_code': i.product_number, 'id':i.id, 'name':i.name, 'product_type':i.product_type, 'sub_amount':sub_product_amount, 'product_per_amount':i.product_type.amount, 'iunit':iunit, 'unit':total_product_sale, 'total_product':product_left, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
				
				else:
				
					if product_stock > 0:
						all_product_stock.append({'product_code': i.product_number,'id':i.id, 'name':i.name, 'product_type':i.product_type, 'sub_amount':sub_product_amount, 'product_per_amount':i.product_type.amount, 'iunit':iunit, 'unit':total_product_sale, 'total_product':product_stock, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })
					else:
						all_product_stock.append({'product_code': i.product_number,'id':i.id, 'name':i.name, 'product_type':i.product_type, 'sub_amount':sub_product_amount, 'product_per_amount':i.product_type.amount, 'iunit':iunit, 'unit':total_product_sale, 'total_product':0, 'default_image':i.default_image, 'price': i.price, 'special_price':i.special_price })


			

			for j in all_product_stock:
				
				all_rows = []
				n += 1
				code = j['product_code']
				name = j['name']
				product_type = j['product_type'].title
				sub_amount = j['sub_amount']
				product_per_amount = j['product_per_amount']
				sub_product = j['sub_amount']
				iunit = j['iunit']
				unit = j['unit']
				price = j['price']
				special_price = j['special_price']
				total_product = j['total_product']

				all_rows = [n, code, name, product_type, sub_product, iunit, unit, price, special_price, total_product]
				col_num = 0
				for index in all_rows:
					ws.write(n, col_num, index, font_style)
					col_num +=1
			wb.save(response)
			return response

	

