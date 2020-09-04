from django.conf.urls import url
from django.urls import path, include	
from . import views

urlpatterns = [
    # path('', views.index, name='client-index'),
    url('', views.index, name='product-history-index'),
    

]