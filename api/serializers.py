from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import Profile
from atenciones.models import Atencion, SignosVitales
from inventario.models import Medicamento, MovimientoInventario
from pacientes.models import Paciente
from portal.models import Cita, Estudiante


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'role', 'colegiatura', 'telefono')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'nombre_completo', 'profile')


class PacienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    edad = serializers.IntegerField(read_only=True)

    class Meta:
        model = Paciente
        fields = (
            'id',
            'nombres',
            'apellidos',
            'nombre_completo',
            'dni',
            'fecha_nacimiento',
            'edad',
            'sexo',
            'telefono',
            'direccion',
            'tipo_sangre',
            'alergias',
            'activo',
            'fecha_registro',
        )
        read_only_fields = ('fecha_registro',)


class SignosVitalesSerializer(serializers.ModelSerializer):
    presion_arterial = serializers.CharField(read_only=True)

    class Meta:
        model = SignosVitales
        fields = (
            'id',
            'atencion',
            'temperatura',
            'presion_sistolica',
            'presion_diastolica',
            'presion_arterial',
            'pulso',
            'frecuencia_respiratoria',
            'saturacion_oxigeno',
            'peso',
            'talla',
            'registrado_en',
        )
        read_only_fields = ('registrado_en',)


class AtencionSerializer(serializers.ModelSerializer):
    paciente_detalle = PacienteSerializer(source='paciente', read_only=True)
    signos_vitales = SignosVitalesSerializer(read_only=True)

    class Meta:
        model = Atencion
        fields = (
            'id',
            'paciente',
            'paciente_detalle',
            'medico',
            'fecha_atencion',
            'motivo_consulta',
            'anamnesis',
            'diagnostico',
            'tratamiento',
            'observaciones',
            'nivel_triage',
            'estado',
            'signos_vitales',
        )
        read_only_fields = ('fecha_atencion',)


class MedicamentoSerializer(serializers.ModelSerializer):
    stock_critico = serializers.BooleanField(read_only=True)

    class Meta:
        model = Medicamento
        fields = (
            'id',
            'nombre',
            'descripcion',
            'categoria',
            'unidad',
            'stock_actual',
            'stock_minimo',
            'stock_critico',
            'precio_unitario',
            'fecha_vencimiento',
            'proveedor',
        )


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    medicamento_nombre = serializers.CharField(source='medicamento.nombre', read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = (
            'id',
            'medicamento',
            'medicamento_nombre',
            'tipo',
            'cantidad',
            'fecha',
            'motivo',
            'usuario',
            'atencion',
        )
        read_only_fields = ('fecha', 'usuario')


class EstudianteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    escuela_nombre = serializers.CharField(source='get_escuela_display', read_only=True)
    tiene_cuenta = serializers.BooleanField(read_only=True)

    class Meta:
        model = Estudiante
        fields = (
            'id',
            'codigo',
            'dni',
            'nombres',
            'apellidos',
            'nombre_completo',
            'escuela',
            'escuela_nombre',
            'ciclo',
            'correo_institucional',
            'matriculado',
            'tiene_cuenta',
        )
        read_only_fields = ('user', 'paciente')


class CitaSerializer(serializers.ModelSerializer):
    estudiante_detalle = EstudianteSerializer(source='estudiante', read_only=True)
    estado_nombre = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Cita
        fields = (
            'id',
            'estudiante',
            'estudiante_detalle',
            'fecha',
            'hora',
            'motivo',
            'estado',
            'estado_nombre',
            'creada_en',
            'atencion',
        )
        read_only_fields = ('creada_en', 'atencion')
