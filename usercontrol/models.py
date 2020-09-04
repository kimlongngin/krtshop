from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def upload_location(instance, filename):
		filebase, extension = filename.split(".")
		return "%s/%s.%s" %(instance.id, instance.id, extension)

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')

def user_directory_path(request, filename):
	# return "files/users/%s/%s" % (request.user.id, filename)
    return str('/'.join(['content', request.name, filename]))


class UserControl(models.Model): 
	name = models.CharField(max_length=50) # Modify for image name
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	phone_number = models.CharField(max_length = 30)
	email = models.EmailField(max_length=250)
	avatar = models.FileField(blank=True, upload_to=user_directory_path,  validators=[validate_file_extension])
	age = models.IntegerField(default=0)
	present_address = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	is_status = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['-created_at']
		def __unicode__(self):
			return self.name

