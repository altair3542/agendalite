from __future__ import annotations

from django.db import models
from django.utils import timezone


class Service(models.Model):
    """
    Servicio que se puede agendar.
    """
    name = models.CharField(max_length=120, unique=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_be_booked(self) -> bool:
        return self.is_active

    def __str__(self) -> str:
        return f"{self.name} ({self.duration_minutes} min)"


class TimeSlotQuerySet(models.QuerySet):
    """
    QuerySet con intención de negocio: 'disponibles', 'futuros', etc.
    """

    def future(self):
        return self.filter(start_at__gte=timezone.now())

    def available(self):
        return self.future().filter(status=TimeSlot.Status.AVAILABLE)

    def for_service(self, service_id: int):
        return self.filter(service_id=service_id)


class TimeSlot(models.Model):
    """
    Cupo de agenda para un servicio en una fecha/hora específica.
    """
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Disponible"
        BLOCKED = "BLOCKED", "Bloqueado"
        BOOKED = "BOOKED", "Reservado"

    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="slots")
    start_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AVAILABLE)

    created_at = models.DateTimeField(auto_now_add=True)

    # Manager con QuerySet custom
    objects = TimeSlotQuerySet.as_manager()

    class Meta:
        ordering = ["start_at"]
        constraints = [
            # Evita duplicar el mismo slot para el mismo servicio
            models.UniqueConstraint(
                fields=["service", "start_at"],
                name="uniq_service_start_at",
            )
        ]

    def is_in_future(self) -> bool:
        return self.start_at >= timezone.now()

    def is_available(self) -> bool:
        return self.is_in_future() and self.status == self.Status.AVAILABLE

    def mark_booked(self) -> None:
        self.status = self.Status.BOOKED

    def mark_available(self) -> None:
        self.status = self.Status.AVAILABLE

    def __str__(self) -> str:
        return f"{self.service.name} @ {self.start_at:%Y-%m-%d %H:%M} ({self.get_status_display()})"


class BookingQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(slot__start_at__gte=timezone.now(), status=Booking.Status.CONFIRMED).select_related("service", "slot")

    def canceled(self):
        return self.filter(status=Booking.Status.CANCELED)


class Booking(models.Model):
    """
    Reserva confirmada de un cliente para un slot.
    """
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmada"
        CANCELED = "CANCELED", "Cancelada"

    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")
    slot = models.OneToOneField(TimeSlot, on_delete=models.PROTECT, related_name="booking")

    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BookingQuerySet.as_manager()

    def cancel(self) -> None:
        self.status = self.Status.CANCELED

    def __str__(self) -> str:
        return f"{self.customer_name} - {self.service.name} @ {self.slot.start_at:%Y-%m-%d %H:%M}"

