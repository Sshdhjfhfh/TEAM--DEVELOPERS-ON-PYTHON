# 04 — Reportes y exportaciones

Referencia del módulo de reportes del Sistema de Gestión del Tópico UNH.
Este documento sustituye la antigua referencia de API REST (eliminada, dado
que el proyecto usa solo vistas basadas en funciones y no expone endpoints JSON).

## 1. Acceso

- **Dashboard** (`/reportes/`): indicadores resumidos por periodo.
- **Reportes** (`/reportes/atenciones/`, `/reportes/pacientes/`,
  `/reportes/inventario/`): listados filtrables.

Todos los reportes requieren autenticación y están protegidos por
`@login_required`. El acceso al dashboard está restringido al personal de
salud (no estudiantes).

## 2. Filtro por periodo

Los reportes se filtran con `GET ?periodo=...`:

| Valor | Rango |
|---|---|
| `hoy` | Desde las 00:00 del día actual |
| `7dias` (defecto) | Últimos 7 días |
| `30dias` | Últimos 30 días |

Ejemplo:

```
GET /reportes/atenciones/?periodo=30dias
```

## 3. Reporte de atenciones

- Listado de atenciones del periodo con su estado y nivel de triage.
- Resumen por nivel de triage y por estado (conteo y porcentaje).

### 3.1 Imprimir / PDF

```
GET /reportes/atenciones/?periodo=7dias&imprimir=1
```

Devuelve la misma información en una vista de impresión con membrete UNH;
el navegador permite *Guardar como PDF*.

### 3.2 Exportar CSV

```
GET /reportes/atenciones/?periodo=7dias&csv=1
```

Descarga un archivo `.csv` con codificación UTF-8 (compatible con Excel) con
las columnas: fecha, paciente, DNI, triage, estado, médico.

## 4. Reporte de pacientes

- Listado de pacientes registrados en el periodo (fecha de registro).
- Exportación CSV con DNI, nombres, sexo, tipo de sangre y alergias.

## 5. Reporte de inventario

- **Valorización**: stock valorizado = Σ (stock_actual × precio_unitario).
- Listado de medicamentos con stock actual, mínimo, estado crítico y valorización.
- Exportación CSV con nombre, categoría, unidad, stock, precio y valorización.

## 6. Dashboard

Muestra indicadores del periodo seleccionado (`hoy`, `7dias`, `30dias`):

- Total de atenciones, pacientes atendidos y citas.
- Distribución por nivel de triage (gráfico).
- Atenciones por estado y por médico.
- Alertas de stock crítico.
- Valorización del inventario.

Los gráficos se renderizan con Chart.js (CDN).

## 7. Pruebas

La cobertura incluye: respuesta de cada reporte por periodo, filtros, vistas
imprimibles y exportaciones CSV con el contenido esperado.