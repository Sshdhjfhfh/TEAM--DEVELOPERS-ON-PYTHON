"""Punto de entrada WSGI para Vercel.

La carpeta `api/` es el directorio que Vercel usa para las funciones
serverless de Python. Aquí se expone la aplicación Django como `app`.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topico_project.settings')

app = get_wsgi_application()