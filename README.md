# Proyecto Final Módulo 4 – Uber Ride Analytics

## Descripción

Este proyecto tiene como objetivo desarrollar una solución completa de Business Intelligence utilizando datos de viajes de Uber durante 2024. Se aplicarán los conceptos vistos en el módulo, incluyendo modelado dimensional, implementación en AWS Aurora PostgreSQL, procesos ETL en Python, SQL avanzado y visualización de datos mediante un dashboard interactivo.

## Pregunta Analítica

**¿Cómo impactan las cancelaciones, los tiempos de espera y el tipo de vehículo en el desempeño operativo y los ingresos de Uber durante 2024?**

## Dataset

Fuente: Uber Ride Analytics Dashboard (Kaggle)

El dataset contiene información de aproximadamente 150,000 viajes e incluye variables relacionadas con:

* Estado del viaje
* Tipo de vehículo
* Ubicación de origen y destino
* Tiempos de atención y duración
* Ingresos del viaje
* Distancia recorrida
* Calificaciones de conductores y clientes
* Métodos de pago
* Cancelaciones y sus motivos

## Avance Actual

### Análisis Exploratorio

* Dataset analizado y validado.
* 150,000 registros y 21 columnas.
* Revisión de valores nulos y registros duplicados.
* Identificación de métricas y dimensiones principales.

### Modelo Dimensional

Grano definido:

> Una fila de la tabla de hechos representa un viaje registrado en la plataforma Uber.

Esquema estrella propuesto:

* Fact_Rides
* Dim_Date
* Dim_Vehicle
* Dim_Location
* Dim_Payment
* Dim_Status

## Tecnologías

* AWS Aurora PostgreSQL
* Python
* Pandas
* SQLAlchemy
* PostgreSQL
* SQL Avanzado
* GitHub
* Streamlit (dashboard)

## Próximos Pasos

1. Implementación del modelo dimensional en AWS Aurora.
2. Desarrollo del proceso ETL.
3. Construcción de consultas analíticas con SQL avanzado.
4. Desarrollo del dashboard interactivo.
5. Elaboración de documentación final y análisis de hallazgos.
