# 06 — Manual de usuario

Guía de uso del Sistema de Gestión del Tópico UNH, pantalla por pantalla.

## 1. Acceso

1. Abrir el navegador en `http://127.0.0.1:8000/`.
2. Iniciar sesión con el usuario del personal (`admin` / `medico` / `enfermera`
   / `farmacia`) o ingresar al portal de estudiantes desde `/portal/`.

El menú lateral cambia según el rol:

- **Personal de salud**: Dashboard, Pacientes, Atenciones, Cola de triage,
  Inventario, Reportes, API REST y Agenda de citas.
- **Estudiante**: Mi portal, Mis citas y Reservar cita.

## 2. Módulo de Pacientes

1. Ir a **Pacientes** en el menú.
2. Usar **Nuevo paciente** para registrar (DNI de 8 dígitos).
3. Buscar por DNI o nombre con el buscador.
4. En el detalle se muestra el historial de atenciones del paciente.

## 3. Módulo de Atenciones

1. Ir a **Atenciones** y usar **Nueva atención**.
2. Seleccionar el paciente, el nivel de triage (Rojo = emergencia, hasta
   Azul = no urgente) y el motivo de consulta.
3. Desde el detalle registrar los **signos vitales**.
4. La **Cola de triage** muestra las atenciones pendientes ordenadas por
   gravedad; al atender se cambia el estado.

## 4. Módulo de Inventario

1. Ir a **Inventario** para ver medicamentos e insumos.
2. Con **Registrar movimiento** se agrega una entrada, salida o ajuste.
3. Una salida mayor al stock disponible es rechazada.
4. Los ítems con stock crítico se resaltan en el listado y el dashboard.

## 5. Reportes

- El **Dashboard** resume indicadores del día/semana/mes con gráficos.
- **Reportes** ofrece vistas por pacientes, atenciones e inventario con
  filtros por periodo (`hoy`, `7 días`, `30 días`).
- Cada reporte tiene botones de **Exportar CSV** (abre en Excel) e
  **Imprimir / PDF** (vista imprimible para guardar como PDF).

### 5.1 Exportación CSV

1. Abrir el reporte deseado (pacientes, atenciones o inventario).
2. Pulsar **Exportar CSV**.
3. El navegador descarga un archivo `.csv` con codificación UTF-8 (compatible
   con Excel) listo para su análisis.

### 5.2 Impresión / PDF

1. Abrir el reporte y pulsar **Imprimir / PDF**.
2. Se abre una vista de impresión con membrete UNH.
3. Usar el botón **Imprimir** del navegador y elegir *Guardar como PDF*.

## 6. Portal de estudiantes

### 6.1 Registro (dos pasos)

1. Ingresar a `/portal/` (o `/portal/validar-codigo/`).
2. **Paso 1**: escribir el código de estudiante y el DNI. Deben coincidir con
   el padrón de matriculados; la matrícula debe estar activa y el código no
   debe tener cuenta previa.
3. **Paso 2**: se muestran los datos académicos autocompletados (escuela,
   ciclo). Completar fecha de nacimiento, sexo, teléfono y contraseña.
4. Al confirmar se crea la cuenta y se ingresa automáticamente al portal.

### 6.0 Roles y permisos

- Cada rol (Médico, Enfermero/a, Farmacéutico/a, Administrador, Estudiante)
  puede realizar acciones de escritura solo en los módulos que le
  corresponden: personal clínico para pacientes y atenciones, farmacéutico
  para inventario, personal para la agenda de citas.
- El estudiante solo accede a su portal de citas.
- Las acciones no permitidas ocultan sus botones en la interfaz y, si se
  intentan por URL, se redirige con un mensaje de error.

### 6.1 Notificaciones de cita

Al reservar, cancelar o atender una cita, se envía un correo al estudiante a
su dirección institucional (si el padrón la registra).

### 6.2 Mi portal

Muestra la información del estudiante (escuela, ciclo, código) y las próximas
citas vigentes.

### 6.3 Reservar cita

1. Ir a **Reservar cita**.
2. Elegir una fecha (lunes a viernes, hasta 30 días) y una hora de los slots
   disponibles (08:00–12:30 y 14:00–16:30).
3. Escribir el motivo y reservar. Solo se permite una cita activa a la vez.

### 6.4 Mis citas

- Se listan todas las citas con su estado.
- Una cita **Pendiente** o **Confirmada** puede cancelarse con el botón
  **Cancelar**.
- Si la cita fue atendida, se muestra un enlace a la atención generada.

## 7. Agenda de citas (personal de salud)

1. Ir a **Agenda de citas** en el menú.
2. Filtrar por estado, fecha o buscar por código/nombre del estudiante.
3. En una cita vigente pulsar **Atender**: se crea automáticamente una
   atención médica con la ficha del estudiante y la cita pasa a **Atendida**.

## 8. API REST

Consulte `docs/04-api.md` para la referencia de endpoints. Se puede explorar
la documentación interactiva en `http://127.0.0.1:8000/api/`.

## 9. Panel de administración

- Acceso en `/admin/` con el usuario `admin`.
- Gestiona usuarios, roles, pacientes, atenciones, inventario, el padrón de
  estudiantes (`Estudiante`) y las citas (`Cita`).
