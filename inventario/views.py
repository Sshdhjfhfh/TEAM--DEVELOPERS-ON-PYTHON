from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import ROLES_GESTION_INVENTARIO, rol_requerido

from .models import Medicamento, MovimientoInventario


def _error_para_mensaje(exc):
    """Convierte un ValidationError en un mensaje legible."""
    if hasattr(exc, 'message_dict'):
        return '; '.join(
            f'{campo}: {" ".join(errs)}' for campo, errs in exc.message_dict.items()
        )
    return '; '.join(str(e) for e in exc.messages)


def _medicamento_desde_post(request):
    """Convierte el POST en los datos de un Medicamento."""
    fecha_vencimiento = request.POST.get('fecha_vencimiento', '')
    return {
        'nombre': request.POST.get('nombre', '').strip(),
        'descripcion': request.POST.get('descripcion', '').strip(),
        'categoria': request.POST.get('categoria', Medicamento.Categoria.MEDICAMENTO),
        'unidad': request.POST.get('unidad', 'unidad').strip(),
        'stock_actual': int(request.POST.get('stock_actual') or 0),
        'stock_minimo': int(request.POST.get('stock_minimo') or 0),
        'precio_unitario': float(request.POST.get('precio_unitario') or 0),
        'fecha_vencimiento': (
            datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date() if fecha_vencimiento else None
        ),
        'proveedor': request.POST.get('proveedor', '').strip(),
    }


@login_required
def lista_medicamentos(request):
    """Lista del almacén con búsqueda y resaltado de stock crítico."""
    q = request.GET.get('q', '').strip()
    medicamentos = Medicamento.objects.all()
    if q:
        medicamentos = medicamentos.filter(
            nombre__icontains=q,
        ) | medicamentos.filter(
            proveedor__icontains=q,
        )
    criticos = Medicamento.objects.filter(stock_actual__lte=F('stock_minimo')).count()
    return render(
        request,
        'inventario/lista.html',
        {'medicamentos': medicamentos.distinct(), 'q': q, 'criticos': criticos},
    )


@login_required
def detalle_medicamento(request, pk):
    """Detalle de un medicamento con su historial de movimientos."""
    medicamento = get_object_or_404(Medicamento, pk=pk)
    movimientos = medicamento.movimientos.select_related('usuario').all()
    return render(
        request,
        'inventario/detalle.html',
        {'medicamento': medicamento, 'movimientos': movimientos},
    )


@login_required
@rol_requerido(*ROLES_GESTION_INVENTARIO)
@require_http_methods(['GET', 'POST'])
def crear_medicamento(request):
    """Registra un nuevo medicamento en el almacén."""
    errores = None
    if request.method == 'POST':
        try:
            medicamento = Medicamento(**_medicamento_desde_post(request))
            medicamento.save()
            messages.success(request, f'Medicamento "{medicamento.nombre}" registrado.')
            return redirect('inventario:detalle', pk=medicamento.pk)
        except (ValueError, ValidationError) as exc:
            errores = _error_para_mensaje(exc) if isinstance(exc, ValidationError) else str(exc)
    return render(request, 'inventario/form.html', {
        'titulo': 'Registrar medicamento',
        'datos': request.POST if request.method == 'POST' else None,
        'errores': errores,
        'categorias': Medicamento.Categoria.choices,
    })


@login_required
@rol_requerido(*ROLES_GESTION_INVENTARIO)
@require_http_methods(['GET', 'POST'])
def editar_medicamento(request, pk):
    """Edita un medicamento existente."""
    medicamento = get_object_or_404(Medicamento, pk=pk)
    errores = None
    if request.method == 'POST':
        try:
            datos = _medicamento_desde_post(request)
            for campo, valor in datos.items():
                setattr(medicamento, campo, valor)
            medicamento.save()
            messages.success(request, f'Medicamento "{medicamento.nombre}" actualizado.')
            return redirect('inventario:detalle', pk=medicamento.pk)
        except (ValueError, ValidationError) as exc:
            errores = _error_para_mensaje(exc) if isinstance(exc, ValidationError) else str(exc)
    return render(request, 'inventario/form.html', {
        'titulo': 'Editar medicamento',
        'medicamento': medicamento,
        'datos': request.POST if request.method == 'POST' else None,
        'errores': errores,
        'categorias': Medicamento.Categoria.choices,
    })


@login_required
def lista_movimientos(request):
    """Historial de movimientos del almacén."""
    movimientos = MovimientoInventario.objects.select_related('medicamento', 'usuario').all()
    tipo = request.GET.get('tipo', '')
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    return render(request, 'inventario/movimientos.html', {'movimientos': movimientos, 'tipo': tipo})


@login_required
@rol_requerido(*ROLES_GESTION_INVENTARIO)
@require_http_methods(['GET', 'POST'])
def registrar_movimiento(request):
    """Registra un movimiento (entrada/salida/ajuste) de stock."""
    medicamentos = Medicamento.objects.all()
    errores = None
    if request.method == 'POST':
        try:
            movimiento = MovimientoInventario(
                medicamento=get_object_or_404(Medicamento, pk=request.POST.get('medicamento')),
                tipo=request.POST.get('tipo', ''),
                cantidad=int(request.POST.get('cantidad') or 0),
                motivo=request.POST.get('motivo', '').strip(),
                usuario=request.user,
            )
            movimiento.save()
            messages.success(
                request,
                f'{movimiento.get_tipo_display()} de {movimiento.cantidad} registrada.',
            )
            return redirect('inventario:movimientos')
        except (ValueError, ValidationError) as exc:
            errores = _error_para_mensaje(exc) if isinstance(exc, ValidationError) else str(exc)
    return render(request, 'inventario/form_movimiento.html', {
        'medicamentos': medicamentos,
        'tipos': MovimientoInventario.Tipo.choices,
        'datos': request.POST if request.method == 'POST' else None,
        'errores': errores,
    })
