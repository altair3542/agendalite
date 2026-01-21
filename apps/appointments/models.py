from django.db import models
from __future__ import annotations
from django.utils import timezone
# Create your models here.

class Service(models.Model):
    # """servicio que se puede agendar"""
    name = models.CharField(max_length=120, unique=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_be_booked(self) -> bool:
        return self.is_active

    def __str__(self) -> str:
        return f"{self.name} ({self.duration_minutes} min)"

    
