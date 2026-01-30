from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.appointments.models import Booking, Service, TimeSlot


class SlotNotAvailableError(Exception):
    pass


class ServiceNotBookableError(Exception):
    pass


class BoookingNotCancelableError(Exception):
    pass

@dataclass(frozen=True)
class CreateBookingResult:
    booking: Booking
    slot: TimeSlot


class BookingService:
    """
    Servicio de dominio: encapsula la lógica para crear reservas.
    Mantiene reglas fuera de vistas/admin y facilita pruebas.
    """

    @staticmethod
    @transaction.atomic
    def create_booking(*, service_id: int, slot_id: int, customer_name: str, customer_email: str) -> CreateBookingResult:
        service = Service.objects.get(id=service_id)

        if not service.can_be_booked():
            raise ServiceNotBookableError("El servicio no está disponible para reservas.")

        # Nota: En PostgreSQL, aquí usaríamos select_for_update() para evitar doble reserva real.
        # En SQLite, el patrón se mantiene para el curso, aunque el locking es más limitado.
        slot = TimeSlot.objects.select_related("service").get(id=slot_id)

        if slot.service_id != service.id:
            raise SlotNotAvailableError("El slot no pertenece al servicio indicado.")

        if slot.start_at < timezone.now():
            raise SlotNotAvailableError("No se puede reservar un slot en el pasado.")

        if slot.status != TimeSlot.Status.AVAILABLE:
            raise SlotNotAvailableError("Este slot ya no está disponible.")

        slot.mark_booked()
        slot.save(update_fields=["status"])

        booking = Booking.objects.create(
            service=service,
            slot=slot,
            customer_name=customer_name,
            customer_email=customer_email,
            status=Booking.Status.CONFIRMED,
        )

        return CreateBookingResult(booking=booking, slot=slot)

    @staticmethod
    @transaction.atomic
    def cancel_booking(*, booking_id: int) -> Booking:
        """
        Cancelación MVP:
        - Booking pasa a CANCELED
        - Slot se mantiene BOOKED (por modelado OneToOne actual)
        """
        booking = Booking.objects.select_related("slot", "service").get(id=booking_id)

        if booking.status == Booking.Status.CANCELED:
            raise BoookingNotCancelableError("La reserva ya esta cancelada")

        # regla simple si quisieramos podriamos prohibir la cancelacion si ya paso la hora.

        if booking.slot.start_at < timezone.now():
            raise BoookingNotCancelableError("No se puede cancelar una reserva que ya paso")

        booking.cancel()
        booking.save(update_fields=["status"])

        return booking


    @staticmethod
    @transaction.atomic
    def cancel_booking_for_customer(*, booking_id: int, customer_email: str) -> Booking:
        """
        Cancelación desde UI (sin login):
        - Solo permitimos cancelar si el correo coincide con el de la reserva.
        - Luego delegamos a cancel_booking() para aplicar reglas de negocio.
        """
        booking = Booking.objects.only("id", "customer_email").get(id=booking_id)

        if booking.customer_email.strip().lower() != customer_email.strip().lower():
            raise BookingNotCancelableError("No puedes cancelar esta reserva con ese correo.")

        return BookingService.cancel_booking(booking_id=booking_id)
