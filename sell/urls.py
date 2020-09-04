from django.conf.urls import include, url
from . import views
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout


app_name = 'sell'
urlpatterns = [
    url(r'^$', views.SaleView.as_view(), name='sale_view'),
   	url(r'^filter_category/$', views.filter_category, name='filter_category'),
   	url(r'^filter_product/$', views.filter_product, name='filter_product'),
   	url(r'^filter_customer/$', views.filter_customer, name='filter_customer'),
   	url(r'^save_order_product_list/$', views.save_order_product_list, name='save_order_product_list'),
   	url(r'^check_invoice_product_list/$', views.check_invoice_product_list, name='check_invoice_product_list'),
   	url(r'^make_invoice_payment/$', views.make_invoice_payment, name='cancelSelling'),
   	url(r'^cancel_selling/$', views.cancel_selling, name='cancel_selling'),
    url(r'^update_order/$', views.update_order, name='update_order'),
    url(r'^delete_invoice/$', views.delete_invoice, name='delete_invoice'),
    url(r'^sub_make_invoice_payment/$', views.sub_make_invoice_payment, name='sub_make_invoice_payment'),
    url(r'^sub_make_payment/$', views.sub_make_payment, name='sub_make_payment'),
    url(r'^print_report/(?P<invoice_id>[0-9, a-z, A-Z]+)/$', views.print_report.as_view(), name='print_report'),
    url(r'^sell_history/$', views.SellHistoryView.as_view(), name='sell_history'),

   
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)