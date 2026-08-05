from django.core.management.base import BaseCommand
from django.utils import timezone

from portal.models import Cita


class Command(BaseCommand):
    """Envía recordatorios de cita al correo institucional 24 horas antes.

    Programar con un cron/task scheduler diario, por ejemplo a las 08:00.
    """

    help = 'Envía recordatorios de cita a los estudiantes citados para mañana.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--horas',
            type=int,
            default=24,
            help='Anticipación en horas para recordar la cita (por defecto 24).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra las citas que se recordarían sin enviar correos.',
        )

    def handle(self, *args, **opciones):
        horas = opciones['horas']
        dry_run = opciones['dry_run']
        inicio = timezone.now()
        fin = inicio + timezone.timedelta(hours=horas)

        citas = (
            Cita.objects.filter(
                estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
                fecha=fin.date(),
            )
            .select_related('estudiante')
        )

        recordadas = 0
        for cita in citas:
            estudiante = cita.estudiante
            if not estudiante.correo_institucional:
                continue
            recordadas += 1
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'[simulación] {estudiante.correo_institucional} — '
                        f'cita {cita.fecha} {cita.hora:%H:%M}'
                    )
                )
                continue
            self._notificar(cita)

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'{recordadas} correo(s) se enviarían.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'{recordadas} recordatorio(s) enviado(s).'))

    def _notificar(self, cita):
        from django.core.mail import send_mail

        estudiante = cita.estudiante
        try:
            send_mail(
                'Recordatorio: su cita en el Tópico UNH es mañana',
                f'Hola {estudiante.nombres},\n\n'
                f'Le recordamos que tiene una cita mañana {cita.fecha:%d/%m/%Y} '
                f'a las {cita.hora:%H:%M} en el Tópico de la universidad.\n'
                f'Motivo: {cita.motivo}\n\n'
                'Preséntese 10 minutos antes de la hora indicada.\n'
                'Si no puede asistir, cancele su cita desde el portal.\n\n'
                'Atentamente, Tópico UNH.',
                'topico@unh.edu.pe',
                [estudiante.correo_institucional],
                fail_silently=True,
            )
        except Exception:
            pass
