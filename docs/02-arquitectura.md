# 02 — Arquitectura del sistema

## 1. Vista general

El sistema sigue la arquitectura **MTV (Model–Template–View)** de Django,
complementada con una **API REST** construida con Django REST Framework.

```
┌───────────────────────────────────────────────────────────┐
│                        Navegador                          │
│    Bootstrap 5 · Bootstrap Icons · Chart.js (CDN)         │
└───────────────▲───────────────────────────▲───────────────┘
                │ HTML (Django Templates)   │ JSON (API REST)
┌───────────────┴───────────────────────────┴───────────────┐
│                        Django 5.1                         │
│  ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌───────────┐  │
│  │ accounts │ │ pacientes │ │ atenciones │ │inventario │  │
│  └──────────┘ └───────────┘ └────────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────────────┐   │
│  │ reportes │ │  portal  │ │ api (DRF: ser + viewsets) │   │
│  └──────────┘ └──────────┘ └───────────────────────────┘   │
└───────────────────────────┬───────────────────────────────┘
                            │ ORM
                ┌───────────▼───────────┐
                │  SQLite (desarrollo)  │
                │ PostgreSQL (prod. *)  │
                └───────────────────────┘
```
\* Planificado para el Sprint 4.

## 2. Aplicaciones Django

| App | Responsabilidad | Modelos |
|---|---|---|
| `accounts` | Autenticación, roles y perfiles. Comando `seed_demo` | `Profile` |
| `pacientes` | Datos maestros de pacientes | `Paciente` |
| `atenciones` | Atención médica, triage y signos vitales | `Atencion`, `SignosVitales` |
| `inventario` | Almacén de medicamentos y trazabilidad de stock | `Medicamento`, `MovimientoInventario` |
| `portal` | Portal de estudiantes: padrón, registro en 2 pasos y citas | `Estudiante`, `Cita` |
| `reportes` | Dashboard e indicadores (sin modelos propios) | — |
| `api` | Exposición REST de los modelos (sin modelos propios) | — |

## 3. Decisiones técnicas

| Decisión | Justificación |
|---|---|
| `User` de Django + `Profile` OneToOne | Evita migraciones complejas de un custom user; el perfil agrega rol, colegiatura y teléfono. Se crea automáticamente con una señal `post_save`. |
| Padrón `Estudiante` con `matriculado` | Fuente de verdad de la matrícula; el registro del portal exige código y DNI que coincidan con el padrón. |
| `Cita` con slots fijos de 30 min | Los horarios (08:00–12:30 y 14:00–16:30) se derivan de constantes; constraint único sobre `(fecha, hora)` para estados activos evita dobles reservas. |
| Registro en dos pasos con sesión | Paso 1 valida el padrón; Paso 2 crea `User` + `Profile` (ESTUDIANTE) + `Paciente` y vincula todo. |
| Triage como `TextChoices` en `Atencion` | Cinco niveles estándar (Rojo/Naranja/Amarillo/Verde/Azul) siguiendo el modelo de triage hospitalario. |
| Stock actualizado en `MovimientoInventario.save()` | Garantiza consistencia: toda variación de stock queda registrada como movimiento (entrada suma, salida resta y valida stock, ajuste fija el valor). |
| `TokenAuthentication` de DRF | Simple, adecuada para clientes internos; se puede migrar a JWT sin cambiar los viewsets. |
| Paginación y filtros globales en DRF | `PAGE_SIZE=20`, `SearchFilter` y `OrderingFilter` configurados en `settings.py`. |
| Bootstrap/Chart.js por CDN | Sin build de frontend: menor complejidad para el equipo. |
| Variables de entorno para settings sensibles | `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`. |

## 4. Flujo principal: atención con triage

```
Paciente llega al Tópico
        │
        ▼
¿Registrado? ──No──► Registrar paciente (pacientes/nuevo)
        │Sí                    │
        ▼◄─────────────────────┘
Crear atención (motivo + nivel de triage)  → estado: EN_ESPERA
        │
        ▼
Cola de triage (ordenada por gravedad y hora de llegada)
        │
        ▼
Registrar signos vitales → estado: EN_ATENCION
        │
        ▼
Diagnóstico y tratamiento → estado: ATENDIDO o DERIVADO
        │
        ▼
Salida de medicamentos del inventario (opcional, vinculada a la atención)
```

## 5. Flujo del portal de estudiantes

```
Estudiante accede a /portal/
        │
        ▼
Paso 1: código + DNI → se validan contra el padrón (matriculado, sin cuenta)
        │
        ▼
Paso 2: datos complementarios + contraseña → se crean User (ESTUDIANTE),
       Profile, Paciente y se vincula el padrón
        │
        ▼
Panel del estudiante (escuela, ciclo) y reserva de cita (slot único)
        │
        ▼
Personal de salud → Agenda de citas → "Atender" → se crea Atención
       y la cita pasa a estado ATENDIDA
```

## 6. Seguridad

- Todas las vistas web requieren autenticación (`@login_required`).
- La API exige `IsAuthenticated` con token o sesión.
- El registro del portal solo valida a estudiantes presentes en el padrón con
  matrícula activa; la DNI debe coincidir y el usuario no debe tener cuenta previa.
- Las citas solo pueden cancelarse por su propio titular.
- Protección CSRF, XFrame y middlewares de seguridad de Django activos.
- `DEBUG` y `SECRET_KEY` configurables por variables de entorno.

## 7. Calidad

- **58 pruebas automatizadas** (pytest + pytest-django).
- CI en GitHub Actions: `manage.py check`, verificación de migraciones y pruebas en Python 3.12 y 3.13.
- Git Flow: `main` (estable) ← `develop` (integración) ← `feature/*`.
