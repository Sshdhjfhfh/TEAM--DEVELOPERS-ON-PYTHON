"""Comando que carga datos de demostración (entorno de desarrollo).

Uso:
    python manage.py seed_demo
    python manage.py seed_demo --reset
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import CustomUser
from atenciones.models import Atencion, RecetaMedicamento, SignosVitales
from inventario.models import Medicamento, MovimientoInventario
from pacientes.models import Paciente
from portal.models import Cita, Estudiante


class Command(BaseCommand):
    help = 'Carga datos de demostración para el Tópico UNH (solo desarrollo).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina los datos existentes antes de cargar los de demostración.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self._reset()
        self.stdout.write('Cargando datos de demostración...')

        admin, _ = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'del Tópico',
                'email': 'admin@topico.unh.edu.pe',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        admin.set_password('admin123')
        admin.role = 'ADMIN'
        admin.save()

        medico, _ = CustomUser.objects.get_or_create(
            username='medico',
            defaults={
                'first_name': 'Juan',
                'last_name': 'Pérez Ramos',
                'email': 'medico@topico.unh.edu.pe',
            },
        )
        medico.set_password('medico123')
        medico.role = 'MEDICO'
        medico.colegiatura = 'CMP-12345'
        medico.save()

        enfermero, _ = CustomUser.objects.get_or_create(
            username='enfermera',
            defaults={
                'first_name': 'María',
                'last_name': 'López Díaz',
                'email': 'enfermera@topico.unh.edu.pe',
            },
        )
        enfermero.set_password('enfermera123')
        enfermero.role = 'ENFERMERO'
        enfermero.save()

        farmacia, _ = CustomUser.objects.get_or_create(
            username='farmacia',
            defaults={
                'first_name': 'Carlos',
                'last_name': 'Torres Medina',
                'email': 'farmacia@topico.unh.edu.pe',
            },
        )
        farmacia.set_password('farmacia123')
        farmacia.role = 'FARMACEUTICO'
        farmacia.save()

        # --- Pacientes de ejemplo ---
        pacientes_data = [
            ('Ana', 'Quispe Huamán', '12345678', date(2001, 3, 12), 'F', 'O+', 'Penicilina'),
            ('Luis', 'García Poma', '23456789', date(1998, 7, 25), 'M', 'A+', ''),
            ('Rosa', 'Castro Llacsa', '34567890', date(2005, 1, 30), 'F', 'O-', ''),
            ('Pedro', 'Rojas Apaza', '45678901', date(1975, 11, 2), 'M', 'B+', 'Polvo'),
            ('Carmen', 'Sulca Tello', '56789012', date(1988, 5, 17), 'F', 'AB+', ''),
        ]
        pacientes = []
        for nombre, apellido, dni, nac, sexo, sangre, alergias in pacientes_data:
            paciente, _ = Paciente.objects.get_or_create(
                dni=dni,
                defaults={
                    'nombres': nombre,
                    'apellidos': apellido,
                    'fecha_nacimiento': nac,
                    'sexo': sexo,
                    'tipo_sangre': sangre,
                    'alergias': alergias,
                    'telefono': '9' + dni[:7],
                    'direccion': 'Huancavelica, Perú',
                    'registrado_por': enfermero,
                },
            )
            pacientes.append(paciente)

        # --- Atenciones de ejemplo ---
        hoy = timezone.localdate()
        atenciones_data = [
            (pacientes[0], medico, 'Dolor abdominal intenso', 'ROJO', 'EN_ATENCION', 38.5, 120, 80, 95, 20, 96),
            (pacientes[1], medico, 'Corte en la mano', 'VERDE', 'ATENDIDO', 36.8, 110, 70, 80, 16, 98),
            (pacientes[2], enfermero, 'Fiebre y malestar general', 'AMARILLO', 'EN_ESPERA', 38.0, 115, 75, 88, 18, 97),
            (pacientes[3], medico, 'Dolor de cabeza y mareos', 'NARANJA', 'EN_ESPERA', 37.2, 140, 90, 76, 18, 98),
            (pacientes[4], None, 'Control de signos vitales', 'AZUL', 'ATENDIDO', 36.6, 100, 65, 72, 15, 99),
        ]
        for i, (paciente, medico, motivo, triage, estado, *signos) in enumerate(atenciones_data):
            atencion, creado = Atencion.objects.get_or_create(
                paciente=paciente,
                motivo_consulta=motivo,
                defaults={
                    'medico': medico,
                    'nivel_triage': triage,
                    'estado': estado,
                    'diagnostico': 'En evaluación por el personal del Tópico.',
                    'tratamiento': 'Indicaciones generales según protocolo.',
                    'fecha_atencion': timezone.now() - timedelta(hours=i * 3),
                },
            )
            if creado:
                SignosVitales.objects.create(
                    atencion=atencion,
                    temperatura=signos[0],
                    presion_sistolica=signos[1],
                    presion_diastolica=signos[2],
                    pulso=signos[3],
                    frecuencia_respiratoria=signos[4],
                    saturacion_oxigeno=signos[5],
                )

        # --- Inventario de ejemplo ---
        medicamentos_data = [
            ('Paracetamol 500mg', 'Analgésico y antipirético', 'MEDICAMENTO', 'tableta', 40, 20, 1.50, farmacia),
            ('Ibuprofeno 400mg', 'Antiinflamatorio no esteroideo', 'MEDICAMENTO', 'tableta', 5, 15, 2.00, farmacia),
            ('Suero fisiológico 0.9%', 'Solución para infusión IV', 'INSUMO', 'bolsa 1L', 12, 10, 8.00, farmacia),
            ('Jeringa descartable 5ml', 'Material médico descartable', 'INSUMO', 'unidad', 8, 30, 0.80, farmacia),
            ('Alcohol en gel', 'Desinfectante de manos', 'INSUMO', 'frasco', 3, 6, 6.50, farmacia),
        ]
        medicamentos = []
        for nombre, desc, cat, unidad, stock, minimo, precio, _ in medicamentos_data:
            medicamento, _ = Medicamento.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': desc,
                    'categoria': cat,
                    'unidad': unidad,
                    'stock_actual': stock,
                    'stock_minimo': minimo,
                    'precio_unitario': precio,
                    'proveedor': 'Farmacia UNH',
                },
            )
            medicamentos.append(medicamento)

        if not MovimientoInventario.objects.exists():
            MovimientoInventario.objects.create(
                medicamento=medicamentos[0],
                tipo=MovimientoInventario.Tipo.ENTRADA,
                cantidad=40,
                motivo='Compra inicial',
                usuario=farmacia,
            )

        # --- Receta de ejemplo (descuenta stock) ---
        primera_atencion = Atencion.objects.first()
        if primera_atencion and not RecetaMedicamento.objects.exists():
            RecetaMedicamento.objects.create(
                atencion=primera_atencion,
                medicamento=medicamentos[0],
                cantidad=10,
                indicaciones='1 tableta cada 8 horas por 3 días',
            )

        # --- Padrón de estudiantes (portal) ---
        padron_data = [
            # codigo, dni, nombres, apellidos, escuela, ciclo, matriculado
            ('2021141001', '12345678', 'Ana', 'Quispe Huamán', Estudiante.Escuela.SISTEMAS, 9, True),
            ('2021141002', '23456789', 'Luis', 'García Poma', Estudiante.Escuela.SISTEMAS, 9, True),
            ('2022141050', '34567890', 'Rosa', 'Castro Llacsa', Estudiante.Escuela.ENFERMERIA, 7, True),
            ('2021142003', '45678901', 'Pedro', 'Rojas Apaza', Estudiante.Escuela.CIVIL, 10, False),
            ('2023142021', '56789012', 'Carmen', 'Sulca Tello', Estudiante.Escuela.OBSTETRICIA, 5, True),
            ('2024141025', '12345671', 'Jorge', 'Condori Asto', Estudiante.Escuela.EDUCACION, 3, True),
        ]
        estudiantes = []
        for codigo, dni, nombres, apellidos, escuela, ciclo, matriculado in padron_data:
            estudiante, _ = Estudiante.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'dni': dni,
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'escuela': escuela,
                    'ciclo': ciclo,
                    'matriculado': matriculado,
                    'correo_institucional': f'{codigo}@unh.edu.pe',
                },
            )
            estudiantes.append(estudiante)

        # Estudiante con cuenta ya creada (para probar el portal con acceso directo).
        estudiante_con_cuenta, _ = CustomUser.objects.get_or_create(
            username='estudiante',
            defaults={
                'first_name': estudiantes[0].nombres,
                'last_name': estudiantes[0].apellidos,
                'email': estudiantes[0].correo_institucional,
            },
        )
        estudiante_con_cuenta.set_password('estudiante123')
        estudiante_con_cuenta.role = 'ESTUDIANTE'
        estudiante_con_cuenta.save()
        estudiantes[0].user = estudiante_con_cuenta
        estudiantes[0].paciente = pacientes[0]
        estudiantes[0].save(update_fields=['user', 'paciente'])
        # Vincula también las fichas existentes de los demás estudiantes del padrón.
        for i, dni in enumerate(['23456789', '34567890', '56789012']):
            try:
                estudiantes[i + 1].paciente = Paciente.objects.get(dni=dni)
                estudiantes[i + 1].save(update_fields=['paciente'])
            except Paciente.DoesNotExist:
                pass

        # --- Citas de ejemplo (portal) ---
        def _proximo_dia_habil():
            fecha = hoy + timedelta(days=1)
            while fecha.weekday() >= 5:
                fecha += timedelta(days=1)
            return fecha

        if not Cita.objects.exists():
            Cita.objects.create(
                estudiante=estudiantes[0],
                fecha=_proximo_dia_habil(),
                hora=Cita.slots_del_dia()[0],
                motivo='Control de presión arterial y dolor de cabeza recurrente.',
                estado=Cita.Estado.CONFIRMADA,
            )
            Cita.objects.create(
                estudiante=estudiantes[1],
                fecha=_proximo_dia_habil() + timedelta(days=1),
                hora=Cita.slots_del_dia()[4],
                motivo='Consulta por gripe y malestar general.',
                estado=Cita.Estado.PENDIENTE,
            )
            Cita.objects.create(
                estudiante=estudiantes[2],
                fecha=_proximo_dia_habil() - timedelta(days=1),
                hora=Cita.slots_del_dia()[2],
                motivo='Vacunación programada.',
                estado=Cita.Estado.ATENDIDA,
            )

        self.stdout.write(self.style.SUCCESS(
            'Datos de demostración cargados correctamente.\n'
            'Usuarios creados (contraseña en la misma línea):\n'
            '  admin      -> admin123\n'
            '  medico     -> medico123\n'
            '  enfermera  -> enfermera123\n'
            '  farmacia   -> farmacia123\n'
            '  estudiante -> estudiante123'
        ))

    def _reset(self):
        self.stdout.write('Eliminando datos existentes...')
        for modelo in (Cita, Estudiante, Atencion, SignosVitales, RecetaMedicamento, Medicamento, MovimientoInventario, Paciente):
            modelo.objects.all().delete()
        for user in CustomUser.objects.filter(username__in=['admin', 'medico', 'enfermera', 'farmacia', 'estudiante']):
            user.delete()
