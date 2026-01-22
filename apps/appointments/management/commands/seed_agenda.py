from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.appointments.models import Service, TimeSlot


class Command(BaseCommand):
    help = "Crea datos de ejemplo para AgendaLite (servicios y slots)."

    def handle(self, *args, **options):
        services = [
            ("Consulta general", 30),
            ("Corte de cabello", 45),
            ("Asesoría", 60),
        ]

        created_services = []
        for name, minutes in services:
            s, _ = Service.objects.get_or_create(name=name, defaults={"duration_minutes": minutes, "is_active": True})
            created_services.append(s)

        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        total_slots = 0

        for s in created_services:
            # Creamos 12 slots futuros, cada 1 hora
            for i in range(1, 13):
                start_at = now + timedelta(hours=i)
                _, created = TimeSlot.objects.get_or_create(
                    service=s,
                    start_at=start_at,
                    defaults={"status": TimeSlot.Status.AVAILABLE},
                )
                if created:
                    total_slots += 1

        self.stdout.write(self.style.SUCCESS(f"Servicios: {len(created_services)} | Slots nuevos: {total_slots}"))
