from django.contrib import admin
from django.contrib.auth.models import User
from .models import Media, Product,ProductType, ProductHistory, ProductUnit, ProductCategory, ProductInStock, SubProductImage, Promotion, ProductInStockHistory, StockLocation
from django.contrib.auth.models import Group 
from django.contrib.admin.models import LogEntry, ADDITION
import os
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from .decorators import action_form


from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _, gettext_lazy


class ProductCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'created_at', 'is_status')
	search_fields = ['name']
	list_per_page = 10 

admin.site.register(ProductCategory, ProductCategoryAdmin)
	

class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'product_number', 'serial_number', 'created_at', 'is_status')
	search_fields = ('name', 'product_number', 'serial_number')
	list_per_page = 10 
admin.site.register(Product, ProductAdmin)


# class ProductUnitAdmin(admin.ModelAdmin):
# 	list_display = ('title', 'product', 'created_at', 'is_status')
# 	search_fields = ('product__name', 'title')
# 	list_per_page = 10 
# admin.site.register(ProductUnit, ProductUnitAdmin)


class ProductHistoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'product_number', 'serial_number', 'created_at')
	search_fields = ('name', 'product_number', 'serial_number')
	list_per_page = 10 
admin.site.register(ProductHistory, admin.ModelAdmin)
	


# Delete selected product in stock historys

class ProductInStockAdmin(admin.ModelAdmin):
	# list_display = ('title', 'product','unit', 'amount_per_unit', 'created_at', 'is_status')
	list_display = ('product','unit', 'amount', 'created_at', 'is_status')
	# search_fields = ('product__name', 'title')
	search_fields = ('product__name', 'title')
	# list_display_links = None
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
	                History = ProductInStockHistory.objects.create(
						product = obj.product,
						title = obj.title,
						unit = obj.unit,
						amount =  obj.amount,
						description = obj.description,
						action = 'DEL')
	                History.save()

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




	def data_of_orders(self, obj):
		return obj.order__count

	def delete_model(self, request, obj):
		if request.POST:
			obj.user = request.user
			super().delete_model(request, obj)
			History = ProductInStockHistory.objects.create(
			product = obj.product,
			title = obj.title,
			unit = obj.unit,
			amount =  obj.amount,
			description = obj.description,
			action = 'DEL'
		)
		History.save()

	def save_model(self, request, obj, form, change):
		obj.user = request.user
		objID = obj.id
		DataofProduct = ProductInStock.objects.filter(id=objID, is_status="True").count()
		
		if DataofProduct:
			super().save_model(request, obj, form, change)

			# Copy product to product's history table "ProductInStockHistory" => Action "UPD"
			# 1 if check this product has in the table then, this script is for update buttion, 
			# 2 otherwise is for save button
			History = ProductInStockHistory.objects.create(
				product = obj.product,
				title = obj.title,
				unit = obj.unit,
				amount =  obj.amount,
				description = obj.description,
				action = 'UPD'
			)
			History.save()

		else:
			# Copy product to product's history table "ProductInStockHistory" => Action "SVE"
			# 1 if check this product has in the table then, this script is for update buttion, 
			# 2 otherwise is for save button
			super().save_model(request, obj, form, change)
			History = ProductInStockHistory.objects.create(
				product = obj.product,
				title = obj.title,
				unit = obj.unit,
				amount =  obj.amount,
				description = obj.description,
				action = 'SVE'
			)
			History.save()

admin.site.register(ProductInStock, ProductInStockAdmin)



class SubProductImageAdmin(admin.ModelAdmin):
	list_display = ('name', 'product', 'created_at', 'is_status')
	search_fields = ('product__name', 'name')
admin.site.register(SubProductImage, SubProductImageAdmin)


class PromotionAdmin(admin.ModelAdmin):
	list_display = ('title', 'product', 'created_at', 'is_status')
	search_fields = ('product__name', 'title')
	list_per_page = 10 

admin.site.register(Promotion, PromotionAdmin)



class ProductInStockHistoryAdmin(admin.ModelAdmin):

	list_display = ('product_id', 'product', 'title', 'unit', 'amount', 'created_at', 'is_status')
	search_fields = ('product__name', 'title')
	list_per_page = 10 

	def delete_model(self, request, obj):
		if request.POST:
			obj.user = request.user
			super().delete_model(request, obj)
		
admin.site.register(ProductInStockHistory, ProductInStockHistoryAdmin)



class StockLocationAdmin(admin.ModelAdmin):
	list_display = ('name', 'location', 'address', 'controller', 'email', 'phone_number', 'created_at', 'is_status')
	search_fields = ('name', 'location', 'address', 'controller', 'email', 'phone_number')
		
admin.site.register(StockLocation, StockLocationAdmin)


class ProductTypeAdmin(admin.ModelAdmin):
	list_display = ('title', 'created_at', 'is_status')
	search_fields = ['title']
		
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Media)
		
# admin.site.unregister(Group)






