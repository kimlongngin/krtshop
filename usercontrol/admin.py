# users/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from usercontrol.models import UserControl

class UserControlAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'phone_number', 'email')
	search_fields = ('name', 'user__username', 'user__first_name', 'user__last_name', 'phone_number', 'email')

admin.site.register(UserControl, UserControlAdmin)



