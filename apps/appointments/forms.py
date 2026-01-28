from __future__ import annotations

from django import forms
from django.utils import timezone

from apps.appointments.models import TimeSlot

class BookingRequestForm(forms.Form):
    """
    Formulario de solicitud de reserva.
    Nota: NO crea Booking directamente. Eso lo hace BookingService.
    """

    customer_name = forms.CharField(
        max_length=120,
        label="Nombre",
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Tu nombre"}),
    )
    customer_email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={"class": "input", "placeholder": "tu@correo.com"}),
    )

    def __init__(self, *args, slot: TimeSlot, **kwargs):
        super().__init__(*args, **kwargs)
        self.slot = slot

    def clean(self):
        cleaned = super().clean()

        if self.slot.start_at < timezone.now():
            raise forms.ValidationError("Este slot ya paso, elige uno diferente.")

        if self.slot.status != TimeSlot.Status.AVAILABLE:
            raise forms.ValidationError("este slot ya no esta disponible.")

        if not self.slot.service.can_be_booked():
            raise forms.ValidationError("ESte servicio no esta disponible")

        return cleaned
