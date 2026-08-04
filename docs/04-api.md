# 04 — API REST

Referencia de la API REST del Sistema de Gestión del Tópico UNH, construida
con Django REST Framework.

## 1. Autenticación

Todos los endpoints requieren autenticación mediante token o sesión.

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/token/` | Obtener token enviando `username` y `password` |

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
     -d "username=admin&password=admin123"
```

Respuesta:

```json
{ "token": "<TOKEN>" }
```

Usar el token en cada petición:

```bash
curl http://127.0.0.1:8000/api/pacientes/ \
     -H "Authorization: Token <TOKEN>"
```

## 2. Parámetros comunes

- Paginación: `?page=N` (20 elementos por página, `count` y `next` en la respuesta).
- Búsqueda: `?search=texto` (campos indicados por recurso).
- Ordenamiento: `?ordering=campo` o `?ordering=-campo`.
- Algunos recursos agregan filtros específicos (`?estado=`, `?triage=`, `?criticos=true`).

## 3. Recursos

| Recurso | Endpoint | Métodos | Notas |
|---|---|---|---|
| Pacientes | `/api/pacientes/` | GET, POST, PUT, PATCH, DELETE | Búsqueda por DNI, nombres, apellidos, teléfono |
| Atenciones | `/api/atenciones/` | GET, POST, PUT, PATCH, DELETE | Filtros `?estado=` y `?triage=`; incluye `signos_vitales` |
| Signos vitales | `/api/signos-vitales/` | GET, POST, PUT, PATCH, DELETE | Uno por atención |
| Medicamentos | `/api/medicamentos/` | GET, POST, PUT, PATCH, DELETE | Filtro `?criticos=true` |
| Movimientos | `/api/movimientos/` | GET, POST, PUT, PATCH, DELETE | `usuario` se asigna del token |
| Usuarios | `/api/usuarios/` | GET | Solo lectura; incluye `profile` |
| Perfiles | `/api/perfiles/` | GET | Solo lectura; filtro `?role=` |
| Estudiantes | `/api/estudiantes/` | GET | Padrón (solo lectura) |
| Citas | `/api/citas/` | GET, POST | Filtro `?estado=`; la reserva exige un estudiante autenticado |

## 4. Ejemplos

### Listar atenciones en espera

```bash
curl http://127.0.0.1:8000/api/atenciones/?estado=EN_ESPERA \
     -H "Authorization: Token <TOKEN>"
```

### Crear paciente

```bash
curl -X POST http://127.0.0.1:8000/api/pacientes/ \
     -H "Authorization: Token <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "nombres": "Ana",
       "apellidos": "Quispe",
       "dni": "12345678",
       "fecha_nacimiento": "2001-03-12",
       "sexo": "F",
       "telefono": "999111222",
       "tipo_sangre": "O+",
       "alergias": "Penicilina"
     }'
```

### Listar estudiantes del padrón de la escuela de Sistemas

```bash
curl "http://127.0.0.1:8000/api/estudiantes/?search=Sistemas" \
     -H "Authorization: Token <TOKEN>"
```

### Reservar una cita desde la API

Solo un usuario autenticado vinculado al padrón (`Profile.role = ESTUDIANTE`
y `Estudiante.user` asignado) puede crear citas; el campo `estudiante` se
asigna automáticamente.

```bash
curl -X POST http://127.0.0.1:8000/api/citas/ \
     -H "Authorization: Token <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "fecha": "2026-08-10",
       "hora": "09:00",
       "motivo": "Control de presión arterial"
     }'
```

## 5. Códigos de error

| Código | Significado |
|---|---|
| 401 | Falta o no es válido el token |
| 403 | Permisos insuficientes |
| 400 | Datos inválidos (los errores se detallan en `errors`) |
| 404 | Recurso no encontrado |
| 429 | Demasiadas peticiones |

## 6. Pruebas de API

La API está cubierta por pruebas automatizadas (`api/tests.py`): obtención de
token, permisos de autenticación, CRUD de pacientes/atenciones/medicamentos,
filtros por estado/triage y búsqueda.
