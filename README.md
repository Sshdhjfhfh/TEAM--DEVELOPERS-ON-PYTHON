# Sistema de Gestión de Tópico UNH

[![CI](https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON/actions/workflows/ci.yml/badge.svg)](https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON/actions)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.17-A30000)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Tests](https://img.shields.io/badge/tests-83%20passed-brightgreen)
![Avance](https://img.shields.io/badge/avance-95%25-yellow)

Sistema web para la **gestión integral del Tópico de la Universidad Nacional
de Huancavelica (UNH)**: registro de pacientes, atenciones médicas con triage,
control de signos vitales, inventario de medicamentos e insumos, reportes
estadísticos, API REST y un **portal de estudiantes** para la reserva de citas.

---

## Tabla de contenido

- [Características](#características)
- [Stack tecnológico](#stack-tecnológico)
- [Instalación](#instalación)
- [Usuarios de demostración](#usuarios-de-demostración)
- [Estructura del proyecto](#estructura-del-proyecto)
- [API REST](#api-rest)
- [Pruebas](#pruebas)
- [Documentación](#documentación)
- [Metodología y avance](#metodología-y-avance)
- [Equipo](#equipo)

---

## Características

| Módulo | Funcionalidad |
|---|---|
| **Cuentas** | Login/registro, perfiles con roles (Médico, Enfermero/a, Farmacéutico/a, Administrador, Estudiante) |
| **Pacientes** | Registro con DNI validado, historial clínico, búsqueda por DNI/nombre, alergias y tipo de sangre |
| **Atenciones** | Registro de atención con triage de 5 niveles (Rojo a Azul), estados (en espera / en atención / atendido / derivado), signos vitales |
| **Cola de triage** | Cola priorizada en tiempo real: emergencias primero, ordenadas por hora de llegada |
| **Inventario** | Medicamentos, insumos y equipos; entradas/salidas/ajustes con actualización automática de stock y alertas de stock crítico |
| **Reportes** | Dashboard con indicadores y gráficos (Chart.js) por día, triage, estado y médico; valorización del inventario. Exportación a **CSV (Excel)** y vista **imprimible (PDF)** |
| **Portal de estudiantes** | Registro en dos pasos validado contra el padrón UNH, autocompletado de escuela y ciclo, y reserva de citas con horario del Tópico |
| **Cola en tiempo real** | El estudiante consulta su turno y posición en la cola del día, ordenada por triage |
| **Historia clínica** | El estudiante consulta sus atenciones, diagnósticos, tratamientos y recetas desde el portal |
| **Recetas digitales** | El personal receta medicamentos y el stock del inventario se descuenta automáticamente |
| **Recordatorios** | Comando `recordar_citas` que avisa por correo 24 h antes de cada cita |
| **Agenda de citas** | Gestión por el personal de salud y conversión de una cita en atención médica |
| **Permisos por rol** | Control de acceso granular por módulo (clínico, farmacia, agenda) con decoradores y ocultado de acciones en la interfaz |
| **Notificaciones** | Correo institucional al estudiante al reservar, cancelar o atender su cita |
| **API REST** | CRUD con autenticación por token, búsqueda, filtros, ordenamiento y paginación |

## Stack tecnológico

- **Backend:** Python 3.12+ · Django 5.1 · Django REST Framework 3.17
- **Frontend:** Django Templates · Bootstrap 5.3 · Bootstrap Icons · Chart.js
- **Base de datos:** SQLite (desarrollo) · PostgreSQL (producción/Vercel)
- **Pruebas:** pytest + pytest-django (83 pruebas)
- **CI/CD:** GitHub Actions

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
├── accounts/              # Usuarios, roles y autenticación (+ comando seed_demo)
├── pacientes/             # Gestión de pacientes
├── atenciones/            # Atenciones médicas, triage y signos vitales
├── inventario/            # Medicamentos y movimientos de stock
├── portal/                # Portal de estudiantes: padrón, registro y citas
├── reportes/              # Dashboard y reportes estadísticos
├── api_rest/              # API REST (serializers, viewsets, router)
├── templates/             # Plantillas (base + una carpeta por módulo)
├── static/                # CSS e imágenes institucionales (logo UNH)
├── api/                   # Punto de entrada WSGI para Vercel (serverless)
├── docs/                  # Documentación del proyecto
├── .github/workflows/     # CI con GitHub Actions
├── manage.py
├── pytest.ini
└── requirements.txt
```

## API REST

Todos los endpoints requieren autenticación (token o sesión). Base: `/api/`.

| Recurso | Endpoint | Métodos |
|---|---|---|
| Token | `POST /api/token/` | Obtener token con `username` y `password` |
| Pacientes | `/api/pacientes/` | GET, POST, PUT, PATCH, DELETE |
| Atenciones | `/api/atenciones/` | GET, POST, PUT, PATCH, DELETE (filtros `?estado=`, `?triage=`) |
| Signos vitales | `/api/signos-vitales/` | GET, POST, PUT, PATCH, DELETE |
| Medicamentos | `/api/medicamentos/` | GET, POST, ... (filtro `?criticos=true`) |
| Movimientos | `/api/movimientos/` | GET, POST (asigna el usuario autenticado) |
| Usuarios | `/api/usuarios/` | GET (solo lectura) |
| Estudiantes | `/api/estudiantes/` | GET (padrón, solo lectura) |
| Citas | `/api/citas/` | GET, POST (filtro `?estado=`; reserva desde cuenta de estudiante) |

Ejemplo:

```bash
# Obtener token
curl -X POST http://127.0.0.1:8000/api/token/ -d "username=admin&password=admin123"

# Listar pacientes
curl http://127.0.0.1:8000/api/pacientes/ -H "Authorization: Token <TOKEN>"
```

Referencia completa: [docs/04-api.md](docs/04-api.md)

## Pruebas

```bash
pytest            # ejecuta las 83 pruebas
pytest -v         # modo detallado
```

Cobertura: modelos (validaciones, propiedades, lógica de stock, slots de
citas), vistas web (autenticación, CRUD, registro de estudiantes, reserva y
cancelación de citas, conversión a atención, permisos por rol, exportaciones
CSV e imprimibles, notificaciones de cita) y API REST (token, permisos,
filtros).

## Documentación

| Documento | Contenido |
|---|---|
| [01 — Visión y alcance](docs/01-vision-y-alcance.md) | Problema, objetivos, alcance del producto |
| [02 — Arquitectura](docs/02-arquitectura.md) | Diseño del sistema, apps, decisiones técnicas |
| [03 — Modelo de datos](docs/03-modelo-de-datos.md) | Entidades, relaciones y diagrama ER |
| [04 — API REST](docs/04-api.md) | Referencia completa de endpoints |
| [05 — Product Backlog](docs/05-product-backlog.md) | User stories, sprints y avance (95 %) |
| [06 — Manual de usuario](docs/06-manual-de-usuario.md) | Guía de uso pantalla por pantalla |
| [07 — Guía de instalación](docs/07-guia-de-instalacion.md) | Instalación detallada y solución de problemas |

## Metodología y avance

El proyecto se desarrolla con **Scrum** y **Git Flow** (ramas `main`,
`develop` y `feature/*`).

| Sprint | Objetivo | Estado |
|---|---|---|
| Sprint 0 | Entorno, repositorio, backlog y wireframes | Completado |
| Sprint 1 | Autenticación, pacientes y atenciones con triage | Completado |
| Sprint 2 | Inventario, reportes, API REST y CI | Completado |
| Sprint 3 | Portal de estudiantes (padrón, registro y citas) | Completado |
| Sprint 4 | Exportación PDF/Excel, permisos por rol, notificaciones de citas | Completado |
| Sprint 5 | Cola en tiempo real, historia clínica, recetas digitales y recordatorios | Completado |
| Sprint 6 | Derivaciones formales y despliegue en producción (PostgreSQL) | Pendiente |

**Avance actual: ~95 %** — detalle en el [Product Backlog](docs/05-product-backlog.md).

## Equipo — TEAM DEVELOPERS ON PYTHON

| Rol | Integrante | GitHub |
|---|---|---|
| Scrum Master | Huaman Prejo, Saul | [@Sshdhjfhfh](https://github.com/Sshdhjfhfh) |
| Backend Dev | Aguilar Rivera, Elvis Antoni | [@EAAR23](https://github.com/EAAR23) |
| Product Owner | (por definir) | — |
| Frontend Dev | (por definir) | — |
| QA / DevOps | (por definir) | — |

## Licencia

Este proyecto se distribuye bajo la licencia incluida en el archivo [LICENSE](LICENSE).
