"""Vistas del portal de estudiantes del Tópico UNH.

Incluye el registro en dos pasos (validación del código de matrícula y
completado de datos), el panel del estudiante, la reserva de citas y la
agenda del personal de salud.
"""

from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.decorators import ROLES_AGENDA_CITAS, rol_requerido
from accounts.models import CustomUser
from atenciones.models import Atencion
from pacientes.models import Paciente

from .models import Cita, Estudiante

SESION_ESTUDIANTE = 'portal_estudiante_id'


def _error_para_mensaje(exc):
    """Convierte un ValidationError en un mensaje legible."""
    if hasattr(exc, 'message_dict'):
        return '; '.join(
            f'{campo}: {" ".join(errs)}' for campo, errs in exc.message_dict.items()
        )
    return '; '.join(str(e) for e in exc.messages)


def _notificar_cita(estudiante, asunto, cuerpo):
    """Envía una notificación por correo al correo institucional del estudiante."""
    if not estudiante.correo_institucional:
        return
    try:
        send_mail(
            asunto,
            cuerpo,
            'topico@unh.edu.pe',
            [estudiante.correo_institucional],
            fail_silently=True,
        )
    except Exception:
        pass


def _perfil(usuario):
    return getattr(usuario, 'profile', None)


def _estudiante_de_usuario(usuario):
    return getattr(usuario, 'estudiante', None)


def _es_estudiante(usuario):
    return (
        usuario.is_authenticated
        and usuario.es_estudiante
        and _estudiante_de_usuario(usuario) is not None
    )


def inicio_portal(request):
    """Punto de entrada del portal: panel del estudiante o agenda del personal."""
    if not request.user.is_authenticated:
        return redirect('portal:validar_codigo')
    if _es_estudiante(request.user):
        estudiante = _estudiante_de_usuario(request.user)
        return render(
            request,
            'portal/inicio.html',
            {
                'estudiante': estudiante,
                'proximas_citas': estudiante.citas.filter(
                    estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
                ).order_by('fecha', 'hora'),
                'historial_citas': estudiante.citas.count(),
            },
        )
    return redirect('portal:lista_citas')


# ---------------------------------------------------------------------------
# Registro del estudiante (dos pasos)
# ---------------------------------------------------------------------------
def validar_codigo(request):
    """Paso 1 del registro: verificar código de matrícula y DNI en el padrón."""
    if request.user.is_authenticated:
        return redirect('portal:inicio')
    errores = None
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        dni = request.POST.get('dni', '').strip()
        try:
            estudiante = Estudiante.objects.get(codigo=codigo)
        except Estudiante.DoesNotExist:
            estudiante = None
            errores = (
                'El código ingresado no figura en el padrón de estudiantes. '
                'Verifique el código o acérquese al Tópico.'
            )
        if estudiante and estudiante.dni != dni:
            errores = 'El DNI no coincide con el código de estudiante.'
        elif estudiante and not estudiante.matriculado:
            errores = (
                'El estudiante no cuenta con matrícula activa en el presente semestre. '
                'Solo los estudiantes matriculados pueden registrarse.'
            )
        elif estudiante and estudiante.tiene_cuenta:
            errores = 'Este código ya tiene una cuenta registrada. Inicie sesión con su código.'
        if not errores and estudiante:
            request.session[SESION_ESTUDIANTE] = estudiante.pk
            return redirect('portal:completar_registro')
    return render(request, 'portal/validar_codigo.html', {
        'errores': errores,
        'datos': request.POST if request.method == 'POST' else None,
    })


def completar_registro(request):
    """Paso 2 del registro: datos complementarios y contraseña."""
    if request.user.is_authenticated:
        return redirect('portal:inicio')
    estudiante_id = request.session.get(SESION_ESTUDIANTE)
    if not estudiante_id:
        return redirect('portal:validar_codigo')
    estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
    if estudiante.tiene_cuenta or not estudiante.matriculado:
        request.session.pop(SESION_ESTUDIANTE, None)
        messages.error(request, 'El código ya no es válido para completar el registro.')
        return redirect('portal:validar_codigo')

    errores = None
    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '')
        sexo = request.POST.get('sexo', '')
        telefono = request.POST.get('telefono', '').strip()
        if not password1 or not password2:
            errores = 'Debe definir una contraseña y confirmarla.'
        elif password1 != password2:
            errores = 'Las contraseñas no coinciden.'
        else:
            try:
                validate_password(password1, user=None)
                user = CustomUser.objects.create_user(
                    username=estudiante.codigo,
                    first_name=estudiante.nombres,
                    last_name=estudiante.apellidos,
                    email=estudiante.correo_institucional,
                    password=password1,
                )
                user.role = CustomUser.Role.ESTUDIANTE
                user.telefono = telefono
                user.save()
                paciente, _ = Paciente.objects.get_or_create(
                    dni=estudiante.dni,
                    defaults={
                        'nombres': estudiante.nombres,
                        'apellidos': estudiante.apellidos,
                        'fecha_nacimiento': datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date(),
                        'sexo': sexo,
                        'telefono': telefono,
                        'registrado_por': user,
                    },
                )
                estudiante.user = user
                estudiante.paciente = paciente
                estudiante.save(update_fields=['user', 'paciente'])
                login(request, user)
                request.session.pop(SESION_ESTUDIANTE, None)
                messages.success(
                    request,
                    f'Bienvenido/a, {estudiante.nombres}. Su cuenta se creó correctamente.',
                )
                return redirect('portal:inicio')
            except ValidationError as exc:
                errores = _error_para_mensaje(exc)
            except ValueError as exc:
                errores = str(exc)
    return render(
        request,
        'portal/completar_registro.html',
        {
            'estudiante': estudiante,
            'errores': errores,
            'sexos': Paciente.Sexo.choices,
            'datos': request.POST if request.method == 'POST' else None,
        },
    )


# ---------------------------------------------------------------------------
# Panel del estudiante
# ---------------------------------------------------------------------------
@login_required
def mis_citas(request):
    """Citas del estudiante autenticado."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    citas = estudiante.citas.select_related('atencion').order_by('-fecha', '-hora')
    return render(request, 'portal/mis_citas.html', {'citas': citas})


@login_required
@require_http_methods(['GET', 'POST'])
def reservar_cita(request):
    """Reserva de una cita de atención en el Tópico."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    fecha = request.GET.get('fecha') or request.POST.get('fecha') or ''
    slots = Cita.slots_disponibles(fecha) if fecha else Cita.slots_del_dia()
    errores = None
    if request.method == 'POST':
        try:
            fecha_reserva = datetime.strptime(fecha, '%Y-%m-%d').date()
            hora = datetime.strptime(request.POST.get('hora', ''), '%H:%M').time()
            motivo = request.POST.get('motivo', '').strip()
            cita = Cita(estudiante=estudiante, fecha=fecha_reserva, hora=hora, motivo=motivo)
            cita.clean()
            if hora not in Cita.slots_disponibles(fecha_reserva):
                raise ValidationError({'hora': 'El horario seleccionado ya no está disponible.'})
            if estudiante.citas.filter(
                estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
            ).exists():
                raise ValidationError(
                    'Ya tiene una cita activa. Cancele la cita vigente para reservar otra.'
                )
            cita.save()
            messages.success(
                request,
                'Cita reservada para el '
                f'{cita.fecha:%d/%m/%Y} a las {cita.hora:%H:%M}. '
                'Preséntese al Tópico a la hora indicada.',
            )
            _notificar_cita(
                estudiante,
                'Cita reservada en el Tópico UNH',
                f'Hola {estudiante.nombres},\n\n'
                f'Su cita fue reservada para el {cita.fecha:%d/%m/%Y} '
                f'a las {cita.hora:%H:%M}.\nMotivo: {cita.motivo}\n\n'
                'Preséntese al Tópico de la universidad a la hora indicada.\n'
                'Atentamente, Tópico UNH.',
            )
            return redirect('portal:mis_citas')
        except (ValueError, ValidationError) as exc:
            errores = _error_para_mensaje(exc) if isinstance(exc, ValidationError) else str(exc)
    return render(request, 'portal/reservar_cita.html', {
        'slots': slots,
        'fecha': fecha,
        'hoy': timezone.localdate().isoformat(),
        'errores': errores,
        'datos': request.POST if request.method == 'POST' else None,
    })


@login_required
def mi_cola(request):
    """Posición del estudiante en la cola de atención del día."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    paciente = estudiante.paciente

    activas = Atencion.objects.filter(
        estado__in=[Atencion.Estado.EN_ESPERA, Atencion.Estado.EN_ATENCION],
        fecha_atencion__date=timezone.localdate(),
    ).select_related('paciente')

    orden_triage = {
        Atencion.NivelTriage.ROJO: 0,
        Atencion.NivelTriage.NARANJA: 1,
        Atencion.NivelTriage.AMARILLO: 2,
        Atencion.NivelTriage.VERDE: 3,
        Atencion.NivelTriage.AZUL: 4,
    }
    cola = sorted(
        activas,
        key=lambda a: (orden_triage[a.nivel_triage], a.fecha_atencion),
    )

    mi_atencion = None
    mi_posicion = None
    en_espera = sum(1 for a in cola if a.estado == Atencion.Estado.EN_ESPERA)
    if paciente:
        for i, atencion in enumerate(cola, start=1):
            if atencion.paciente_id == paciente.pk:
                mi_atencion = atencion
                mi_posicion = i
                break

    return render(request, 'portal/mi_cola.html', {
        'estudiante': estudiante,
        'cola': cola,
        'en_espera': en_espera,
        'mi_atencion': mi_atencion,
        'mi_posicion': mi_posicion,
    })


@login_required
def mi_historia_clinica(request):
    """Historia clínica del estudiante: atenciones previas con diagnóstico y receta."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    paciente = estudiante.paciente
    if paciente is None:
        return render(request, 'portal/historia_clinica.html', {'estudiante': estudiante, 'atenciones': []})
    atenciones = (
        paciente.atenciones
        .select_related('medico')
        .prefetch_related('receta__medicamento')
        .order_by('-fecha_atencion')
    )
    return render(request, 'portal/historia_clinica.html', {
        'estudiante': estudiante,
        'atenciones': atenciones,
    })


@login_required
@require_http_methods(['POST'])
def cancelar_cita(request, pk):
    """Cancelación de una cita propia (solo pendiente o confirmada)."""
    estudiante = _estudiante_de_usuario(request.user)
    if estudiante is None:
        return redirect('portal:inicio')
    cita = get_object_or_404(Cita, pk=pk, estudiante=estudiante)
    if cita.activa:
        cita.estado = Cita.Estado.CANCELADA
        cita.save(update_fields=['estado'])
        messages.success(request, 'Su cita fue cancelada correctamente.')
        _notificar_cita(
            estudiante,
            'Cita cancelada en el Tópico UNH',
            f'Hola {estudiante.nombres},\n\n'
            f'Su cita del {cita.fecha:%d/%m/%Y} a las {cita.hora:%H:%M} '
            'fue cancelada.\nSi lo desea, puede reservar un nuevo horario '
            'desde el portal.\n\nAtentamente, Tópico UNH.',
        )
    else:
        messages.warning(request, 'La cita seleccionada ya no puede cancelarse.')
    return redirect('portal:mis_citas')


# ---------------------------------------------------------------------------
# Agenda del personal de salud
# ---------------------------------------------------------------------------
@login_required
@rol_requerido(*ROLES_AGENDA_CITAS)
def lista_citas(request):
    """Agenda de citas del Tópico con filtros (personal de salud)."""
    citas = Cita.objects.select_related(
        'estudiante__paciente',
        'atencion',
    ).all()
    estado = request.GET.get('estado', '')
    fecha = request.GET.get('fecha', '')
    q = request.GET.get('q', '').strip()

    if estado:
        citas = citas.filter(estado=estado)
    if fecha:
        citas = citas.filter(fecha=fecha)
    if q:
        citas = citas.filter(
            estudiante__codigo__icontains=q,
        ) | citas.filter(
            estudiante__nombres__icontains=q,
        ) | citas.filter(
            estudiante__apellidos__icontains=q,
        )

    return render(
        request,
        'portal/citas.html',
        {
            'citas': citas.distinct(),
            'estado': estado,
            'fecha': fecha,
            'q': q,
            'estado_opciones': Cita.Estado.choices,
            'pendientes': Cita.objects.filter(estado=Cita.Estado.PENDIENTE).count(),
            'confirmadas': Cita.objects.filter(estado=Cita.Estado.CONFIRMADA).count(),
        },
    )


@login_required
@rol_requerido(*ROLES_AGENDA_CITAS)
@require_http_methods(['GET', 'POST'])
def convertir_cita(request, pk):
    """Convierte una cita vigente en una atención médica (personal de salud)."""
    cita = get_object_or_404(
        Cita.objects.select_related('estudiante__paciente'),
        pk=pk,
    )
    if not cita.activa:
        messages.warning(request, 'La cita seleccionada no se encuentra vigente.')
        return redirect('portal:lista_citas')

    if request.method == 'POST':
        paciente = cita.estudiante.paciente
        if paciente is None:
            messages.error(request, 'El estudiante no tiene una ficha de paciente vinculada.')
            return redirect('portal:lista_citas')
        atencion = Atencion.objects.create(
            paciente=paciente,
            medico=request.user,
            motivo_consulta=cita.motivo,
        )
        cita.atencion = atencion
        cita.estado = Cita.Estado.ATENDIDA
        cita.save(update_fields=['atencion', 'estado'])
        messages.success(
            request,
            f'Cita de {cita.estudiante.nombre_completo} convertida en la atención #{atencion.pk}.',
        )
        _notificar_cita(
            cita.estudiante,
            'Su cita fue atendida en el Tópico UNH',
            f'Hola {cita.estudiante.nombres},\n\n'
            f'Le informamos que su cita del {cita.fecha:%d/%m/%Y} fue atendida '
            f'en el Tópico de la universidad (atención #{atencion.pk}).\n\n'
            'Atentamente, Tópico UNH.',
        )
        return redirect('atenciones:detalle', pk=atencion.pk)
    return render(request, 'portal/convertir_cita.html', {'cita': cita})
