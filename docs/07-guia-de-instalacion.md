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
| `DB_ENGINE` | `sqlite` | `postgres` para usar PostgreSQL |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | vacíos | Credenciales de PostgreSQL (solo con `DB_ENGINE=postgres`) |
| `DJANGO_EMAIL_BACKEND`, `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD` | consola | Configuración SMTP de notificaciones |

## 5. Pruebas

```bash
python -m pytest          # ejecuta las 83 pruebas
python -m pytest -v       # modo detallado
python manage.py check    # verifica la configuración
```

## 6. Recordatorios de citas

El comando `recordar_citas` envía un correo de recordatorio a los estudiantes
con cita programada para la próxima mañana (24 horas antes):

```bash
python manage.py recordar_citas                 # envía los recordatorios
python manage.py recordar_citas --dry-run       # solo simula (no envía)
python manage.py recordar_citas --horas 48      # anticipación de 48 horas
```

Programarlo en Windows (Programador de tareas) o con cron en Linux:

```bash
# Cron: cada día a las 08:00
0 8 * * * cd /ruta/al/proyecto && venv/bin/python manage.py recordar_citas
```

## 7. Solución de problemas

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'rest_framework'` | Activar el entorno virtual (`.\venv\Scripts\Activate.ps1`) y ejecutar `pip install -r requirements.txt`. |
| La consola muestra caracteres como `?` al correr comandos | Es solo la codificación de la consola; los archivos están en UTF-8. Ejecutar `chcp 65001` para mostrar correctamente. |
| `migrate` falla con la base de datos | Eliminar `db.sqlite3` (solo desarrollo) y ejecutar `python manage.py migrate` y `python manage.py seed_demo`. |
| Puertos ocupados | Usar otro puerto: `python manage.py runserver 127.0.0.1:8001`. |
| No se ven los estilos/logos | Ejecutar `python manage.py collectstatic` y verificar que `static/` contenga `css/estilos.css` e `img/unh-logo.png`. |

## 8. Despliegue (planificado, Sprint 6)

La migración a PostgreSQL se hará configurando `DATABASES` en `settings.py` vía
variables de entorno (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`),
desactivando `DEBUG`, definiendo `DJANGO_ALLOWED_HOSTS` y sirviendo los
estáticos con `collectstatic`.

### 8.1 Despliegue en Vercel

Vercel ejecuta el proyecto en funciones serverless, por lo que **no funciona
con SQLite** (el disco es efímero). Requiere PostgreSQL.

1. **Crear una base de datos gratuita** en [Neon](https://neon.tech) o
   [Supabase](https://supabase.com). Copiar los datos de conexión
   (`host`, `dbname`, `user`, `password`, `port`).
2. **Configurar el proyecto en Vercel** conectándolo a este repositorio
   de GitHub (Vercel detecta `vercel.json`).
3. **Definir variables de entorno** en Vercel (Project Settings → Environment
   Variables):
   - `DB_ENGINE=postgres`
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
   - `DJANGO_SECRET_KEY` (una clave aleatoria segura)
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=<tu-dominio>.vercel.app`
   - `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` y las
     credenciales SMTP reales si se quiere correo de notificaciones.
4. **Primer despliegue**: las migraciones se ejecutan automáticamente por el
   `buildCommand` de `vercel.json`. Después se recomienda cargar los datos de
   demostración una vez con un comando de consola (ver paso 5).
5. **(Opcional) Cargar datos demo** en producción: como Vercel no permite
   ejecutar comandos de gestión directamente, se puede crear un superusuario
   temporalmente con `python manage.py createsuperuser` local apuntando a la
   misma BD, o usar `python manage.py seed_demo` desde una copia del proyecto
   con las mismas variables de entorno.

> Nota: en Vercel el correo de consola no se muestra; para ver correos es
> obligatorio configurar un SMTP real.

### 8.2 Alternativa recomendada (VPS/Render)

Como Vercel es serverless y sin estado, para un sistema con sesiones y citas
se recomienda como alternativa **Render** o una **VPS** con PostgreSQL y
`gunicorn`, ejecutando migraciones y `recordar_citas` mediante un cron.
