from django import forms

from .models import Medicamento, MovimientoInventario


class MedicamentoForm(forms.ModelForm):
    """Formulario de registro y edición de medicamentos."""

    class Meta:
        model = Medicamento
        fields = (
            'nombre',
            'descripcion',
            'categoria',
            'unidad',
            'stock_actual',
            'stock_minimo',
            'precio_unitario',
            'fecha_vencimiento',
            'proveedor',
        )
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MovimientoForm(forms.ModelForm):
    """Formulario para registrar movimientos de inventario."""

    class Meta:
        model = MovimientoInventario
        fields = ('medicamento', 'tipo', 'cantidad', 'motivo', 'atencion')
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'atencion': forms.Select(attrs={'class': 'form-select'}),
        }
