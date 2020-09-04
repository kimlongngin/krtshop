from django.db import models

from django.contrib.auth.models import User

from datetime import date
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from location.models import Location
from product.models import Product
from django.core.validators import RegexValidator

from django.forms import ModelForm


class Customer(models.Model):
	full_name = models.CharField(max_length=255, primary_key=True)
	phone_number = models.CharField(max_length=50)
	email = models.CharField(max_length=255, blank=True)
	province = models.ForeignKey(Location, related_name='province_location', on_delete=models.CASCADE)
	address = models.TextField()
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	is_status = models.BooleanField(default=True)

	def __str__ (self):
	 	return str(self.full_name)


	class Meta:
	    ordering = ['created_at']
	    def __unicode__(self):
	        return self.full_name


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

def getUser(self):
	if self.request.user.is_authenticated():
		return User



def validate_file_pdf(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')

def content_file_name(instance, filename):
	#return "files/users/%s/%s" % (request.user.id, filename)
    return '/'.join(['content', instance.user.username, filename])


class SaleInvoice(models.Model): 
	invoice_number = models.CharField(max_length=500, null=True, blank=True, 
        validators=[RegexValidator(regex='^[a-zA-Z0-9]*$',
        message='Produce number must be Alphanumeric',code='Number is invalide'),], 
        default=increment_invoice_number)
	user = models.ForeignKey(User, related_name='sale_invoice_user', on_delete=models.CASCADE) # who are sell this product
	customer = models.ForeignKey(Customer, related_name='sale_invoice_customer', on_delete=models.CASCADE)
	description= models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	is_status = models.BooleanField(default=True)

	def __str__ (self):
	 	return self.invoice_number 

	class Meta:
		ordering = ["-created_at", "-updated_at"]
		
STATUS_CHOICES = (
	('', ''),
	('FULL', 'Full'),
    ('OWE', 'Owe'),
)

class Payment(models.Model):
	invoice = models.ForeignKey(SaleInvoice, related_name='payment_invoice', on_delete = models.CASCADE)
	tax = models.FloatField(default=0.0, blank=True)
	total_amount = models.FloatField(default=0.0)
	discount = models.FloatField(default=0.0, blank=True) # Discount as percentage.
	pay_amount = models.FloatField(default=0.0)
	receive_amount = models.FloatField(default=0.0)
	remain = models.FloatField(default=0.0)
	pay_status = models.CharField(max_length=10, choices=STATUS_CHOICES)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	pay_date = models.DateTimeField(auto_now_add=True, blank=True)
	is_status = models.BooleanField(default=True)

	def __str__ (self):
	 	return str(self.invoice)

	class Meta:
		ordering = ["-created_at", "-updated_at"]
		def __unicode__(self):
			return self.invoice
	
class SaleInvoiceForm(ModelForm): 
	def __init__(self, *args, **kwargs): 
		super(SaleInvoiceForm, self).__init__(*args, **kwargs)                       
		self.fields['user'].disabled = True		
	class Meta:
		fields = ['user']
		# model = SaleInvoice
   


class SaleInvoiceItem(models.Model):
	invoice = models.ForeignKey(SaleInvoice, related_name='sale_invoice', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='sale_invoice_item_product', on_delete=models.CASCADE)
	unit= models.IntegerField(default=0) #Quantity in one product
	unit_price = models.FloatField(default=0.0, blank=True) # Price in per_unit
	discount = models.FloatField(default=0.0, blank=True) # Discount as percentage
	discount_unit = models.FloatField(default=0.0, blank=True) # Discount as unit
	description= models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	is_status = models.BooleanField(default=True)
	
	def __str__ (self):
		return str(self.invoice)

	class Meta:
		ordering = ["-created_at", "-updated_at"]


class SaleInvoiceItemHistory(models.Model):
	invoice = models.ForeignKey(SaleInvoice, related_name='sale_invoice_history', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='sale_invoice_item_product_history', on_delete=models.CASCADE)
	unit= models.IntegerField(default=0)
	unit_price = models.FloatField(default=0.0)
	description= models.TextField(blank=True)
	action = models.CharField(max_length=20, null=True, blank=True) # NO SVE, UPD, DEL
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	is_status = models.BooleanField(default=True)
	user = models.ForeignKey(User, related_name='sale_invoice_user_history', on_delete=models.CASCADE) # who are sell this product

	def __str__ (self):
			return str(self.invoice)
	class Meta:
		ordering = ["-created_at", "-updated_at"]




