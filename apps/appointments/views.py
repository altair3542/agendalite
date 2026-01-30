from __future__ import annotations
from typing import Any

from django.db.models.query import QuerySet
from django.views import View
from django.utils import timezone

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from apps.appointments.forms import BookingRequestForm, MyBookingsFilterForm
from apps.appointments.models import Service, TimeSlot, Booking
from apps.appointments.services.booking_service import (
    BookingService,
    SlotNotAvailableError,
    ServiceNotBookableError,
)


class HomeRedirectView(TemplateView):
    """
    Home simple: redirige al listado de servicios.
    """
    template_name = "appointments/base.html"

    def get(self, request, *args, **kwargs):
        return redirect("appointments:service_list")


class ServiceListView(ListView):
    """
    Lista de servicios activos.
    """
    model = Service
    template_name = "appointments/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        # Consultas expresivas: lo que el usuario puede agendar
        return Service.objects.filter(is_active=True).order_by("name")


class ServiceDetailView(DetailView):
    """
    Detalle del servicio + slots disponibles.
    """
    model = Service
    template_name = "appointments/service_detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        service = self.object

        # Mostramos próximos 20 slots disponibles
        ctx["available_slots"] = (
            TimeSlot.objects.for_service(service.id).available().select_related("service")[:20]
        )
        return ctx


class BookingCreateView(FormView):
    """
    Reserva de un slot específico.
    La creación real se delega a BookingService.
    """
    template_name = "appointments/booking_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.slot = self._get_slot()
        return super().dispatch(request, *args, **kwargs)

    def _get_slot(self) -> TimeSlot:
        slot_id = self.kwargs.get("slot_id")
        try:
            return TimeSlot.objects.select_related("service").get(id=slot_id)
        except TimeSlot.DoesNotExist:
            raise Http404("Slot no encontrado")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Inyectamos slot al Form para validaciones coherentes
        kwargs["slot"] = self.slot
        return kwargs

    def get_form_class(self):
        return BookingRequestForm

    def form_valid(self, form):
        # Regla importante: el servicio es la fuente de verdad para reservar
        try:
            result = BookingService.create_booking(
                service_id=self.slot.service_id,
                slot_id=self.slot.id,
                customer_name=form.cleaned_data["customer_name"],
                customer_email=form.cleaned_data["customer_email"],
            )
        except (SlotNotAvailableError, ServiceNotBookableError) as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

        messages.success(self.request, "Reserva creada correctamente.")
        return redirect("appointments:booking_success", booking_id=result.booking.id)


class BookingSuccessView(TemplateView):
    template_name = "appointments/booking_success.html"

    def get_context_data(self, **kwargs):
        return {"booking_id": kwargs["booking_id"]}


class MyBookingsView(ListView):
    """
    /my-bookings/?email=...&status=...&date_from=...&date_to=...
    - Filtros validados por form
    - Paginación para UX real
    """
    model = Booking
    template_name = "appointments/my_bookings.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_form(self):
        return MyBookingsFilterForm(self.request.GET or None)

    def get_queryset(self):
        form = self.get_form()

        # si el form no es valido, no consultamos nada... (evita consultas raras...)
        if not form.is_valid():
            return Booking.objects.none()

        email = form.cleaned_data["email"].strip().lower()
        status = form.cleaned_data.get("status") or ""
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")

        qs = (
            Booking.objects
            .select_related("service", "slot")
            .filter(customer_email=email)
            .order_by("-slot__start_at")
        )

        if status:
            qs = qs.filter(status=status)

        if date_from:
            qs = qs.filter(slot__start_at__date__gte=date_from)

        if date_to:
            qs = qs.filter(slot__start_at__date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = self.get_form()
        ctx["form"] = form
        return ctx

class BookingCancelView(View):
    """
    POST /booking/<id>/cancel/
    Requiere 'email' (del usuario) para autorizar cancelación sin login.
    """
    def post(self, request, booking_id: int):
        email = (request.POST.get("email") or "").strip().lower()

        if not email:
            messages.error(request, "Debes ingresar tu correo para cancelar una reserva.")
            return redirect("appointments:my_bookings")

        try:
            BookingService.cancel_booking_for_customer(booking_id=booking_id, customer_email=email)
            messages.success(request, "Reserva cancelada correctamente.")
        except BookingNotCancelableError as e:
            messages.error(request, str(e))
        except Booking.DoesNotExist:
            messages.error(request, "Reserva no encontrada.")

        # Redirigimos de vuelta conservando el email para que el usuario vea su lista
        return redirect(f"{reverse('appointments:my_bookings')}?email={email}")

