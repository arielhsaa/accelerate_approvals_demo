# 💳 Payment Authorization Demo App

## Overview

**Versión:** 1.0.0 (Demo)  
**Tipo:** Aplicación básica para demostraciones rápidas  
**Uso:** Presentaciones rápidas, monitoreo básico, prototipos

## Características

### ✅ Incluye:
- **Dashboard básico** con KPIs principales
- **Monitoreo en tiempo real** de transacciones
- **Visualización geográfica** simple
- **Análisis de códigos de declinación**
- **Interfaz simple** y fácil de usar

### ❌ No incluye:
- Genie AI
- Smart Retry avanzado
- Navegación multi-página
- Visualizaciones avanzadas
- Geo-analytics con PyDeck

## Estructura de Archivos

```
demo_app/
├── app.py              # Aplicación principal (renombrado de 06_app_demo_ui.py)
├── app.yaml            # Configuración de Databricks App
├── requirements.txt    # Dependencias mínimas
└── README.md           # Este archivo
```

## Recursos Requeridos

- **Memoria:** 2-4 Gi
- **CPU:** 1-2 cores
- **Dependencias:** Mínimas (9 paquetes)

## Despliegue

```bash
# 1. Preparar directorio de despliegue
mkdir -p /tmp/payment-demo-app
cp app.py /tmp/payment-demo-app/
cp app.yaml /tmp/payment-demo-app/
cp requirements.txt /tmp/payment-demo-app/

# 2. Subir a Databricks workspace
databricks workspace import-dir /tmp/payment-demo-app \
  /Workspace/Users/<your-email>/payment-authorization-demo --overwrite

# 3. Desplegar app
databricks apps deploy payment-authorization-demo \
  --source-code-path /Workspace/Users/<your-email>/payment-authorization-demo
```

## Configuración

- **Puerto:** 8501
- **Refresh Interval:** 120 segundos (2 minutos)
- **Cache TTL:** 600 segundos (10 minutos)
- **Genie AI:** Deshabilitado
- **Smart Retry:** Deshabilitado

## Casos de Uso

- ✅ Demostraciones rápidas a stakeholders
- ✅ Prototipos y pruebas de concepto
- ✅ Monitoreo básico de operaciones
- ✅ Entrenamiento de nuevos usuarios
- ✅ Presentaciones ejecutivas simples

## Comparación con Otras Versiones

| Característica | Demo | Advanced | Premium |
|---------------|------|----------|---------|
| Páginas | 1 | 7 | 8 |
| Genie AI | ❌ | ✅ | ✅ |
| Geo-analytics | Básico | Intermedio | Avanzado |
| PyDeck Maps | ❌ | ❌ | ✅ |
| Choropleth | ❌ | ❌ | ✅ |
| Recursos | Bajo | Medio | Alto |
| Dependencias | 9 | 20+ | 25+ |

## Soporte

Para más información, consulta:
- `../advanced_app/README.md` - Versión intermedia
- `../premium_app/README.md` - Versión enterprise
- `/DEPLOYMENT_STRUCTURE.md` - Guía de despliegue general
