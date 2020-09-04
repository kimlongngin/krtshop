from django.conf.urls import url
from django.urls import path, include
from . import views
from django.conf import settings 
from django.conf.urls.static import static 

from django.contrib.auth import views as auth_views


app_name = 'usercontrol'

urlpatterns = [
    url(r'^login/$', views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$', views.auth_logout, name='auth_logout' ),
	url(r'^register/$', views.UserFormView.as_view(), name='register'),
	url(r'^usercontrol/', views.IndexView.as_view(), name='index'),
	url(r'^userlist/', views.ListUserView.as_view(), name='listuser'),

	url(r'^list_user_invoice/(?P<pk>[0-9, a-z, A-Z]+)/$', views.ListUserInvoice.as_view(), name='list_user_invoice'),

	url(r'^search_list_user_invoice/$', views.SearchListUserInvoice.as_view(), name='search_list_user_invoice'),
	url(r'^export_list_invoice/(?P<pk>[0-9, a-z, A-Z]+)/$', views.ExportListInvoiceView.as_view(), name='export_list_invoice'),

	url(r'^export_search_list_invoice/(?P<pk>[0-9, a-z, A-Z]+)/(?P<start_date>[0-9, a-z, A-Z]+)/(?P<end_date>[0-9, a-z, A-Z]+)/$', views.ExportSearchListInvoiceView.as_view(), name='export_search_list_invoice'),


	url(r'^all_user_invoice/$', views.AllUserInvoiceView.as_view(), name='all_user_invoice'),
	url(r'^search_all_user_invoice/$', views.SearchAllUserInvoiceView.as_view(), name='search_all_user_invoice'),
	url(r'^export_all_user_invoice/$', views.ExportAllUserInvoiceView.as_view(), name='export_all_user_invoice'),
	url(r'^export_all_search_user_invoice/(?P<key_term>[0-9, a-z, A-Z]+)/(?P<start_date>[0-9, a-z, A-Z]+)/(?P<end_date>[0-9, a-z, A-Z]+)/$', views.ExportAllSearchUserInvoiceView.as_view(), name='export_all_search_user_invoice'),


	# url(r'^login/$', auth_views.login, name='login'),	
	# url(r'^logout/$', views.auth_logout, name='auth_logout' ),
]
