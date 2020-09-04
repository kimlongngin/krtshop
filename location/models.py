from django.db import models
from datetime import date
from django.conf import settings
import os
from django.core.exceptions import ValidationError

class Location(models.Model):
	name = models.CharField(max_length=200)
	description= models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	is_status = models.BooleanField(default=True)

	def __str__ (self):
		return self.name
	class Meta:
		ordering = ["-created_at", "-updated_at"]
