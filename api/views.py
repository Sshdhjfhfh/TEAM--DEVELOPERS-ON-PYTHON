from django.contrib.auth.models import User
from django.db.models import F
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from accounts.models import Profile
from atenciones.models import Atencion, SignosVitales
from inventario.models import Medicamento, MovimientoInventario
from pacientes.models import Paciente
from portal.models import Cita, Estudiante

from .serializers import (
    AtencionSerializer,
    CitaSerializer,
    EstudianteSerializer,
    MedicamentoSerializer,
    MovimientoInventarioSerializer,
    PacienteSerializer,
    ProfileSerializer,
    SignosVitalesSerializer,
    UserSerializer,
)


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """Usuarios del sistema. Acceso de solo lectura."""

    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering_fields = ('username', 'last_name')


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Perfiles (roles) de los usuarios."""

    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    search_fields = ('user__username', 'user__first_name', 'role')
    filterset_fields = ('role',)


class PacienteViewSet(viewsets.ModelViewSet):
    """CRUD completo de pacientes."""

    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    search_fields = ('dni', 'nombres', 'apellidos', 'telefono')
    ordering_fields = ('apellidos', 'fecha_registro')
    ordering = ('apellidos',)


class AtencionViewSet(viewsets.ModelViewSet):
    """CRUD completo de atenciones médicas."""

    queryset = Atencion.objects.select_related('paciente', 'medico').all()
    serializer_class = AtencionSerializer
    search_fields = (
        'paciente__dni',
        'paciente__nombres',
        'paciente__apellidos',
        'motivo_consulta',
        'diagnostico',
    )
    ordering_fields = ('fecha_atencion', 'nivel_triage')
    ordering = ('-fecha_atencion',)

    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        triage = self.request.query_params.get('triage')
        if estado:
            queryset = queryset.filter(estado=estado)
        if triage:
            queryset = queryset.filter(nivel_triage=triage)
        return queryset


class SignosVitalesViewSet(viewsets.ModelViewSet):
    """CRUD de signos vitales asociados a las atenciones."""

    queryset = SignosVitales.objects.select_related('atencion').all()
    serializer_class = SignosVitalesSerializer


class MedicamentoViewSet(viewsets.ModelViewSet):
    """CRUD del almacén de medicamentos e insumos."""

    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer
    search_fields = ('nombre', 'proveedor', 'descripcion')
    ordering_fields = ('nombre', 'stock_actual', 'fecha_vencimiento')
    ordering = ('nombre',)

    def get_queryset(self):
        queryset = super().get_queryset()
        criticos = self.request.query_params.get('criticos')
        if criticos == 'true':
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
        return queryset


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """CRUD de movimientos de inventario (entradas, salidas y ajustes)."""

    queryset = MovimientoInventario.objects.select_related('medicamento', 'usuario').all()
    serializer_class = MovimientoInventarioSerializer
    search_fields = ('medicamento__nombre', 'motivo')
    ordering_fields = ('fecha',)
    ordering = ('-fecha',)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class EstudianteViewSet(viewsets.ReadOnlyModelViewSet):
    """Padrón de estudiantes matriculados. Acceso de solo lectura."""

    queryset = Estudiante.objects.select_related('user', 'paciente').all()
    serializer_class = EstudianteSerializer
    search_fields = ('codigo', 'dni', 'nombres', 'apellidos')
    ordering_fields = ('apellidos', 'ciclo')
    ordering = ('apellidos',)


class CitaViewSet(viewsets.ModelViewSet):
    """Reservas de atención del portal de estudiantes."""

    queryset = Cita.objects.select_related('estudiante', 'atencion').all()
    serializer_class = CitaSerializer
    search_fields = (
        'estudiante__codigo',
        'estudiante__nombres',
        'estudiante__apellidos',
        'motivo',
    )
    ordering_fields = ('fecha', 'hora')
    ordering = ('-fecha', '-hora')

    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def perform_create(self, serializer):
        estudiante = getattr(self.request.user, 'estudiante', None)
        if estudiante is None:
            raise ValidationError({
                'estudiante': 'Debe autenticarse como estudiante matriculado para reservar.',
            })
        serializer.save(estudiante=estudiante)
