from django.db import models
from datetime import date
from django.conf import settings
import os
from django.core.exceptions import ValidationError

class Position(models.Model):
	name = models.CharField(max_length=200)
	description= models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	is_status = models.BooleanField(default=True)



	class Meta:
		ordering = ["-created_at", "-updated_at"]

