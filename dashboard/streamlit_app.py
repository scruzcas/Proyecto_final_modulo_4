# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path


# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Uber Ride Analytics 2024",
    page_icon="🚗",
    layout="wide"
)

DATA_DIR = Path(__file__).parent / "data"


# =========================
# CARGA DE DATOS
# =========================
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

    if "full_date" in df.columns:
        df["full_date"] = pd.to_datetime(df["full_date"])

    if "month" in df.columns:
        df["month"] = df["month"].astype(str)

    return df


df = load_data()


# =========================
# ENCABEZADO
# =========================
st.title("🚗 Uber Ride Analytics 2024")

st.markdown(
    """
    Dashboard OLAP construido a partir de un modelo dimensional en AWS Aurora PostgreSQL.
    
    Esta versión funciona de forma **offline**, leyendo archivos CSV exportados desde el Data Warehouse.
    El objetivo es analizar cómo las cancelaciones, los tiempos de espera y el tipo de vehículo impactan
    el desempeño operativo y los ingresos de Uber durante 2024.
    """
)

st.divider()


# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros del dashboard")

vehicle_options = sorted(df["vehicle_type"].dropna().unique())
status_options = sorted(df["booking_status"].dropna().unique())

vehicle_filter = st.sidebar.multiselect(
    "Tipo de vehículo",
    options=vehicle_options,
    default=vehicle_options
)

status_filter = st.sidebar.multiselect(
    "Estado del viaje",
    options=status_options,
    default=status_options
)

df_filtered = df[
    (df["vehicle_type"].isin(vehicle_filter)) &
    (df["booking_status"].isin(status_filter))
].copy()


# =========================
# PARTE I — KPIs GENERALES
# =========================
st.markdown("## Parte I: Desempeño general")

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

st.divider()


# =========================
# PARTE II — ESTADOS DE VIAJE
# =========================
st.markdown("## Parte II: Distribución de estados de viaje")

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

st.divider()


# =========================
# PARTE III — INGRESOS POR VEHÍCULO
# =========================
st.markdown("## Parte III: Ingresos por tipo de vehículo")

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

st.dataframe(
    vehicle_revenue,
    use_container_width=True
)

st.divider()


# =========================
# PARTE IV — EVOLUCIÓN MENSUAL
# =========================
st.markdown("## Parte IV: Evolución mensual de ingresos")

if "year_month" in df_filtered.columns:
    month_col = "year_month"
elif "month_name" in df_filtered.columns:
    month_col = "month_name"
elif "month" in df_filtered.columns:
    month_col = "month"
else:
    month_col = None

if month_col:
    monthly_revenue = (
        df_filtered
        .groupby(month_col, as_index=False)
        .agg(
            total_bookings=("booking_id", "count"),
            total_revenue=("booking_value", "sum")
        )
        .sort_values(month_col)
    )

    monthly_chart = (
        alt.Chart(monthly_revenue)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{month_col}:N", title="Month"),
            y=alt.Y("total_revenue:Q", title="Total revenue"),
            tooltip=[
                month_col,
                alt.Tooltip("total_bookings:Q", format=","),
                alt.Tooltip("total_revenue:Q", format="$,.2f")
            ]
        )
        .properties(height=400)
    )

    st.altair_chart(monthly_chart, use_container_width=True)
else:
    st.warning("No se encontró una columna de mes en dim_date.")

st.divider()


# =========================
# PARTE V — TOP RUTAS MÁS RENTABLES
# =========================
st.markdown("## Parte V: Top rutas más rentables")

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

    st.dataframe(
        top_routes,
        use_container_width=True
    )

else:
    st.warning("No se encontraron columnas de pickup_location y drop_location.")

st.divider()


# =========================
# PARTE VI — RANKING OPERATIVO POR VEHÍCULO
# =========================
st.markdown("## Parte VI: Ranking operativo por tipo de vehículo")

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

st.dataframe(
    vehicle_ranking,
    use_container_width=True
)

st.divider()


# =========================
# PARTE VII — IMPACTO ESPERA / FALLAS / INGRESOS
# =========================
st.markdown("## Parte VII: Impacto de tiempos de espera, fallas e ingresos")

st.markdown(
    """
    Esta visualización resume la pregunta analítica principal del proyecto:
    
    **¿Cómo impactan las cancelaciones, los tiempos de espera y el tipo de vehículo
    en el desempeño operativo y los ingresos de Uber durante 2024?**
    """
)

bubble_data = vehicle_ranking.copy()

bubble_chart = (
    alt.Chart(bubble_data)
    .mark_circle(opacity=0.75)
    .encode(
        x=alt.X("avg_ctat:Q", title="Avg CTAT - Customer Wait Time"),
        y=alt.Y("failure_rate_pct:Q", title="Failure Rate %"),
        size=alt.Size("total_revenue:Q", title="Total Revenue"),
        color=alt.Color("vehicle_type:N", title="Vehicle Type"),
        tooltip=[
            "vehicle_type",
            alt.Tooltip("avg_ctat:Q", format=".2f"),
            alt.Tooltip("avg_vtat:Q", format=".2f"),
            alt.Tooltip("failure_rate_pct:Q", format=".2f"),
            alt.Tooltip("total_revenue:Q", format="$,.2f"),
            alt.Tooltip("total_bookings:Q", format=",")
        ]
    )
    .properties(height=500)
)

st.altair_chart(bubble_chart, use_container_width=True)

st.divider()


# =========================
# DATASET FINAL
# =========================
st.markdown("## Exploración del dataset integrado")

st.dataframe(
    df_filtered,
    use_container_width=True,
    height=500
)
