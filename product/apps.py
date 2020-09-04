from django.apps import AppConfig
from product.models import Product, Media

class ProductConfig(AppConfig):
    name = 'product'


def base_media(request):
    return {'all_media': Media.objects.all().order_by('created_at')} # of course some filter here
