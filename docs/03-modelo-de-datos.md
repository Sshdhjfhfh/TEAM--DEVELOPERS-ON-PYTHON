# 03 — Modelo de datos

## 1. Diagrama entidad–relación (lógico)

```
┌──────────────────┐ 1      n ┌──────────────────┐
│    CustomUser    │──────────│     Paciente     │
│   (ROL_CHOICES)  │(registró)│ dni (único)      │
└────────┬─────────┘          │ nombres/apellidos│
         │                    │ tipo_sangre      │
         │ 1 (médico)         │ alergias         │
         │ n ┌──────────────┐ │ activo (baja)    │
         ├────│   Atencion   │ │                  │
         │   │ nivel_triage  │ └────────┬─────────┘
         │   │ estado        │          │ 1
         │   │ motivo_consulta│          │ n
         │   │ diagnostico   │ ┌────────▼─────────┐
         │   │ tratamiento   │ │      Cita        │
         │   └──────┬────────┘ │ estudiante (FK)  │
         │          │ 1        │ fecha/hora       │
         │          │ 1        └────────┬─────────┘
         │   ┌──────▼─────────┐         │ 0..1
         │   │ SignosVitales  │         │
         │   │ temperatura    │ ┌───────▼────────┐
         │   │ presión S/D    │ │ (vinculación)  │
         │   │ pulso, FR, SpO2│ └────────────────┘
         │   │ peso, talla    │
         │   └────────────────┘
         │ 1     n ┌──────────────────────┐ n       1 ┌──────────────┐
         └────────│ MovimientoInventario │───────────│ Medicamento  │
                 │ tipo (E/S/Ajuste)    │           │ stock_actual │
                 │ cantidad             │           │ stock_minimo │
                 │ atencion (opcional)  │           │ categoria    │
                 └──────────────────────┘           └──────────────┘
                       n       1 ┌──────────────┐
              RecetaMedicamento──│  Medicamento │
              (atencion, medicamento)           │
                                 └──────────────┘
               UNIQUE (atencion, medicamento)

CustomUser ──1──── 1──── Estudiante (padrón)
CustomUser ──1──── 1──── Paciente (ficha de estudiante)
Estudiante ──1──── n──── Cita ────0..1──── Atencion
```

## 2. Entidades

### accounts.CustomUser
`AUTH_USER_MODEL` del proyecto. Hereda de `AbstractUser` y agrega el rol propio
del dominio. El **retiro lógico** se implementa con el atributo `activo`.

| Campo | Tipo | Detalle |
|---|---|---|
| username / first_name / last_name / email | (AbstractUser) | Estándar de Django |
| rol | CharField (choices `ROL_CHOICES`) | `ADMIN`, `MEDICO`, `ENFERMERO`, `FARMACEUTICO`, `ESTUDIANTE` |
| colegiatura | CharField(30) | Opcional |
| telefono | CharField(20) | Opcional |
| activo | BooleanField (defecto True) | Baja lógica; se usa en lugar de `is_active` para no romper la autenticación |
| es_estudiante | property | True si `rol == ESTUDIANTE` |

Los usuarios se crean con `create_user()` (gestión web en `accounts/`) y con
`seed_demo`. No hay modelo `Profile`.

### pacientes.Paciente
| Campo | Tipo | Detalle |
|---|---|---|
| nombres / apellidos | CharField(100) | Obligatorios |
| dni | CharField(8) único | Solo dígitos (validado), mín. 8 |
| fecha_nacimiento | DateField | Se deriva la propiedad `edad` |
| sexo | CharField choices | `M`, `F` |
| tipo_sangre | CharField choices | `O±`, `A±`, `B±`, `AB±`, `DES` |
| alergias | TextField | Opcional (se resalta en la ficha) |
| activo | BooleanField | Baja lógica |
| registrado_por | FK → CustomUser (SET_NULL) | Trazabilidad |
| fecha_registro | DateTimeField auto | — |

### atenciones.Atencion
| Campo | Tipo | Detalle |
|---|---|---|
| paciente | FK → Paciente (CASCADE) | related_name `atenciones` |
| medico | FK → CustomUser (SET_NULL) | Opcional |
| fecha_atencion | DateTimeField auto | — |
| motivo_consulta | TextField | Obligatorio |
| anamnesis / diagnostico / tratamiento / observaciones | TextField | Opcionales |
| nivel_triage | choices | `ROJO`, `NARANJA`, `AMARILLO` (defecto), `VERDE`, `AZUL` |
| estado | choices | `EN_ESPERA` (defecto), `EN_ATENCION`, `ATENDIDO`, `DERIVADO` |

### atenciones.SignosVitales
OneToOne con `Atencion` (related_name `signos_vitales`). Campos numéricos
opcionales: temperatura (°C), presión sistólica/diastólica (mmHg), pulso (lpm),
frecuencia respiratoria (rpm), saturación de oxígeno (%, 1–100), peso (kg),
talla (cm). Propiedad `presion_arterial` = `"120/80"`.

### atenciones.RecetaMedicamento
| Campo | Tipo | Detalle |
|---|---|---|
| atencion | FK → Atencion (CASCADE) | related_name `recetas` |
| medicamento | FK → Medicamento (CASCADE) | related_name `recetas` |
| cantidad | PositiveInteger | — |
| indicaciones | TextField | Opcional |

> **Restricción:** `unique_together = ('atencion', 'medicamento')` — el mismo
> medicamento no puede repetirse en una misma atención.

### inventario.Medicamento
| Campo | Tipo | Detalle |
|---|---|---|
| nombre | CharField(150) | — |
| categoria | choices | `MEDICAMENTO`, `INSUMO`, `EQUIPO` |
| unidad | CharField(20) | p. ej. tableta, frasco |
| stock_actual / stock_minimo | PositiveInteger | Propiedad `stock_critico` = actual ≤ mínimo |
| precio_unitario | Decimal(10,2) | En soles (S/) |
| fecha_vencimiento | DateField | Opcional |
| proveedor | CharField(100) | Opcional |

### inventario.MovimientoInventario
| Campo | Tipo | Detalle |
|---|---|---|
| medicamento | FK → Medicamento (CASCADE) | related_name `movimientos` |
| tipo | choices | `ENTRADA` (suma), `SALIDA` (resta y **valida stock**), `AJUSTE` (fija el stock) |
| cantidad | PositiveInteger ≥ 1 | — |
| usuario | FK → CustomUser (SET_NULL) | Asignado automáticamente en las vistas |
| atencion | FK → Atencion (SET_NULL) | Opcional: vincula el consumo a una atención |

> **Regla de negocio:** el stock del medicamento se actualiza dentro de
> `MovimientoInventario.save()`; una salida mayor al stock disponible lanza
> `ValidationError` y no se registra. La receta médica también descuenta stock.

### portal.Estudiante (padrón de matriculados)
| Campo | Tipo | Detalle |
|---|---|---|
| codigo | CharField(10) único | Código de matrícula UNH |
| dni | CharField(8) único | Debe coincidir al registrarse en el portal |
| nombres / apellidos | CharField(100) | Se autocompletan en el registro |
| escuela | choices | `SISTEMAS`, `CIVIL`, `AMBIENTAL`, `ELECTRONICA`, `ENFERMERIA`, `OBSTETRICIA`, `EDUCACION`, `DERECHO` |
| ciclo | PositiveSmallInteger | Nivel académico del estudiante |
| matriculado | BooleanField | Matrícula activa del semestre (si es falsa, no puede registrarse) |
| correo_institucional | EmailField | Opcional |
| user | OneToOne → CustomUser (SET_NULL) | Cuenta creada en el Paso 2; propiedad `tiene_cuenta` |
| paciente | OneToOne → Paciente (SET_NULL) | Ficha clínica vinculada al estudiante |

### portal.Cita
| Campo | Tipo | Detalle |
|---|---|---|
| estudiante | FK → Estudiante (CASCADE) | related_name `citas` |
| fecha | DateField | Solo lunes a viernes, futuro y máx. 30 días |
| hora | TimeField | Debe pertenecer a los slots (08:00–12:30, 14:00–16:30) |
| motivo | TextField | Motivo de la consulta |
| estado | choices | `PENDIENTE` (defecto), `CONFIRMADA`, `ATENDIDA`, `CANCELADA` |
| creada_en | DateTimeField auto | — |
| atencion | OneToOne → Atencion (SET_NULL) | Se llena al convertir la cita en atención |

> **Reglas de agenda:** cada estudiante solo puede tener una cita activa a la
> vez; el formulario oculta los slots ocupados y hay un constraint único
> `(fecha, hora)` para estados `PENDIENTE`/`CONFIRMADA`.

## 3. Convenciones

- Todas las claves primarias son `BigAutoField`.
- Los FK a usuarios usan `on_delete=SET_NULL` para conservar el historial.
- `verbose_name` en español en todos los campos (se refleja en el admin).
- Zona horaria: `America/Lima`; idioma: `es-pe`.