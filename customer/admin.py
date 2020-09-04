from django.contrib import admin

from django.contrib.auth.models import User
from .models import Customer, SaleInvoice, SaleInvoiceItem, SaleInvoiceItemHistory, Payment
from product.models import Product
from django.contrib.auth.models import Group 
from django.contrib.admin.models import LogEntry, ADDITION
import os
from django.contrib.admin import helpers
from django.template.response import TemplateResponse

from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _, gettext_lazy
# from admin_auto_filters.filters import AutocompleteFilter


# class CustomerFilter(AutocompleteFilter):
#     title = 'Search customer' # display title
#     field_name = 'full_name' # name of the foreign key field

class PaymentAdmin(admin.ModelAdmin):
	list_display = ('invoice', 'pay_amount', 'remain', 'pay_status', 'created_at', 'pay_date')
	search_fields = ('invoice__invoice_number', 'pay_status', 'pay_date')

admin.site.register(Payment, PaymentAdmin)
		

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'phone_number', 'email', 'province', 'address', 'created_at', 'is_status')
	search_fields = ('full_name', 'phone_number', 'email', 'address')
	
admin.site.register(Customer, CustomerAdmin)


class SaleInvoiceAdmin(admin.ModelAdmin):
	list_display = ('invoice_number', 'user', 'customer','created_at', 'updated_at')
	search_fields = ('invoice_number', 'user__first_name', 'customer__full_name', 'created_at', 'updated_at')
	# readonly_fields = ('user')

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'user': 
			kwargs['queryset'] = User.objects.filter(username=request.user.username)
		return super(SaleInvoiceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

	# def get_readonly_fields(self, request, obj=None):
	# 	if obj is not None:
	# 	    return self.readonly_fields + ('user',)
	# 	return [self.readonly_fields]

	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			if obj is not None:
				return self.readonly_fields + ('user',)
			return [self.readonly_fields]
		else:
			if obj is None:
				return self.readonly_fields + ('user',)
			return []
	
	# Add current loggedin user into the dropdown field
	def add_view(self, request, form_url="", extra_context=None):
		data = request.GET.copy()
		data['user'] = request.user
		request.GET = data
		# return super(SaleInvoiceAdmin, self).add_view(request, form_url="", extra_context=extra_context)
		return super(SaleInvoiceAdmin, self).add_view(request, form_url="", extra_context=extra_context)

admin.site.register(SaleInvoice, SaleInvoiceAdmin)


class SaleInvoiceItemAdmin(admin.ModelAdmin):
	list_display = ('invoice','product', 'unit', 'unit_price', 'discount', 'created_at')
	search_fields = ('invoice__invoice_number', 'product__name')

	view_on_site = False
	# actions = ['delete_selected']
	list_per_page = 10 


	def delete_selected(modeladmin, request, queryset):
    
	    opts = modeladmin.model._meta
	    app_label = opts.app_label

	    # Populate deletable_objects, a data structure of all related objects that
	    # will also be deleted.
	    deletable_objects, model_count, perms_needed, protected = modeladmin.get_deleted_objects(queryset, request)

	    # The user has already confirmed the deletion.
	    # Do the deletion and return None to display the change list view again.
	    if request.POST.get('post') and not protected:
	        if perms_needed:
	            raise PermissionDenied
	        n = queryset.count()
	        if n:
	            for obj in queryset:
	                obj_display = str(obj)
	                modeladmin.log_deletion(request, obj, obj_display)
	                SaleItemHistory = SaleInvoiceItemHistory.objects.create(
						invoice = obj.invoice,
						product = obj.product,
						unit = obj.unit,
						unit_price = obj.unit_price,
						description = obj.description,
						created_at = obj.created_at,
						action = 'UPD',
						user = request.user )
	                SaleItemHistory.save()

	            modeladmin.delete_queryset(request, queryset)
	            modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
	                "count": n, "items": model_ngettext(modeladmin.opts, n)
	            }, messages.SUCCESS)
	        # Return None to display the change list page again.
	        return None

	    objects_name = model_ngettext(queryset)

	    if perms_needed or protected:
	        title = _("Cannot delete %(name)s") % {"name": objects_name}
	    else:
	        title = _("Are you sure?")

	    context = {
	        **modeladmin.admin_site.each_context(request),
	        'title': title,
	        'objects_name': str(objects_name),
	        'deletable_objects': [deletable_objects],
	        'model_count': dict(model_count).items(),
	        'queryset': queryset,
	        'perms_lacking': perms_needed,
	        'protected': protected,
	        'opts': opts,
	        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
	        'media': modeladmin.media,
	    }

	    request.current_app = modeladmin.admin_site.name

	    # Display the confirmation page
	    return TemplateResponse(request, modeladmin.delete_selected_confirmation_template or [
	        "admin/%s/%s/delete_selected_confirmation.html" % (app_label, opts.model_name),
	        "admin/%s/delete_selected_confirmation.html" % app_label,
	        "admin/delete_selected_confirmation.html"
	    ], context)

	delete_selected.allowed_permissions = ('delete',)

	delete_selected.short_description = "Delete all selected objects"


	def save_model(self, request, obj, form, change):
		obj.user = request.user
		objID = obj.id
		SaleObj = SaleInvoiceItem.objects.filter(id=objID, is_status="True").count()

		
		if SaleObj:
			super().save_model(request, obj, form, change)

			# Copy product to product's history table "ProductInStockHistory" => Action "UPD"
			# 1 if check this product has in the table then, this script is for update buttion, 
			# 2 otherwise is for save button
			SaleItemHistory = SaleInvoiceItemHistory.objects.create(
				invoice = obj.invoice,
				product = obj.product,
				unit = obj.unit,
				unit_price = obj.unit_price,
				description = obj.description,
				created_at = obj.created_at,
				action = 'UPD',
				user = request.user
			)
			SaleItemHistory.save()

		else:
			# Copy product to product's history table "ProductInStockHistory" => Action "SVE"
			# 1 if check this product has in the table then, this script is for update buttion, 
			# 2 otherwise is for save button
			super().save_model(request, obj, form, change)
			SaleItemHistory = SaleInvoiceItemHistory.objects.create(
				invoice = obj.invoice,
				product = obj.product,
				unit = obj.unit,
				unit_price = obj.unit_price,
				description = obj.description,
				created_at = obj.created_at,
				action = 'SVE',
				user = request.user,
			)
			SaleItemHistory.save()

	def delete_model(self, request, obj):
		if request.POST:
			super().delete_model(request, obj)
			SaleItemHistory = SaleInvoiceItemHistory.objects.create(
				invoice = obj.invoice,
				product = obj.product,
				unit = obj.unit,
				unit_price = obj.unit_price,
				description = obj.description,
				created_at = obj.created_at,
				action = 'DEL', 
				user = request.user
			)
			SaleItemHistory.save()
		
admin.site.register(SaleInvoiceItem, SaleInvoiceItemAdmin)



class SaleInvoiceItemHistoryAdmin(admin.ModelAdmin):
	list_display = ('invoice', 'product', 'unit', 'unit_price', 'created_at')
	search_fields = ('invoice', 'product')
	

admin.site.register(SaleInvoiceItemHistory, SaleInvoiceItemHistoryAdmin)

# Register your models here.
