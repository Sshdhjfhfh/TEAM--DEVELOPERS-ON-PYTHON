# 09 — Retrospectiva

Retrospectiva del Proyecto Integrador de Programación Web II — TEAM
DEVELOPERS ON PYTHON. Resume qué funcionó bien por sprint y qué se mejoraría
en una versión 2 (v2), tal como se expone en el minuto final de la presentación.

## 1. Qué funcionó bien

### Sprint 1 — Módulo base
- Definir el dominio del Tópico UNH y el modelo de datos temprano permitió
  avanzar sin rehacer migraciones en los sprints siguientes.
- El CRUD de pacientes con DNI validado quedó listo y reutilizable para los
  demás módulos.

### Sprint 2 — Relación y Bootstrap
- Aplicar `unique_together` en `RecetaMedicamento` desde el inicio evitó
  datos duplicados en las recetas.
- Adoptar Bootstrap 5 desde este sprint dio consistencia visual a toda la
  interfaz (navbar, badges de estado, tablas).

### Sprint 3 — Sistema completo
- La gestión de usuarios con `create_user()` y el filtro por rol se integraron
  de forma natural con `CustomUser.ROL_CHOICES`.
- El uso exclusivo de **vistas basadas en funciones (FBV)** y **HTML manual**
  (sin Django Forms ni DRF) mantuvo el código sencillo y alineado a las
  restricciones del docente.
- Las 82 pruebas automatizadas dieron confianza para refactorizar y desplegar.

### General
- El CI en GitHub Actions (`manage.py check` + pytest en Python 3.12 y 3.13)
  detectó errores antes de cada entrega.
- Git Flow con ramas `feature/*` → `develop` → `main` mantuvo `main` estable.
- Desplegar en Vercel + Neon PostgreSQL validó el sistema en un entorno real.

## 2. Qué mejoraríamos en una v2

| Área | Mejora propuesta |
|---|---|
| Frontend | Reemplazar los gráficos por CDN por una librería instalable y agregar AJAX para la cola en tiempo real (actualmente requiere refrescar la página). |
| Seguridad | Agregar autenticación por correo (2FA) y políticas de contraseñas más estrictas. |
| Datos | Cargar un padrón real de estudiantes desde Excel/CSV en lugar del comando `seed_demo`. |
| Proceso | Documentar cada historia de usuario con capturas desde el sprint en curso (no al final). |
| Producto | Añadir la historia clínica electrónica completa y la derivación formal a centros externos con seguimiento. |
| DevOps | Migrar a un servidor con estado (VPS/Render) para tareas en segundo plano como los recordatorios de citas sin depender de cron externo. |

## 3. Lecciones aprendidas

1. Validar los requisitos del docente (prohibiciones de CBV, Django Forms y
   DRF) al inicio evitó retrabajo: el refactor del Sprint 6 fue el cambio más
   costoso del proyecto.
2. Las pruebas automatizadas aceleran el desarrollo: permitieron eliminar
   Django Forms y DRF sin romper funcionalidad.
3. El `unique_together` y el retiro lógico son decisiones de modelo de datos
   que deben tomarse antes de crear registros de prueba.