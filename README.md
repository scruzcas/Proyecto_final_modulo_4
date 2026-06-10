# Proyecto Final Módulo 4 – Uber Ride Analytics


## Descripción

Este proyecto tiene como objetivo desarrollar una solución completa de Business Intelligence utilizando datos de viajes de Uber durante 2024. Se aplicarán los conceptos vistos en el módulo, incluyendo modelado dimensional, implementación en AWS Aurora PostgreSQL, procesos ETL en Python, SQL avanzado y visualización de datos mediante un dashboard interactivo.

## Pregunta Analítica

**¿Cómo impactan las cancelaciones, los tiempos de espera y el tipo de vehículo en el desempeño operativo y los ingresos de Uber durante 2024?**

## Justificación

La eficiencia operativa es un factor clave para plataformas de movilidad como Uber. Las cancelaciones, los tiempos de llegada del conductor y las características del servicio pueden afectar tanto la experiencia del usuario como los ingresos generados por la plataforma.

A través del análisis de los viajes registrados durante 2024, este proyecto busca identificar patrones relacionados con:

* Cancelaciones por parte de clientes y conductores.
* Tiempos de atención y duración de viajes.
* Desempeño de los distintos tipos de vehículo.
* Impacto en ingresos y satisfacción del usuario.

Los resultados permitirán comprender qué factores operativos están asociados con un mejor desempeño del servicio.

---

## Dataset

**Fuente:** Uber Ride Analytics Dashboard (Kaggle)

El dataset contiene información de aproximadamente **150,000 viajes** y **21 variables**, incluyendo:

* Estado del viaje.
* Tipo de vehículo.
* Ubicación de origen y destino.
* Distancia recorrida.
* Ingresos por viaje.
* Tiempos de atención.
* Calificaciones de conductores y clientes.
* Métodos de pago.
* Cancelaciones y motivos de cancelación.

### Análisis Exploratorio Inicial

* Registros: 150,000
* Columnas: 21
* Periodo analizado: 2024
* Se identificaron valores nulos asociados al estado de los viajes (cancelados o incompletos), considerados válidos para el análisis.
* Se detectaron Booking ID repetidos; sin embargo, corresponden a registros distintos y no representan duplicados reales del dataset.

---

## Arquitectura del Proyecto

### Flujo End-to-End

```text
                   Uber Ride Dataset (CSV)
                   Kaggle - 150,000 registros
                              │
                              │
                              ▼

                  ETL Python - etl_pipeline.py

                  Extract  → Lectura del archivo CSV
                  Transform→ Limpieza de datos,
                              tratamiento de nulos,
                              generación de dimensiones,
                              creación de surrogate keys
                  Load     → Carga a AWS Aurora PostgreSQL

                              │
                              ▼

                    AWS Aurora PostgreSQL
                         Schema: uber_bi

                    • dim_date
                    • dim_vehicle
                    • dim_location
                    • dim_payment
                    • dim_status
                    • fact_rides

                              │
                              ▼

                     SQL Analítico Avanzado

                    • CTEs
                    • Window Functions
                    • Rankings
                    • Tendencias temporales

                              │
                              ▼

                     Dashboard Interactivo

                 • Ingresos
                 • Cancelaciones
                 • Tiempos de espera
                 • Tipo de vehículo
```

---

## Modelo Dimensional

### Grano

Una fila de la tabla de hechos representa un viaje (booking) registrado en la plataforma Uber durante 2024.

### Esquema Estrella

```text
                         dim_date
                    ┌───────────────┐
                    │  date_key PK  │
                    │  full_date    │
                    │  year         │
                    │  quarter      │
                    │  month        │
                    │  month_name   │
                    │  day          │
                    │  day_name     │
                    │  is_weekend   │
                    │  hour         │
                    └───────────────┘
                            ▲
                            │
                            │
┌────────────────┐     ┌────┴─────────────────────┐     ┌────────────────┐
│  dim_vehicle   │────►│       fact_rides         │◄────│  dim_payment   │
│                │     │                          │     │                │
│ vehicle_key PK │     │ ride_key PK             │     │ payment_key PK │
│ vehicle_type   │     │ date_key FK             │     │ payment_method │
└────────────────┘     │ vehicle_key FK          │     └────────────────┘
                       │ pickup_location_key FK  │
                       │ drop_location_key FK    │
                       │ payment_key FK          │
                       │ status_key FK           │
                       │                          │
                       │ booking_id              │
                       │ customer_id             │
                       │ booking_value           │
                       │ ride_distance           │
                       │ avg_vtat                │
                       │ avg_ctat                │
                       │ driver_rating           │
                       │ customer_rating         │
                       │ cancelled_customer      │
                       │ cancelled_driver        │
                       │ incomplete_ride         │
                       └──────────┬──────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                                   │
                ▼                                   ▼

      ┌──────────────────┐               ┌──────────────────┐
      │  dim_location    │               │   dim_status     │
      │                  │               │                  │
      │ location_key PK  │               │ status_key PK   │
      │ location_name    │               │ booking_status  │
      └──────────────────┘               └──────────────────┘

         (usada como Pickup y Drop)
```

### Dimensiones

* **Dim_Date:** Información temporal del viaje.
* **Dim_Vehicle:** Tipo de vehículo utilizado.
* **Dim_Location:** Ubicación de origen y destino.
* **Dim_Payment:** Método de pago utilizado.
* **Dim_Status:** Estado final del viaje.

### Tabla de Hechos

**Fact_Rides**

Contiene las métricas principales del negocio:

* Booking Value
* Ride Distance
* Avg VTAT
* Avg CTAT
* Driver Rating
* Customer Rating
* Indicadores de cancelación
* Indicadores de viajes incompletos

---

## Tecnologías

* AWS Aurora PostgreSQL
* Python
* Pandas
* SQLAlchemy
* PostgreSQL
* SQL Avanzado
* GitHub
* Streamlit

---

## Estado Actual del Proyecto

### Completado

* Definición de la pregunta analítica.
* Exploración y validación del dataset.
* Diseño del modelo dimensional.
* Diseño de la arquitectura general de la solución.

### En desarrollo

* Implementación del esquema en AWS Aurora PostgreSQL.
* Desarrollo del proceso ETL.
* Construcción de consultas analíticas con SQL avanzado.
* Desarrollo del dashboard interactivo.

---

## Próximos Pasos

1. Crear el esquema dimensional en AWS Aurora PostgreSQL.
2. Desarrollar el pipeline ETL completo.
3. Implementar consultas analíticas utilizando SQL avanzado.
4. Construir el dashboard interactivo.
5. Documentar hallazgos y conclusiones finales.

---

## Repositorio

Proyecto académico desarrollado como entrega final del Módulo 4, aplicando técnicas de Business Intelligence, modelado dimensional, ETL, SQL avanzado y visualización de datos sobre un caso de análisis de operaciones de Uber.

