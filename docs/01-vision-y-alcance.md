# 01 — Visión y alcance

## 1. Contexto y problema

El Tópico de la Universidad Nacional de Huancavelica (UNH) brinda atención de
primeros auxilios y atención primaria a estudiantes, docentes y personal
administrativo. Actualmente los procesos se llevan de forma **manual**
(cuadernos de registro y hojas de cálculo), lo que genera:

- Pérdida y duplicidad de información de pacientes.
- Falta de priorización objetiva en la atención (no existe triage formal).
- Desabastecimiento de medicamentos por falta de control de stock.
- Imposibilidad de generar reportes e indicadores para la toma de decisiones.

## 2. Visión del producto

> **Para** el personal de salud del Tópico UNH **que** necesita registrar y
> priorizar atenciones de forma rápida y confiable, **el Sistema de Gestión
> de Tópico UNH** es una aplicación web **que** centraliza pacientes,
> atenciones con triage, inventario y reportes en tiempo real, **a diferencia
> del** registro manual en cuadernos, **nuestro producto** garantiza
> trazabilidad, priorización clínica y disponibilidad de la información.

## 3. Objetivos

### Objetivo general
Desarrollar un sistema web que digitalice y optimice la gestión integral del
Tópico UNH.

### Objetivos específicos
1. Registrar y consultar pacientes con validación de DNI e historial de atenciones.
2. Gestionar atenciones médicas con clasificación de triage de 5 niveles, registro
   de signos vitales y recetas médicas.
3. Controlar el inventario de medicamentos e insumos con alertas de stock crítico.
4. Generar reportes e indicadores (dashboard) con exportación CSV e imprimible.
5. Ofrecer un portal de estudiantes que valide la matrícula contra el padrón UNH y
   permita reservar citas de atención en línea.

## 4. Alcance

### Incluido (versión actual)
- Autenticación de usuarios con rol propio del dominio (Médico, Enfermero/a,
  Farmacéutico/a, Administrador, Estudiante), retiro lógico y CRUD de usuarios
  web por el administrador.
- CRUD de pacientes con búsqueda por DNI/nombre.
- Registro de atenciones con triage, estados, signos vitales y recetas médicas.
- Cola de triage priorizada en tiempo real.
- Inventario con entradas/salidas/ajustes y stock automático.
- Dashboard y reportes por periodo (hoy / 7 días / 30 días) con exportación CSV
  e imprimible (PDF).
- Portal de estudiantes: registro validado contra el padrón de matriculados,
  autocompletado de datos académicos y reserva de citas con horario del Tópico.
- Agenda de citas para el personal y conversión de una cita en atención médica.
- Notificaciones por correo y recordatorios automáticos de citas.
- Panel de administración de Django.

### Excluido (futuras versiones)
- Derivación formal a centros de salud externos (queda como estado de la
  atención: `DERIVADO`).
- Historia clínica electrónica completa (fuera de alcance del ciclo).

## 5. Usuarios / interesados

| Interesado | Interés |
|---|---|
| Estudiantes UNH | Registrarse en el portal, consultar su información académica y reservar citas |
| Personal de enfermería | Registrar pacientes, triage, signos vitales y atender citas |
| Médicos | Consultar historial, registrar diagnóstico y tratamiento |
| Farmacéutico | Controlar stock y movimientos de medicamentos |
| Jefatura del Tópico | Reportes e indicadores de gestión |

## 6. Restricciones y supuestos

- El sistema opera inicialmente en la red local del Tópico.
- La normativa de protección de datos personales (Ley N.º 29733 — Perú) exige
  restringir el acceso mediante autenticación.
- El equipo de desarrollo trabaja bajo Scrum con sprints de 2 semanas.
