# Proyecto Final Módulo 4 – Uber Ride Analytics: Análisis Operativo y Financiero de Reservas Uber

## Dashboard interactivo

**Aplicación desplegada en Streamlit:**

 **[https://proyectofinalmodulo4-scc.streamlit.app/](https://proyectofinalmodulo4-scc.streamlit.app/)**

---

## Resumen

Este proyecto desarrolla una solución completa de **Business Intelligence** para analizar el desempeño operativo y financiero de Uber durante 2024 mediante técnicas de modelado dimensional, procesos ETL, almacenamiento en AWS Aurora PostgreSQL, consultas SQL analíticas y visualización interactiva con Streamlit.

Se construyó un modelo OLAP tipo estrella a partir de un dataset de **150,000 reservas**, permitiendo analizar la relación entre:

* Cancelaciones de viajes.
* Tiempos de espera.
* Tipos de vehículo.
* Ingresos generados.
* Eficiencia operativa.

El resultado final es un dashboard interactivo que permite responder la pregunta analítica principal y generar hallazgos relevantes para la toma de decisiones.

---

# Pregunta analítica

## ¿Cómo impactan las cancelaciones, los tiempos de espera y el tipo de vehículo en el desempeño operativo y los ingresos de Uber durante 2024?

---

# Problema y motivación

Las plataformas de movilidad dependen de la capacidad de convertir solicitudes de viaje en viajes completados.

Sin embargo, factores como:

* Cancelaciones por parte del cliente.
* Cancelaciones por parte del conductor.
* Falta de conductores disponibles.
* Viajes incompletos.
* Tiempos excesivos de espera.

pueden afectar directamente:

* Los ingresos de la plataforma.
* La satisfacción de los usuarios.
* La eficiencia operativa.
* La utilización de los vehículos.

Este proyecto busca identificar qué factores operativos tienen mayor impacto sobre el desempeño financiero y operacional de Uber.

---

# Objetivos

## Objetivo general

Analizar el desempeño operativo y financiero de Uber durante 2024 mediante un modelo dimensional y un dashboard interactivo que permita evaluar el impacto de cancelaciones, tiempos de espera y tipos de vehículo.

## Objetivos específicos

* Analizar la distribución de estados de viaje.
* Evaluar los ingresos generados por tipo de vehículo.
* Identificar vehículos con mayor participación financiera.
* Analizar la evolución mensual de ingresos.
* Detectar rutas con mayor rentabilidad.
* Comparar tasas de finalización y fallas operativas.
* Evaluar el impacto de los tiempos de espera sobre las cancelaciones.
* Construir una solución OLAP para análisis multidimensional.

---

# Fuente de datos

### Dataset

**Uber Ride Analytics Dashboard Dataset**

Fuente:

📊 Kaggle

El conjunto de datos contiene información de viajes registrados durante 2024.

## Tamaño del dataset

| Métrica   |                       Valor |
| --------- | --------------------------: |
| Registros |                     150,000 |
| Variables |                          21 |
| Periodo   | Enero 2024 – Diciembre 2024 |

---

# Análisis exploratorio inicial

## Calidad de datos

### Registros

* 150,000 filas
* 21 columnas

### Periodo analizado

* Fecha mínima: 2024-01-01
* Fecha máxima: 2024-12-30

### Valores nulos

Los nulos identificados corresponden principalmente a registros cancelados o incompletos, por lo que representan comportamiento válido del negocio.

Ejemplos:

| Variable                    | % Nulos |
| --------------------------- | ------: |
| Incomplete Rides Reason     |     94% |
| Cancelled Rides by Customer |     93% |
| Driver Cancellation Reason  |     82% |
| Booking Value               |     32% |
| Ride Distance               |     32% |

### Distribución de estados

| Estado                | Reservas |
| --------------------- | -------: |
| Completed             |   93,000 |
| Cancelled by Driver   |   27,000 |
| No Driver Found       |   10,500 |
| Cancelled by Customer |   10,500 |
| Incomplete            |    9,000 |

### Duplicados

Se identificaron 1,233 Booking ID repetidos.

Después de la revisión se determinó que corresponden a registros independientes con atributos distintos, por lo que no fueron eliminados.

---

# 🏗️ Arquitectura End-to-End

```text
                    Uber Dataset (CSV)
                             │
                             ▼

                ETL Python (Pandas)
        ┌──────────────────────────────┐
        │ Extract                      │
        │ Transform                    │
        │ Load                         │
        └──────────────────────────────┘
                             │
                             ▼

                 AWS Aurora PostgreSQL
                    Schema: uber_dwh

        • dim_date
        • dim_customer
        • dim_vehicle
        • dim_location
        • dim_payment
        • dim_status
        • fact_bookings

                             │
                             ▼

                    SQL Analítico
               (CTEs + Aggregations)

                             │
                             ▼

                Exportación a CSV
             (independencia de AWS)

                             │
                             ▼

                  Dashboard Streamlit
```

---

#  Estructura del repositorio

```text
Proyecto_final_modulo_4/
│
├── README.md
│
├── notebooks/
│   └── proyecto_final.ipynb
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── dim_date.csv
│   ├── dim_customer.csv
│   ├── dim_vehicle.csv
│   ├── dim_location.csv
│   ├── dim_payment.csv
│   ├── dim_status.csv
│   └── fact_bookings.csv
|
├──ncr_ride_bookings.csv
```

---

#  Modelo dimensional

## Grano

Una fila de la tabla de hechos representa una reserva (booking) registrada en Uber durante 2024.

---

## Esquema estrella

```text
                 dim_date
                      │
                      │
                      ▼

 dim_customer ──► fact_bookings ◄── dim_vehicle
                      │
                      │
                      ▼

 dim_location ◄───────┼───────► dim_payment
                      │
                      ▼

                 dim_status
```

---

## Dimensiones

### dim_date

Información temporal del viaje.

* Fecha
* Día
* Mes
* Trimestre
* Año
* Día de semana

### dim_customer

Identificador único de cliente.

### dim_vehicle

Tipo de vehículo.

* Auto
* Bike
* Go Mini
* Go Sedan
* Premier Sedan
* Uber XL
* eBike

### dim_location

Ubicación de origen y destino.

### dim_payment

Método de pago.

### dim_status

Estado del viaje y motivos asociados.

---

## Tabla de hechos

### fact_bookings

Métricas principales:

* Booking Value
* Ride Distance
* Avg VTAT
* Avg CTAT
* Driver Rating
* Customer Rating
* Viajes completados
* Cancelaciones
* Viajes incompletos

---

# ⚙️ Proceso ETL

## Extract

Se realizó la lectura del archivo CSV utilizando Pandas.

```python
df = pd.read_csv("ncr_ride_bookings.csv")
```

---

## Transform

Transformaciones principales:

* Estandarización de nombres de columnas.
* Conversión de fechas.
* Limpieza de identificadores.
* Tratamiento de valores nulos.
* Construcción de dimensiones.
* Generación de surrogate keys.
* Construcción de la tabla de hechos.
* Validaciones de integridad.

### Validaciones realizadas

| Validación          | Resultado |
| ------------------- | --------- |
| Filas origen        | 150,000   |
| Filas fact_bookings | 150,000   |
| Llaves nulas        | 0         |
| Fechas inválidas    | 0         |

---

## Load

La carga se realizó en AWS Aurora PostgreSQL utilizando:

* SQLAlchemy
* Psycopg2
* Pandas to_sql()

Schema utilizado:

```sql
uber_dwh
```

---

# ☁️ Implementación en AWS

Motor:

**Amazon Aurora PostgreSQL**

Base de datos:

```sql
northwind
```

Schema:

```sql
uber_dwh
```

Tablas cargadas:

```sql
dim_date
dim_customer
dim_vehicle
dim_location
dim_payment
dim_status
fact_bookings
```

---

# 💻 Consultas SQL analíticas

Se desarrollaron siete consultas principales:

### 1. KPIs generales

Obtiene:

* Total bookings
* Revenue total
* Completion rate
* Failure rate

---

### 2. Distribución de estados de viaje

Analiza:

* Completed
* Cancelled by Driver
* Cancelled by Customer
* No Driver Found
* Incomplete

---

### 3. Ingresos por tipo de vehículo

Permite identificar la participación financiera de cada categoría.

---

### 4. Evolución mensual de ingresos

Analiza tendencias temporales utilizando agregaciones mensuales.

---

### 5. Top rutas más rentables

Identifica los corredores con mayor generación de ingresos.

---

### 6. Ranking operativo por tipo de vehículo

Compara:

* Completion Rate
* Failure Rate
* Revenue Share

---

### 7. Impacto de tiempos de espera, fallas e ingresos

Relaciona:

* Avg VTAT
* Avg CTAT
* Failure Rate
* Revenue

---

#  Dashboard interactivo

El dashboard fue desarrollado en Streamlit y utiliza archivos CSV exportados desde el modelo dimensional, permitiendo su ejecución sin depender de una conexión activa a AWS.

## Módulos principales

### 1. Desempeño general

* Total bookings
* Revenue
* Completion rate
* Failure rate

### 2. Distribución de estados

Análisis de resultados operativos.

### 3. Ingresos por tipo de vehículo

Comparación financiera.

### 4. Evolución mensual de ingresos

Análisis temporal.

### 5. Top rutas más rentables

Análisis geográfico.

### 6. Ranking operativo

Comparación de eficiencia operativa.

### 7. Impacto de tiempos de espera

Relación entre eficiencia y resultados financieros.

---

#  Hallazgos principales

## Hallazgo 1

Durante 2024 se registraron **150,000 reservas** que generaron ingresos por **$51.8 millones**.

---

## Hallazgo 2

El **62%** de las reservas culminó exitosamente, mientras que el **38%** terminó en cancelaciones, falta de conductor o viajes incompletos.

---

## Hallazgo 3

El estado **Completed** concentró **93,000 viajes**, siendo el resultado dominante dentro de la operación.

---

## Hallazgo 4

El vehículo **Auto** fue el principal generador de ingresos, aportando aproximadamente el **25% del revenue total**.

---

## Hallazgo 5

El mes con mayores ingresos fue **marzo**, mientras que **febrero** presentó el menor desempeño.

---

## Hallazgo 6

La ruta **New Delhi Railway Station → Rajouri Garden** fue la ruta más rentable del periodo analizado.

---

## Hallazgo 7

**Go Sedan** presentó la mayor tasa de fallas operativas.

---

## Hallazgo 8

**Uber XL** registró la mayor tasa de finalización de viajes.

---

## Hallazgo 9

Los vehículos con mayores ingresos no necesariamente presentan la mejor eficiencia operativa.

---

## Hallazgo 10

Los tiempos de espera y la disponibilidad de conductores tienen un impacto directo sobre la tasa de fallas y los ingresos generados.

---

#  Conclusiones

El desempeño de Uber durante 2024 no depende únicamente del volumen de reservas o de los ingresos generados, sino también de la eficiencia operativa con la que se atienden las solicitudes.

Los resultados muestran que:

* Las cancelaciones representan una fuente importante de pérdida operativa.
* Los tiempos de espera están asociados con mayores tasas de falla.
* Los vehículos con mayores ingresos no siempre son los más eficientes.
* La evaluación conjunta de ingresos, tiempos de espera y tasas de finalización proporciona una visión más completa del negocio.

Desde una perspectiva de Business Intelligence, el modelo dimensional construido permite analizar el negocio desde múltiples dimensiones y facilita la identificación de oportunidades de mejora operativa y financiera.


# 👨‍💻 Autor

**Sebastián Cruz Castro**

Proyecto Final — Módulo 4
Diplomado en Manejo de Datos SQL y NoSQL en Entornos Cloud AWS

---

## 🔗 Enlaces

**Repositorio GitHub**

[Proyecto Final Módulo 4](https://github.com/scruzcas/Proyecto_final_modulo_4?utm_source=chatgpt.com)

**Dashboard Streamlit**

[Uber Ride Analytics Dashboard](https://proyectofinalmodulo4-scc.streamlit.app/?utm_source=chatgpt.com)

Este formato está bastante alineado con una entrega de nivel alto porque cubre: problema, arquitectura, modelo dimensional, ETL, implementación cloud, SQL avanzado, dashboard, hallazgos y conclusiones; que son precisamente los elementos que suelen evaluar en la rúbrica del proyecto final.

