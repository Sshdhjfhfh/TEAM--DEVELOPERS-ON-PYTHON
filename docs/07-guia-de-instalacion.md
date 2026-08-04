# 07 — Guía de instalación

Guía detallada para instalar y ejecutar el Sistema de Gestión del Tópico UNH
en un entorno de desarrollo.

## 1. Requisitos

- Python 3.12 o 3.13 (proyecto probado con 3.13.2).
- Git.
- Conexión a internet (para descargar dependencias y los estilos por CDN).

## 2. Instalación

### Windows (PowerShell)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON.git
cd TEAM--DEVELOPERS-ON-PYTHON

# 2. Crear y activar el entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. (Opcional) Cargar datos de demostración
python manage.py seed_demo

# 6. Iniciar el servidor
python manage.py runserver
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/`.

## 3. Usuarios de demostración

Después de `python manage.py seed_demo`:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador (acceso a `/admin/`) |
| `medico` | `medico123` | Médico |
| `enfermera` | `enfermera123` | Enfermero/a |
| `farmacia` | `farmacia123` | Farmacéutico/a |
| `estudiante` | `estudiante123` | Estudiante (portal) |

Además se carga un padrón de 6 estudiantes. El estudiante con código
`2021141002` (Luis García Poma) no tiene cuenta, por lo que permite probar el
flujo completo de registro en el portal.

> Estas credenciales son solo para desarrollo. Nunca usarlas en producción.

## 4. Variables de entorno (opcional)

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | (clave de desarrollo) | Clave secreta de Django |
| `DJANGO_DEBUG` | `True` | Modo depuración |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Hosts permitidos, separados por coma |

## 5. Pruebas

```bash
python -m pytest          # ejecuta las 58 pruebas
python -m pytest -v       # modo detallado
python manage.py check    # verifica la configuración
```

## 6. Solución de problemas

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'rest_framework'` | Activar el entorno virtual (`.\venv\Scripts\Activate.ps1`) y ejecutar `pip install -r requirements.txt`. |
| La consola muestra caracteres como `?` al correr comandos | Es solo la codificación de la consola; los archivos están en UTF-8. Ejecutar `chcp 65001` para mostrar correctamente. |
| `migrate` falla con la base de datos | Eliminar `db.sqlite3` (solo desarrollo) y ejecutar `python manage.py migrate` y `python manage.py seed_demo`. |
| Puertos ocupados | Usar otro puerto: `python manage.py runserver 127.0.0.1:8001`. |
| No se ven los estilos/logos | Ejecutar `python manage.py collectstatic` y verificar que `static/` contenga `css/estilos.css` e `img/unh-logo.png`. |

## 7. Despliegue (planificado, Sprint 5)

La migración a PostgreSQL se hará configurando `DATABASES` en `settings.py` vía
variables de entorno (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`),
desactivando `DEBUG`, definiendo `DJANGO_ALLOWED_HOSTS` y sirviendo los
estáticos con `collectstatic`.
