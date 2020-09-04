from django.conf.urls import include, url
from django.urls import path
from . import views
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout

app_name = 'customer'

urlpatterns = [
    path('', views.IndexView.as_view(), name='customer_index'),
    url(r'^detail/(?P<full_name>[0-9, a-z, A-Z]+)/$', views.CustomerDetailView.as_view(), name='customer_detail'),
    url(r'^export_customer_invoice/(?P<full_name>[0-9, a-z, A-Z]+)/$', views.ExportCustomerInvoiceView.as_view(), name='export_customer_invoice'),
    url(r'^search_customer_invoice/$', views.SearchCustomerInvoice.as_view(), name='search_customer_invoice'),
    url(r'^export_search_customer_invoice/(?P<full_name>[0-9, a-z, A-Z]+)/(?P<start_date>[0-9, a-z, A-Z]+)/(?P<end_date>[0-9, a-z, A-Z]+)/$', views.ExportSearchCustomerInvoice.as_view(), name='export_search_customer_invoice'),

    url(r'^list_invoice_detail/(?P<invoice_no>[0-9, a-z, A-Z]+)/$', views.ListInvoiceDetailView.as_view(), name='list_invoice_detail'),
    url(r'^list_client/$', views.ListClient.as_view(), name='list_client'),
    url(r'^owe_list/$', views.OweClient.as_view(), name='owe_list'),
    url(r'^compansate_remaining/(?P<invoice_no>[0-9, a-z, A-Z]+)/$', views.CompansateRemaining.as_view(), name='compansate_remaining'),
    url(r'^make_payment/$', views.MakePayment.as_view(), name='make_payment'),
    url(r'^owe_list_search/$', views.OweListSearch.as_view(), name='owe_list_search'),
    url(r'^save_list/$', views.SaveList.as_view(), name='save_list'),
    url(r'^delete_save/(?P<pk>[0-9]+)/$', views.DeleteSave.as_view(), name='delete_save'),
    url(r'^search_save_list/$', views.SearchSaveList.as_view(), name='search_save_list'),
    url(r'^save_payment/(?P<invoice_no>[0-9, a-z, A-Z]+)/$', views.PaymentSaveView.as_view(), name='save_payment'),
    url(r'^make_save_payment/$', views.MakeSavePayment.as_view(), name='make_save_payment'),

]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)