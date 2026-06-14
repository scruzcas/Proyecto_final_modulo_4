# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path


st.set_page_config(
    page_title="Uber Ride Analytics 2024",
    page_icon="🚗",
    layout="wide"
)

DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_data():
    fact = pd.read_csv(DATA_DIR / "fact_bookings.csv")
    dim_date = pd.read_csv(DATA_DIR / "dim_date.csv")
    dim_vehicle = pd.read_csv(DATA_DIR / "dim_vehicle.csv")
    dim_location = pd.read_csv(DATA_DIR / "dim_location.csv")
    dim_payment = pd.read_csv(DATA_DIR / "dim_payment.csv")
    dim_status = pd.read_csv(DATA_DIR / "dim_status.csv")

    df = (
        fact
        .merge(dim_date, on="date_key", how="left")
        .merge(dim_vehicle, on="vehicle_key", how="left")
        .merge(dim_location, on="location_key", how="left")
        .merge(dim_payment, on="payment_key", how="left")
        .merge(dim_status, on="status_key", how="left")
    )

    date_col = None
    for col in ["fecha", "full_date", "date", "booking_date"]:
        if col in df.columns:
            date_col = col
            break

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["mes"] = df[date_col].dt.to_period("M").dt.to_timestamp()

    return df


df = load_data()


st.title("🚗 Uber Ride Analytics 2024")

st.markdown(
    """
## Objetivo del análisis

Este dashboard presenta un análisis OLAP del desempeño operativo y financiero de Uber durante 2024,
utilizando información exportada desde un Data Warehouse construido en AWS Aurora PostgreSQL.

### Pregunta analítica

**¿Cómo impactan las cancelaciones, los tiempos de espera y el tipo de vehículo en el desempeño operativo y los ingresos de Uber durante 2024?**

### Enfoque del análisis

El análisis se enfoca en identificar patrones relacionados con reservas completadas, cancelaciones,
fallas operativas, ingresos, tiempos de espera, rutas más rentables y desempeño por tipo de vehículo.

La versión publicada del dashboard funciona de forma **offline**, leyendo archivos CSV exportados desde
el modelo dimensional del Data Warehouse.
"""
)

st.divider()


st.sidebar.header("Filtros del dashboard")

vehicle_options = ["Todos"] + sorted(df["vehicle_type"].dropna().unique())
status_options = ["Todos"] + sorted(df["booking_status"].dropna().unique())

vehicle_filter = st.sidebar.selectbox(
    "Tipo de vehículo",
    options=vehicle_options
)

status_filter = st.sidebar.selectbox(
    "Estado del viaje",
    options=status_options
)

df_filtered = df.copy()

if vehicle_filter != "Todos":
    df_filtered = df_filtered[df_filtered["vehicle_type"] == vehicle_filter]

if status_filter != "Todos":
    df_filtered = df_filtered[df_filtered["booking_status"] == status_filter]


st.markdown("## Desempeño general")

total_bookings = len(df_filtered)
total_revenue = df_filtered["booking_value"].sum()
completed_bookings = df_filtered["is_completed"].sum()

failed_bookings = (
    df_filtered["is_cancelled_customer"].sum()
    + df_filtered["is_cancelled_driver"].sum()
    + df_filtered["is_no_driver_found"].sum()
    + df_filtered["is_incomplete"].sum()
)

completion_rate = completed_bookings / total_bookings if total_bookings else 0
failure_rate = failed_bookings / total_bookings if total_bookings else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total bookings", f"{total_bookings:,.0f}")
col2.metric("Total revenue", f"${total_revenue:,.0f}")
col3.metric("Completion rate", f"{completion_rate:.2%}")
col4.metric("Failure rate", f"{failure_rate:.2%}")

st.info(
    f"""
### Interpretación

Durante 2024 se registraron **{total_bookings:,.0f} reservas**, generando ingresos por
**${total_revenue:,.0f}**.

La tasa de finalización fue de **{completion_rate:.2%}**, lo que indica qué proporción de las reservas
culminaron exitosamente como viajes completados.

Por otro lado, la tasa de fallas fue de **{failure_rate:.2%}**, equivalente a
**{failed_bookings:,.0f} reservas** que no se completaron debido a cancelaciones del cliente,
cancelaciones del conductor, falta de conductor disponible o viajes incompletos.

Este resultado permite evaluar la eficiencia operativa general de la plataforma, ya que una proporción
alta de viajes no completados representa pérdida de oportunidades de ingreso.
"""
)

st.divider()


st.markdown("## Distribución de estados de viaje")

status_summary = (
    df_filtered
    .groupby("booking_status", as_index=False)
    .agg(total_bookings=("booking_id", "count"))
    .sort_values("total_bookings", ascending=False)
)

status_chart = (
    alt.Chart(status_summary)
    .mark_bar()
    .encode(
        x=alt.X("total_bookings:Q", title="Total bookings"),
        y=alt.Y("booking_status:N", sort="-x", title="Booking status"),
        tooltip=["booking_status", "total_bookings"]
    )
    .properties(height=350)
)

st.altair_chart(status_chart, use_container_width=True)

if not status_summary.empty:
    top_status = status_summary.iloc[0]
    st.info(
        f"""
### Interpretación

El estado de viaje más frecuente es **{top_status['booking_status']}**, con
**{top_status['total_bookings']:,.0f} reservas**.

Esta distribución permite identificar qué parte del volumen total corresponde a viajes completados
y qué proporción se concentra en cancelaciones, falta de conductor o viajes incompletos.
"""
    )

st.divider()


st.markdown("## Ingresos por tipo de vehículo")

vehicle_revenue = (
    df_filtered
    .groupby("vehicle_type", as_index=False)
    .agg(
        total_bookings=("booking_id", "count"),
        total_revenue=("booking_value", "sum"),
        avg_booking_value=("booking_value", "mean"),
        avg_vtat=("avg_vtat", "mean"),
        avg_ctat=("avg_ctat", "mean")
    )
    .sort_values("total_revenue", ascending=False)
)

vehicle_chart = (
    alt.Chart(vehicle_revenue)
    .mark_bar()
    .encode(
        x=alt.X("total_revenue:Q", title="Total revenue"),
        y=alt.Y("vehicle_type:N", sort="-x", title="Vehicle type"),
        tooltip=[
            "vehicle_type",
            alt.Tooltip("total_bookings:Q", format=","),
            alt.Tooltip("total_revenue:Q", format="$,.2f"),
            alt.Tooltip("avg_booking_value:Q", format="$,.2f"),
            alt.Tooltip("avg_vtat:Q", format=".2f"),
            alt.Tooltip("avg_ctat:Q", format=".2f")
        ]
    )
    .properties(height=350)
)

st.altair_chart(vehicle_chart, use_container_width=True)

if not vehicle_revenue.empty:
    top_vehicle = vehicle_revenue.iloc[0]
    st.info(
        f"""
### Interpretación

El tipo de vehículo con mayores ingresos es **{top_vehicle['vehicle_type']}**, con
**${top_vehicle['total_revenue']:,.0f}** generados en **{top_vehicle['total_bookings']:,.0f} reservas**.

Este análisis permite identificar qué categorías de vehículo tienen mayor peso financiero dentro de la
operación. Sin embargo, un vehículo con altos ingresos no necesariamente es el más eficiente si también
presenta tiempos de espera elevados o una alta tasa de fallas.
"""
    )

st.dataframe(vehicle_revenue, use_container_width=True)

st.divider()


st.markdown("## Evolución mensual de ingresos")

if "mes" in df_filtered.columns:
    monthly_revenue = (
        df_filtered
        .dropna(subset=["mes"])
        .groupby("mes", as_index=False)
        .agg(
            total_bookings=("booking_id", "count"),
            completed_bookings=("is_completed", "sum"),
            cancelled_customer=("is_cancelled_customer", "sum"),
            cancelled_driver=("is_cancelled_driver", "sum"),
            no_driver_found=("is_no_driver_found", "sum"),
            total_revenue=("booking_value", "sum")
        )
        .sort_values("mes")
    )

    monthly_revenue["operational_failures"] = (
        monthly_revenue["cancelled_customer"]
        + monthly_revenue["cancelled_driver"]
        + monthly_revenue["no_driver_found"]
    )

    monthly_revenue["completion_rate_pct"] = (
        monthly_revenue["completed_bookings"] / monthly_revenue["total_bookings"] * 100
    )

    monthly_revenue["operational_failure_rate_pct"] = (
        monthly_revenue["operational_failures"] / monthly_revenue["total_bookings"] * 100
    )

    monthly_revenue["previous_month_revenue"] = monthly_revenue["total_revenue"].shift(1)

    monthly_revenue["revenue_growth_pct"] = (
        (monthly_revenue["total_revenue"] - monthly_revenue["previous_month_revenue"])
        / monthly_revenue["previous_month_revenue"]
        * 100
    )

    revenue_line = (
        alt.Chart(monthly_revenue)
        .mark_line(point=True)
        .encode(
            x=alt.X("mes:T", title="Mes"),
            y=alt.Y("total_revenue:Q", title="Ingresos totales"),
            tooltip=[
                alt.Tooltip("mes:T", title="Mes"),
                alt.Tooltip("total_bookings:Q", title="Reservas", format=","),
                alt.Tooltip("completed_bookings:Q", title="Reservas completadas", format=","),
                alt.Tooltip("completion_rate_pct:Q", title="Completion rate %", format=".2f"),
                alt.Tooltip("operational_failures:Q", title="Fallas operativas", format=","),
                alt.Tooltip("operational_failure_rate_pct:Q", title="Failure rate %", format=".2f"),
                alt.Tooltip("total_revenue:Q", title="Revenue", format="$,.2f"),
                alt.Tooltip("revenue_growth_pct:Q", title="Growth %", format=".2f"),
            ],
        )
        .properties(height=420)
    )

    st.altair_chart(revenue_line, use_container_width=True)

    if not monthly_revenue.empty:
        best_month = monthly_revenue.sort_values("total_revenue", ascending=False).iloc[0]
        worst_month = monthly_revenue.sort_values("total_revenue", ascending=True).iloc[0]
        avg_growth = monthly_revenue["revenue_growth_pct"].dropna().mean()

        st.info(
            f"""
### Interpretación

La evolución mensual permite analizar la estabilidad de los ingresos durante 2024.

El mes con mayores ingresos fue **{best_month['mes'].strftime('%Y-%m')}**, con
**${best_month['total_revenue']:,.0f}**. El mes con menores ingresos fue
**{worst_month['mes'].strftime('%Y-%m')}**, con **${worst_month['total_revenue']:,.0f}**.

El crecimiento mensual promedio fue de **{avg_growth:.2f}%**. Esta métrica permite identificar si el
desempeño financiero fue creciente, estable o volátil a lo largo del año.
"""
        )

    st.dataframe(monthly_revenue, use_container_width=True)

else:
    st.warning(
        """
No se encontró una columna de fecha válida. Revisa si en `dim_date.csv`
existe una columna llamada `fecha`, `full_date`, `date` o `booking_date`.
"""
    )

st.divider()


st.markdown("## Top rutas más rentables")

if "pickup_location" in df_filtered.columns and "drop_location" in df_filtered.columns:
    df_filtered["route"] = (
        df_filtered["pickup_location"].astype(str)
        + " → "
        + df_filtered["drop_location"].astype(str)
    )

    top_routes = (
        df_filtered
        .groupby("route", as_index=False)
        .agg(
            total_bookings=("booking_id", "count"),
            total_revenue=("booking_value", "sum"),
            avg_distance=("ride_distance", "mean")
        )
        .sort_values("total_revenue", ascending=False)
        .head(15)
    )

    routes_chart = (
        alt.Chart(top_routes)
        .mark_bar()
        .encode(
            x=alt.X("total_revenue:Q", title="Total revenue"),
            y=alt.Y("route:N", sort="-x", title="Route"),
            tooltip=[
                "route",
                alt.Tooltip("total_bookings:Q", format=","),
                alt.Tooltip("total_revenue:Q", format="$,.2f"),
                alt.Tooltip("avg_distance:Q", format=".2f")
            ]
        )
        .properties(height=500)
    )

    st.altair_chart(routes_chart, use_container_width=True)

    if not top_routes.empty:
        best_route = top_routes.iloc[0]
        st.info(
            f"""
### Interpretación

La ruta más rentable es **{best_route['route']}**, con ingresos totales de
**${best_route['total_revenue']:,.0f}** y **{best_route['total_bookings']:,.0f} reservas**.

Este resultado permite identificar corredores o trayectos con mayor valor económico para la plataforma,
lo cual puede apoyar decisiones relacionadas con disponibilidad de conductores, cobertura y estrategia
operativa por zona.
"""
        )

    st.dataframe(top_routes, use_container_width=True)

else:
    st.warning("No se encontraron columnas de pickup_location y drop_location.")

st.divider()


st.markdown("## Ranking operativo por tipo de vehículo")

vehicle_ranking = (
    df_filtered
    .groupby("vehicle_type", as_index=False)
    .agg(
        total_bookings=("booking_id", "count"),
        total_revenue=("booking_value", "sum"),
        avg_booking_value=("booking_value", "mean"),
        avg_vtat=("avg_vtat", "mean"),
        avg_ctat=("avg_ctat", "mean"),
        completed_bookings=("is_completed", "sum"),
        cancelled_customer=("is_cancelled_customer", "sum"),
        cancelled_driver=("is_cancelled_driver", "sum"),
        no_driver_found=("is_no_driver_found", "sum"),
        incomplete_bookings=("is_incomplete", "sum")
    )
)

vehicle_ranking["failed_bookings"] = (
    vehicle_ranking["cancelled_customer"]
    + vehicle_ranking["cancelled_driver"]
    + vehicle_ranking["no_driver_found"]
    + vehicle_ranking["incomplete_bookings"]
)

vehicle_ranking["completion_rate_pct"] = (
    vehicle_ranking["completed_bookings"] / vehicle_ranking["total_bookings"] * 100
)

vehicle_ranking["failure_rate_pct"] = (
    vehicle_ranking["failed_bookings"] / vehicle_ranking["total_bookings"] * 100
)

vehicle_ranking = vehicle_ranking.sort_values("failure_rate_pct", ascending=False)

st.dataframe(vehicle_ranking, use_container_width=True)

if not vehicle_ranking.empty:
    highest_failure = vehicle_ranking.iloc[0]
    best_completion = vehicle_ranking.sort_values("completion_rate_pct", ascending=False).iloc[0]

    st.info(
        f"""
### Interpretación

El tipo de vehículo con mayor tasa de fallas es **{highest_failure['vehicle_type']}**, con
**{highest_failure['failure_rate_pct']:.2f}%**. Esto significa que una proporción importante de sus
reservas no termina como viaje completado.

Por otro lado, el vehículo con mejor tasa de finalización es **{best_completion['vehicle_type']}**, con
**{best_completion['completion_rate_pct']:.2f}%**.

Esta comparación permite distinguir entre vehículos con alto potencial financiero y vehículos con mejor
desempeño operativo.
"""
    )

st.divider()


st.markdown("## Impacto de tiempos de espera, fallas e ingresos")

st.markdown(
    """
Esta sección resume la pregunta analítica principal del proyecto:

**¿Cómo impactan las cancelaciones, los tiempos de espera y el tipo de vehículo
en el desempeño operativo y los ingresos de Uber durante 2024?**
"""
)

impact_data = vehicle_ranking.copy()
impact_data = impact_data.sort_values("failure_rate_pct", ascending=False)

impact_chart = (
    alt.Chart(impact_data)
    .mark_bar()
    .encode(
        x=alt.X("failure_rate_pct:Q", title="Failure Rate %"),
        y=alt.Y("vehicle_type:N", sort="-x", title="Tipo de vehículo"),
        tooltip=[
            "vehicle_type",
            alt.Tooltip("failure_rate_pct:Q", format=".2f"),
            alt.Tooltip("avg_ctat:Q", format=".2f"),
            alt.Tooltip("avg_vtat:Q", format=".2f"),
            alt.Tooltip("total_revenue:Q", format="$,.2f"),
            alt.Tooltip("total_bookings:Q", format=",")
        ],
    )
    .properties(height=420)
)

st.altair_chart(impact_chart, use_container_width=True)

if not impact_data.empty:
    highest_failure = impact_data.iloc[0]
    highest_revenue = impact_data.sort_values("total_revenue", ascending=False).iloc[0]
    highest_wait = impact_data.sort_values("avg_ctat", ascending=False).iloc[0]

    st.info(
        f"""
### Interpretación ejecutiva

El tipo de vehículo con mayor tasa de fallas es **{highest_failure['vehicle_type']}**, con
**{highest_failure['failure_rate_pct']:.2f}%**. Esto indica que, de cada 100 reservas de este tipo
de vehículo, aproximadamente **{highest_failure['failure_rate_pct']:.0f}** no terminan como viajes
completados.

El vehículo con mayor generación de ingresos es **{highest_revenue['vehicle_type']}**, con
**${highest_revenue['total_revenue']:,.0f}**. Esto permite diferenciar entre vehículos relevantes
por ingresos y vehículos con mayores problemas operativos.

El mayor tiempo promedio de espera del cliente corresponde a **{highest_wait['vehicle_type']}**, con
**{highest_wait['avg_ctat']:.2f} minutos** promedio. Si este vehículo también presenta una tasa alta
de fallas, puede considerarse un punto crítico de operación.

En conjunto, el análisis muestra que el desempeño de Uber no debe evaluarse únicamente por ingresos,
sino también por eficiencia operativa, tiempos de espera y capacidad para convertir reservas en viajes
completados.
"""
    )

st.dataframe(
    impact_data[
        [
            "vehicle_type",
            "total_bookings",
            "total_revenue",
            "avg_vtat",
            "avg_ctat",
            "failure_rate_pct",
            "completion_rate_pct"
        ]
    ],
    use_container_width=True
)

st.divider()


st.markdown("## Conclusión general")

st.success(
    """
El análisis muestra que el desempeño de Uber durante 2024 no depende únicamente del volumen de reservas
o de los ingresos generados, sino también de la eficiencia operativa con la que se atienden las solicitudes.

Los tipos de vehículo con mayores ingresos no necesariamente son los más eficientes, por lo que es necesario
evaluar simultáneamente ingresos, tiempos de espera y tasa de fallas.

Las cancelaciones, la falta de conductor disponible y los viajes incompletos representan factores clave que
reducen la conversión de reservas en viajes completados y, por lo tanto, afectan el desempeño financiero.

Desde una perspectiva OLAP, el modelo dimensional permite analizar el negocio por tiempo, vehículo, ubicación,
método de pago y estado de reserva, facilitando la identificación de áreas de oportunidad operativa y financiera.
"""
)

st.divider()


st.markdown("## Exploración del dataset integrado")

st.dataframe(
    df_filtered,
    use_container_width=True,
    height=500
)
