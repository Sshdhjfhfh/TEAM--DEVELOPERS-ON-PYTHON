from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import MedicamentoForm, MovimientoForm
from .models import Medicamento, MovimientoInventario


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
@require_http_methods(['GET', 'POST'])
def crear_medicamento(request):
    """Registra un nuevo medicamento en el almacén."""
    form = MedicamentoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        medicamento = form.save()
        messages.success(request, f'Medicamento "{medicamento.nombre}" registrado.')
        return redirect('inventario:detalle', pk=medicamento.pk)
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Registrar medicamento'})


@login_required
@require_http_methods(['GET', 'POST'])
def editar_medicamento(request, pk):
    """Edita un medicamento existente."""
    medicamento = get_object_or_404(Medicamento, pk=pk)
    form = MedicamentoForm(request.POST or None, instance=medicamento)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Medicamento "{medicamento.nombre}" actualizado.')
        return redirect('inventario:detalle', pk=medicamento.pk)
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Editar medicamento', 'medicamento': medicamento})


@login_required
def lista_movimientos(request):
    """Historial de movimientos del almacén."""
    movimientos = MovimientoInventario.objects.select_related('medicamento', 'usuario').all()
    tipo = request.GET.get('tipo', '')
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    return render(request, 'inventario/movimientos.html', {'movimientos': movimientos, 'tipo': tipo})


@login_required
@require_http_methods(['GET', 'POST'])
def registrar_movimiento(request):
    """Registra un movimiento (entrada/salida/ajuste) de stock."""
    form = MovimientoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        movimiento = form.save(commit=False)
        movimiento.usuario = request.user
        movimiento.save()
        messages.success(request, f'{movimiento.get_tipo_display()} de {movimiento.cantidad} registrada.')
        return redirect('inventario:movimientos')
    return render(request, 'inventario/form_movimiento.html', {'form': form})
