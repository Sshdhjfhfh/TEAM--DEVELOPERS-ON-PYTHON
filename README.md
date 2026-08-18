# Sistema de Gestión de Tópico UNH

[![CI](https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON/actions/workflows/ci.yml/badge.svg)](https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON/actions)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Tests](https://img.shields.io/badge/tests-82%20passed-brightgreen)
![Avance](https://img.shields.io/badge/avance-100%25-brightgreen)

Sistema web para la **gestión integral del Tópico de la Universidad Nacional
de Huancavelica (UNH)**: registro de pacientes, atenciones médicas con triage,
control de signos vitales, inventario de medicamentos e insumos, reportes
estadísticos con exportación y un **portal de estudiantes** para la reserva de
citas. Construido únicamente con **vistas basadas en funciones (FBV)** y
**HTML manual** (sin Django Forms, sin DRF, sin frameworks JS).

---

## Tabla de contenido

- [Características](#características)
- [Stack tecnológico](#stack-tecnológico)
- [Instalación](#instalación)
- [Usuarios de demostración](#usuarios-de-demostración)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Pruebas](#pruebas)
- [Documentación](#documentación)
- [Metodología y avance](#metodología-y-avance)
- [Equipo](#equipo)

---

## Características

| Módulo | Funcionalidad |
|---|---|
| **Cuentas** | Login/logout, usuarios con rol propio del dominio (Médico, Enfermero/a, Farmacéutico/a, Administrador, Estudiante), retiro lógico y CRUD de usuarios por el administrador con `create_user()` |
| **Pacientes** | Registro con DNI validado, historial clínico, búsqueda por DNI/nombre, alergias y tipo de sangre |
| **Atenciones** | Registro de atención con triage de 5 niveles (Rojo a Azul), estados (en espera / en atención / atendido / derivado), signos vitales y recetas médicas |
| **Cola de triage** | Cola priorizada en tiempo real: emergencias primero, ordenadas por hora de llegada |
| **Inventario** | Medicamentos, insumos y equipos; entradas/salidas/ajustes con actualización automática de stock y alertas de stock crítico |
| **Reportes** | Dashboard con indicadores y gráficos (Chart.js) por día, triage, estado y médico; valorización del inventario. Exportación a **CSV (Excel)** y vista **imprimible (PDF)** con filtro por periodo |
| **Portal de estudiantes** | Registro en dos pasos validado contra el padrón UNH, autocompletado de escuela y ciclo, y reserva de citas con horario del Tópico |
| **Cola en tiempo real** | El estudiante consulta su turno y posición en la cola del día, ordenada por triage |
| **Historia clínica** | El estudiante consulta sus atenciones, diagnósticos, tratamientos y recetas desde el portal |
| **Recetas digitales** | El personal receta medicamentos y el stock del inventario se descuenta automáticamente (un medicamento no se repite en la misma receta) |
| **Recordatorios** | Comando `recordar_citas` que avisa por correo 24 h antes de cada cita |
| **Agenda de citas** | Gestión por el personal de salud y conversión de una cita en atención médica |
| **Permisos por rol** | Control de acceso granular por módulo (clínico, farmacia, agenda) con decoradores y ocultado de acciones en la interfaz |
| **Notificaciones** | Correo institucional al estudiante al reservar, cancelar o atender su cita |

## Stack tecnológico

- **Backend:** Python 3.12+ · Django 5.1 (vistas basadas en funciones)
- **Frontend:** Django Templates (HTML manual) · Bootstrap 5.3 · Bootstrap Icons · Chart.js (CDN)
- **Base de datos:** SQLite (desarrollo) · PostgreSQL (producción/Neon)
- **Pruebas:** pytest + pytest-django (82 pruebas)
- **CI/CD:** GitHub Actions
- **Despliegue:** Vercel (serverless) + Neon PostgreSQL

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON.git
cd TEAM--DEVELOPERS-ON-PYTHON

# 2. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. (Opcional) Cargar datos de demostración
python manage.py seed_demo

# 6. Iniciar el servidor
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/> en el navegador.

Instalación detallada: [docs/07-guia-de-instalacion.md](docs/07-guia-de-instalacion.md).

## Usuarios de demostración

Tras ejecutar `python manage.py seed_demo`:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador (acceso a `/admin/`) |
| `medico` | `medico123` | Médico |
| `enfermera` | `enfermera123` | Enfermero/a |
| `farmacia` | `farmacia123` | Farmacéutico/a |
| `estudiante` | `estudiante123` | Estudiante (portal) |

> Solo para desarrollo. Nunca usar estas credenciales en producción.

## Estructura del proyecto

```
TEAM--DEVELOPERS-ON-PYTHON/
├── topico_project/        # Configuración del proyecto (settings, urls, wsgi)
├── accounts/              # CustomUser con ROL_CHOICES, login/logout y CRUD
│                          # de usuarios (FBV) + comando seed_demo
├── pacientes/             # Gestión de pacientes
├── atenciones/            # Atenciones médicas, triage, signos vitales y recetas
├── inventario/            # Medicamentos y movimientos de stock
├── reportes/              # Dashboard y reportes estadísticos (CSV/imprimible)
├── portal/                # Portal de estudiantes: padrón, registro y citas
├── templates/             # Plantillas HTML (base + una carpeta por módulo)
├── static/                # CSS e imágenes institucionales (logo UNH)
├── api/                   # Punto de entrada WSGI para Vercel (serverless)
├── docs/                  # Documentación del proyecto
├── .github/workflows/     # CI con GitHub Actions
├── manage.py
├── pytest.ini
└── requirements.txt
```

## Pruebas

```bash
pytest            # ejecuta las 82 pruebas
pytest -v         # modo detallado
python manage.py check   # verifica la configuración
```

Cobertura: modelos (validaciones, propiedades, lógica de stock, slots de
citas), vistas FBV (autenticación, CRUD, registro de estudiantes, reserva y
cancelación de citas, conversión a atención, permisos por rol, exportaciones
CSV e imprimibles, notificaciones de cita).

## Documentación

| Documento | Contenido |
|---|---|
| [01 — Visión y alcance](docs/01-vision-y-alcance.md) | Problema, objetivos, alcance del producto |
| [02 — Arquitectura](docs/02-arquitectura.md) | Diseño del sistema, apps, decisiones técnicas |
| [03 — Modelo de datos](docs/03-modelo-de-datos.md) | Entidades, relaciones y diagrama ER |
| [04 — Reportes y exportaciones](docs/04-reportes.md) | Filtros, vistas imprimibles y CSV |
| [05 — Product Backlog](docs/05-product-backlog.md) | User stories, sprints y avance (100 %) |
| [06 — Manual de usuario](docs/06-manual-de-usuario.md) | Guía de uso pantalla por pantalla |
| [07 — Guía de instalación](docs/07-guia-de-instalacion.md) | Instalación detallada y despliegue |
| [08 — Equipo Scrum](docs/08-equipo-scrum.md) | Roles del equipo y evidencia en el proyecto |
| [09 — Retrospectiva](docs/09-retrospectiva.md) | Lecciones aprendidas por sprint |

## Metodología y avance

El proyecto se desarrolla con **Scrum** y **Git Flow** (ramas `main`,
`develop` y `feature/*`).

| Sprint | Objetivo | Estado |
|---|---|---|
| Sprint 0 | Entorno, repositorio, backlog y wireframes | Completado |
| Sprint 1 | Autenticación, pacientes y atenciones con triage | Completado |
| Sprint 2 | Inventario, reportes y CI | Completado |
| Sprint 3 | Portal de estudiantes (padrón, registro y citas) | Completado |
| Sprint 4 | Exportación CSV/imprimible, permisos por rol, notificaciones de citas | Completado |
| Sprint 5 | Cola en tiempo real, historia clínica, recetas digitales y recordatorios | Completado |
| Sprint 6 | Refactor a CustomUser y solo FBVs, y despliegue en producción (PostgreSQL/Neon) | Completado |

**Avance actual: 100 %** — detalle en el [Product Backlog](docs/05-product-backlog.md).

## Equipo — TEAM DEVELOPERS ON PYTHON

| Rol | Integrante | GitHub |
|---|---|---|
| Scrum Master | Huaman Prejo, Saul | [@Sshdhjfhfh](https://github.com/Sshdhjfhfh) |
| Backend Dev | Aguilar Rivera, Elvis Antoni | [@EAAR23](https://github.com/EAAR23) |

Roles completos y evidencia: [docs/08-equipo-scrum.md](docs/08-equipo-scrum.md).

## Licencia

Este proyecto se distribuye bajo la licencia incluida en el archivo [LICENSE](LICENSE).