from django.contrib import admin

from .models import Service, TimeSlot, Booking
from .services.booking_service import BookingService, BoookingNotCancelableError

# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes", "is_active", "created_at")
    search_fields = ("name", )
    list_filter  = ("is_active",)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("service", "start_at", "status", "created_at")
    list_filter = ("service", "status")
    search_fields = ("service__name",)
    ordering = ("start_at",)

@admin.action(description="Cancelar reservas seleccionadas (cambia status a CANCELED)")
def cancel_bookings(modeladmin, request, queryset):
    ok = 0
    failed = 0

    for booking in queryset:
        try:
            BookingService.cancel_booking(booking_id=booking.id)
            ok += 1
        except BoookingNotCancelableError as e:
            failed += 1
            modeladmin.message_user(request, f"reserva {booking.id}: {e}, level=messages.WARNING")

    if ok:
        modeladmin.message_user(request, f"reservas canceladas {ok}, level=message.SUCCESS")

    if failed:
        modeladmin.message_user(request, f"reservas NO canceladas {failed}, level=message.WARNING")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_email", "service", "slot", "status", "created_at")
    list_filter = ("service", "status")
    search_fields = ("customer_name", "customer_email", "service__name")
    actions = [cancel_bookings]
