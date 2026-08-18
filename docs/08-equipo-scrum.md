# 08 — Equipo Scrum

Roles del equipo **TEAM DEVELOPERS ON PYTHON** para el Proyecto Integrador de
Programación Web II. Según el esquema del docente, cada integrante asume un rol
y **los roles pueden rotar entre sprints**.

## 1. Asignación de roles

| Rol | Responsabilidad | Integrante | Evidencia en el proyecto |
|---|---|---|---|
| Scrum Master | Coordina el equipo y gestiona el Product Backlog | Huaman Prejo, Saul | [`docs/05-product-backlog.md`](05-product-backlog.md) con user stories y plan de sprints al 100 % |
| Backend Developer | Models, vistas FBVs, admin, migraciones | Aguilar Rivera, Elvis Antoni | Vistas basadas en funciones en `accounts/`, `pacientes/`, `atenciones/`, `inventario/`, `portal/` y `reportes/` |
| Frontend Developer | Templates HTML/Bootstrap, `base.html` | Huaman Prejo, Saul | `templates/base.html`, plantillas por módulo, interfaz responsiva con Bootstrap 5 |
| QA / Tester | Verificar cada funcionalidad y datos de prueba | Aguilar Rivera, Elvis Antoni | 82 pruebas automatizadas (pytest) y usuarios de demostración en `seed_demo` |
| DevOps / Docs | `requirements.txt`, estructura de carpetas, documentación | Huaman Prejo, Saul | `docs/` completa, despliegue en Vercel + Neon, CI en GitHub Actions |

> Los roles de Frontend, QA y DevOps fueron cubiertos por ambos integrantes de
> forma rotativa entre sprints, tal como permite el esquema del docente.

## 2. Usuarios de demostración (datos de prueba)

Creados por el comando `python manage.py seed_demo`:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `medico` | `medico123` | Médico |
| `enfermera` | `enfermera123` | Enfermero/a |
| `farmacia` | `farmacia123` | Farmacéutico/a |
| `estudiante` | `estudiante123` | Estudiante (portal) |

Además se carga un padrón de 6 estudiantes para probar el registro del portal.

## 3. Lista de verificación por sprint

### Sprint 1 — Módulo base + HTML (6 pts)

- [x] CRUD funcional de pacientes (crear, listar, detalle, editar, retirar).
- [x] `admin` registrado con datos de prueba.
- [x] Formularios HTML manuales (sin Django Forms).
- [x] `manage.py check` sin errores.

### Sprint 2 — Relación + Bootstrap (6 pts)

- [x] `unique_together = ('atencion', 'medicamento')` en `RecetaMedicamento`.
- [x] Estados con `choices` y badges de color (triage, atención, cita, movimiento).
- [x] Retiro lógico (cambio de estado) en lugar de eliminación.
- [x] Interfaz con Bootstrap 5: navbar, tablas, badges y formularios.

### Sprint 3 — Sistema completo (8 pts)

- [x] Autenticación con login/logout (`/cuentas/login/`).
- [x] Gestión de usuarios web con `create_user()`.
- [x] Filtro por rol: el administrador ve todo; cada rol ve solo lo suyo.
- [x] Reportes por periodo con filtro `request.GET.get('periodo')`.
- [x] Exportación CSV de pacientes, atenciones e inventario.
- [x] Despliegue en producción (Vercel + Neon PostgreSQL).

## 4. Repositorio

- GitHub: [TEAM--DEVELOPERS-ON-PYTHON](https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON)
- Producción: <https://topico-unh.vercel.app>