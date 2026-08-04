# 05 — Product Backlog

El proyecto se desarrolla con **Scrum** (sprints de 2 semanas) y **Git Flow**
(`main` estable, `develop` de integración y ramas `feature/*`).

## 1. Épicas

1. **EP-1 Gestión de cuentas y roles**: autenticación, perfiles con rol y
   registro de personal.
2. **EP-2 Gestión clínica**: pacientes, atenciones con triage, signos vitales
   y cola priorizada.
3. **EP-3 Gestión de almacén**: medicamentos e insumos, movimientos de stock y
   alertas.
4. **EP-4 Reportes y decisiones**: dashboard e indicadores por periodo.
5. **EP-5 Portal de estudiantes**: padrón, registro validado y reserva de citas.
6. **EP-6 Integración**: API REST, exportaciones y despliegue.

## 2. Historias de usuario

| ID | Historia | Épica | Prioridad | Estado |
|---|---|---|---|---|
| HU-01 | Como personal del Tópico quiero iniciar sesión con mi usuario para usar el sistema. | EP-1 | Alta | Hecho |
| HU-02 | Como administrador quiero asignar roles para controlar los accesos. | EP-1 | Alta | Hecho |
| HU-03 | Como enfermero/a quiero registrar pacientes validando el DNI para evitar duplicados. | EP-2 | Alta | Hecho |
| HU-04 | Como enfermero/a quiero clasificar cada atención con triage para priorizar emergencias. | EP-2 | Alta | Hecho |
| HU-05 | Como personal quiero registrar los signos vitales de cada atención. | EP-2 | Alta | Hecho |
| HU-06 | Como médico quiero ver la cola de triage ordenada por gravedad. | EP-2 | Alta | Hecho |
| HU-07 | Como farmacéutico quiero registrar entradas y salidas de medicamentos con stock automático. | EP-3 | Alta | Hecho |
| HU-08 | Como farmacéutico quiero ver alertas de stock crítico para reponer el almacén. | EP-3 | Media | Hecho |
| HU-09 | Como jefatura quiero un dashboard con indicadores del Tópico. | EP-4 | Media | Hecho |
| HU-10 | Como jefatura quiero reportes por periodo de atenciones, pacientes e inventario. | EP-4 | Media | Hecho |
| HU-11 | Como estudiante UNH quiero registrarme en el portal validando mi código y DNI. | EP-5 | Alta | Hecho |
| HU-12 | Como estudiante quiero ver mi escuela y ciclo autocompletados desde el padrón. | EP-5 | Alta | Hecho |
| HU-13 | Como estudiante quiero reservar una cita eligiendo fecha y hora disponibles. | EP-5 | Alta | Hecho |
| HU-14 | Como estudiante quiero cancelar mi cita vigente si no puedo asistir. | EP-5 | Alta | Hecho |
| HU-15 | Como personal quiero ver la agenda de citas y convertirlas en atenciones. | EP-5 | Alta | Hecho |
| HU-16 | Como desarrollador quiero una API REST autenticada para integrar sistemas. | EP-6 | Media | Hecho |
| HU-17 | Como jefatura quiero exportar reportes a PDF/Excel. | EP-6 | Media | Pendiente |
| HU-18 | Como administrador quiero permisos granulares por rol en cada vista. | EP-6 | Media | Pendiente |
| HU-19 | Como personal quiero derivar formalmente pacientes a centros externos. | EP-6 | Media | Pendiente |
| HU-20 | Como administrador quiero desplegar el sistema en producción con PostgreSQL. | EP-6 | Alta | Pendiente |
| HU-21 | Como estudiante quiero recibir notificaciones sobre mi cita. | EP-5 | Baja | Pendiente |

## 3. Plan de sprints

| Sprint | Objetivo | Historias | Estado | Avance |
|---|---|---|---|---|
| Sprint 0 | Entorno, repositorio, Git Flow, wireframes y backlog | — | Completado | 100 % |
| Sprint 1 | Cuentas y roles, pacientes y atenciones con triage | HU-01 a HU-06 | Completado | 100 % |
| Sprint 2 | Inventario, reportes, API REST y CI | HU-07 a HU-10, HU-16 | Completado | 100 % |
| Sprint 3 | Portal de estudiantes (padrón, registro, citas) | HU-11 a HU-15 | Completado | 100 % |
| Sprint 4 | Exportaciones, permisos por rol y derivaciones | HU-17 a HU-19 | En curso | ~30 % |
| Sprint 5 | Despliegue en producción y notificaciones | HU-20, HU-21 | Pendiente | 0 % |

## 4. Avance global

**Avance estimado: ~70 %**

| Componente | Estado |
|---|---|
| Backend (modelos, reglas de negocio) | Completado |
| Vistas web y plantillas | Completado |
| Portal de estudiantes | Completado |
| API REST | Completado |
| Pruebas automatizadas (58) | Completado |
| Documentación | Completado |
| Exportaciones / permisos / derivaciones | Pendiente |
| Producción (PostgreSQL) | Pendiente |

## 5. Definición de hecho (DoD)

- Código en `develop`, rama `feature/*` fusionada.
- `manage.py check` sin errores y migraciones al día.
- Pruebas unitarias de la funcionalidad incluidas y pasando.
- Interfaz sin emojis y con estilos del Tópico UNH.
- Documentación actualizada en `docs/`.
