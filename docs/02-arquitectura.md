# 02 — Arquitectura del sistema

## 1. Vista general

El sistema sigue la arquitectura **MTV (Model–Template–View)** de Django con
**vistas basadas en funciones (FBV)** y **HTML manual** (sin Django Forms, sin
DRF y sin frameworks JS), según las restricciones del docente.

```
┌───────────────────────────────────────────────────────────┐
│                        Navegador                          │
│    Bootstrap 5 · Bootstrap Icons · Chart.js (CDN)         │
└─────────────────────────────▲─────────────────────────────┘
                              │ HTML (Django Templates)
┌─────────────────────────────┴─────────────────────────────┐
│                        Django 5.1                         │
│  ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌───────────┐  │
│  │ accounts │ │ pacientes │ │ atenciones │ │inventario │  │
│  └──────────┘ └───────────┘ └────────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────┐                                 │
│  │ reportes │ │  portal  │                                 │
│  └──────────┘ └──────────┘                                 │
└───────────────────────────┬───────────────────────────────┘
                            │ ORM
                ┌───────────▼───────────┐
                │  SQLite (desarrollo)  │
                │  PostgreSQL (Neon)    │
                └───────────────────────┘
```

## 2. Aplicaciones Django

| App | Responsabilidad | Modelos |
|---|---|---|
| `accounts` | `CustomUser` con `ROL_CHOICES`, login/logout, CRUD de usuarios web (FBV) | `CustomUser` |
| `pacientes` | Datos maestros de pacientes | `Paciente` |
| `atenciones` | Atención médica, triage, signos vitales y recetas | `Atencion`, `SignosVitales`, `RecetaMedicamento` |
| `inventario` | Almacén de medicamentos y trazabilidad de stock | `Medicamento`, `MovimientoInventario` |
| `portal` | Portal de estudiantes: padrón, registro en 2 pasos y citas | `Estudiante`, `Cita` |
| `reportes` | Dashboard e indicadores (sin modelos propios) | — |

## 3. Decisiones técnicas

| Decisión | Justificación |
|---|---|
| `CustomUser` con `ROL_CHOICES` | El rol es propio del dominio y vive en el mismo modelo del usuario (requisito del docente); no se usa un perfil separado. |
| Vistas basadas en funciones (FBV) | Cumple la restricción del proyecto: solo FBVs, sin CBVs. |
| HTML manual (sin Django Forms) | El docente exige formularios escritos a mano; `request.POST` se valida en las vistas. |
| Padrón `Estudiante` con `matriculado` | Fuente de verdad de la matrícula; el registro del portal exige código y DNI que coincidan con el padrón. |
| `Cita` con slots fijos de 30 min | Los horarios (08:00–12:30 y 14:00–16:30) se derivan de constantes; constraint único sobre `(fecha, hora)` para estados activos evita dobles reservas. |
| Registro en dos pasos con sesión | Paso 1 valida el padrón; Paso 2 crea el `CustomUser` (ESTUDIANTE) + `Paciente` y vincula todo. |
| Triage como `TextChoices` en `Atencion` | Cinco niveles estándar (Rojo/Naranja/Amarillo/Verde/Azul) siguiendo el modelo de triage hospitalario. |
| `RecetaMedicamento` con `unique_together (atencion, medicamento)` | Evita recetar dos veces el mismo medicamento en una misma atención (patrón exigido por el docente). |
| Stock actualizado en `MovimientoInventario.save()` | Garantiza consistencia: toda variación de stock queda registrada como movimiento (entrada suma, salida resta y valida stock, ajuste fija el valor). |
| Bootstrap/Chart.js por CDN | Sin build de frontend: menor complejidad para el equipo. |
| Variables de entorno para settings sensibles | `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` y base de datos. |

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
Recetar medicamentos → se descuenta stock del inventario
        │
        ▼
Salida de medicamentos del inventario (vinculada a la atención)
```

## 5. Flujo del portal de estudiantes

```
Estudiante accede a /portal/
        │
        ▼
Paso 1: código + DNI → se validan contra el padrón (matriculado, sin cuenta)
        │
        ▼
Paso 2: datos complementarios + contraseña → se crean CustomUser (ESTUDIANTE)
        y Paciente, y se vincula el padrón
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
- Permisos por rol mediante decoradores y control de acciones en la interfaz.
- El registro del portal solo valida a estudiantes presentes en el padrón con
  matrícula activa; la DNI debe coincidir y el usuario no debe tener cuenta previa.
- Las citas solo pueden cancelarse por su propio titular.
- Protección CSRF, XFrame y middlewares de seguridad de Django activos.
- `DEBUG` y `SECRET_KEY` configurables por variables de entorno.

## 7. Calidad

- **82 pruebas automatizadas** (pytest + pytest-django).
- CI en GitHub Actions: `manage.py check`, verificación de migraciones y pruebas en Python 3.12 y 3.13.
- Git Flow: `main` (estable) ← `develop` (integración) ← `feature/*`.