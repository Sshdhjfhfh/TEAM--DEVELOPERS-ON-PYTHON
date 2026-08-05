import csv
import io
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from atenciones.models import Atencion
from inventario.models import Medicamento, MovimientoInventario
from pacientes.models import Paciente


def _periodo_inicio(request):
    """Devuelve el periodo seleccionado y su fecha de inicio."""
    periodo = request.GET.get('periodo', 'hoy')
    hoy = timezone.localdate()
    if periodo == 'semana':
        inicio = hoy - timezone.timedelta(days=6)
    elif periodo == 'mes':
        inicio = hoy - timezone.timedelta(days=29)
    else:
        periodo = 'hoy'
        inicio = hoy
    return periodo, inicio


def _csv_response(nombre_archivo, encabezados, filas):
    """Devuelve una respuesta CSV con BOM UTF-8 (compatible con Excel)."""
    buffer = io.StringIO()
    buffer.write('\ufeff')
    escritor = csv.writer(buffer)
    escritor.writerow(encabezados)
    for fila in filas:
        escritor.writerow(fila)
    respuesta = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.csv"'
    return respuesta


def _conteo_por_dia(queryset, campo_fecha):
    """Agrupa un queryset por día y devuelve una lista JSON para los gráficos."""
    por_dia = (
        queryset
        .annotate(dia=TruncDate(campo_fecha))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )
    return json.dumps([
        {'dia': item['dia'].isoformat(), 'total': item['total']}
        for item in por_dia if item['dia']
    ])


@login_required
def dashboard(request):
    """Panel principal con indicadores del Tópico en tiempo real."""
    periodo, inicio = _periodo_inicio(request)

    atenciones_periodo = Atencion.objects.filter(fecha_atencion__date__gte=inicio)
    pacientes_periodo = Paciente.objects.filter(fecha_registro__date__gte=inicio)

    triage = atenciones_periodo.values('nivel_triage').annotate(total=Count('id'))

    contexto = {
        'periodo': periodo,
        'total_pacientes': Paciente.objects.count(),
        'pacientes_nuevos': pacientes_periodo.count(),
        'atenciones_periodo': atenciones_periodo.count(),
        'atenciones_hoy': Atencion.objects.filter(fecha_atencion__date=timezone.localdate()).count(),
        'en_espera': Atencion.objects.filter(estado=Atencion.Estado.EN_ESPERA).count(),
        'en_atencion': Atencion.objects.filter(estado=Atencion.Estado.EN_ATENCION).count(),
        'triage_json': json.dumps({item['nivel_triage']: item['total'] for item in triage}),
        'atenciones_por_dia_json': _conteo_por_dia(atenciones_periodo, 'fecha_atencion'),
        'medicamentos_criticos': list(
            Medicamento.objects.filter(stock_actual__lte=F('stock_minimo'))[:8]
        ),
        'ultimas_atenciones': Atencion.objects.select_related('paciente').order_by('-fecha_atencion')[:5],
    }
    return render(request, 'reportes/dashboard.html', contexto)


@login_required
def reporte_pacientes(request):
    """Reporte de pacientes registrados por periodo."""
    periodo, inicio = _periodo_inicio(request)
    pacientes = Paciente.objects.filter(fecha_registro__date__gte=inicio)
    por_sexo = pacientes.values('sexo').annotate(total=Count('id'))
    return render(
        request,
        'reportes/pacientes.html',
        {
            'periodo': periodo,
            'total': pacientes.count(),
            'por_sexo': por_sexo,
            'por_dia_json': _conteo_por_dia(pacientes, 'fecha_registro'),
        },
    )


@login_required
def reporte_atenciones(request):
    """Reporte de atenciones por periodo, triage y estado."""
    periodo, inicio = _periodo_inicio(request)
    atenciones = Atencion.objects.filter(fecha_atencion__date__gte=inicio)
    por_triage = list(
        atenciones.values('nivel_triage').annotate(total=Count('id')).order_by('nivel_triage')
    )
    por_estado = list(
        atenciones.values('estado').annotate(total=Count('id')).order_by('estado')
    )
    por_medico = (
        atenciones.exclude(medico__isnull=True)
        .values('medico__first_name', 'medico__last_name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    return render(
        request,
        'reportes/atenciones.html',
        {
            'periodo': periodo,
            'total': atenciones.count(),
            'por_triage_json': json.dumps(por_triage),
            'por_estado_json': json.dumps(por_estado),
            'por_medico': por_medico,
        },
    )


@login_required
def reporte_inventario(request):
    """Reporte del estado del almacén: stock y movimientos."""
    criticos = Medicamento.objects.filter(stock_actual__lte=F('stock_minimo'))
    movimientos = MovimientoInventario.objects.values('tipo').annotate(
        total=Count('id'),
        cantidad_total=Sum('cantidad'),
    )
    valor_inventario = sum(
        m.stock_actual * float(m.precio_unitario) for m in Medicamento.objects.all()
    )
    return render(
        request,
        'reportes/inventario.html',
        {
            'total_items': Medicamento.objects.count(),
            'criticos': list(criticos),
            'movimientos': movimientos,
            'valor_inventario': round(valor_inventario, 2),
        },
    )


# ---------------------------------------------------------------------------
# Exportación y reportes imprimibles
# ---------------------------------------------------------------------------
@login_required
def exportar_pacientes_csv(request):
    """Exporta los pacientes del periodo a CSV."""
    _, inicio = _periodo_inicio(request)
    pacientes = Paciente.objects.filter(fecha_registro__date__gte=inicio).order_by('apellidos')
    filas = [[
        p.dni,
        p.nombres,
        p.apellidos,
        p.get_sexo_display(),
        p.edad,
        p.tipo_sangre or '',
        p.telefono,
        p.fecha_registro.strftime('%d/%m/%Y %H:%M'),
    ] for p in pacientes]
    return _csv_response(
        'reporte_pacientes',
        ['DNI', 'Nombres', 'Apellidos', 'Sexo', 'Edad', 'Tipo de sangre', 'Teléfono', 'Fecha de registro'],
        filas,
    )


@login_required
def exportar_atenciones_csv(request):
    """Exporta las atenciones del periodo a CSV."""
    _, inicio = _periodo_inicio(request)
    atenciones = Atencion.objects.select_related('paciente', 'medico').filter(
        fecha_atencion__date__gte=inicio,
    ).order_by('fecha_atencion')
    filas = [[
        a.fecha_atencion.strftime('%d/%m/%Y %H:%M'),
        a.paciente.nombre_completo,
        a.paciente.dni,
        a.medico_nombre,
        a.motivo_consulta,
        a.get_nivel_triage_display(),
        a.get_estado_display(),
    ] for a in atenciones]
    return _csv_response(
        'reporte_atenciones',
        ['Fecha', 'Paciente', 'DNI', 'Médico', 'Motivo', 'Triage', 'Estado'],
        filas,
    )


@login_required
def exportar_inventario_csv(request):
    """Exporta el estado del almacén a CSV."""
    medicamentos = Medicamento.objects.order_by('nombre')
    filas = [[
        m.nombre,
        m.get_categoria_display(),
        m.unidad,
        m.stock_actual,
        m.stock_minimo,
        'Sí' if m.stock_critico else 'No',
        m.precio_unitario,
        m.fecha_vencimiento.strftime('%d/%m/%Y') if m.fecha_vencimiento else '',
        m.proveedor,
    ] for m in medicamentos]
    return _csv_response(
        'reporte_inventario',
        ['Medicamento', 'Categoría', 'Unidad', 'Stock actual', 'Stock mínimo', 'Stock crítico', 'Precio (S/)', 'Vencimiento', 'Proveedor'],
        filas,
    )


@login_required
def imprimir_pacientes(request):
    """Vista imprimible de pacientes del periodo (guardar como PDF)."""
    periodo, inicio = _periodo_inicio(request)
    pacientes = Paciente.objects.filter(fecha_registro__date__gte=inicio).order_by('apellidos')
    return render(request, 'reportes/imprimir_pacientes.html', {
        'periodo': periodo,
        'pacientes': pacientes,
    })


@login_required
def imprimir_atenciones(request):
    """Vista imprimible de atenciones del periodo (guardar como PDF)."""
    periodo, inicio = _periodo_inicio(request)
    atenciones = Atencion.objects.select_related('paciente', 'medico').filter(
        fecha_atencion__date__gte=inicio,
    ).order_by('fecha_atencion')
    return render(request, 'reportes/imprimir_atenciones.html', {
        'periodo': periodo,
        'atenciones': atenciones,
    })


@login_required
def imprimir_inventario(request):
    """Vista imprimible del estado del almacén (guardar como PDF)."""
    criticos = Medicamento.objects.filter(stock_actual__lte=F('stock_minimo'))
    return render(request, 'reportes/imprimir_inventario.html', {
        'medicamentos': Medicamento.objects.order_by('nombre'),
        'total_criticos': criticos.count(),
    })
