from __future__ import annotations

import pandas as pd
import streamlit as st

from analytics.business_metrics import cohort_retention
from analytics.kpi_metrics import kpi_dict
from ridp.config import get_data_directories


GOLD_DIR = get_data_directories().gold
LANGS = {
    "English": {
        "page_title": "Revenue Intelligence Platform",
        "title": "Revenue Intelligence Data Platform",
        "caption": "Bronze/Silver/Gold analytics stack with business KPIs and retention insights.",
        "language": "Language",
        "gold_missing": "Gold layer not found. Run the pipelines first.",
        "gmv": "GMV",
        "aov": "AOV",
        "active_customers": "Active Customers",
        "churn_rate_proxy": "Churn Rate Proxy",
        "monthly_revenue": "Monthly Revenue",
        "cohort_retention": "Cohort Retention",
        "customer_360": "Customer 360 Sample",
    },
    "Portuguese": {
        "page_title": "Plataforma de Inteligencia de Receita",
        "title": "Plataforma de Inteligencia de Receita",
        "caption": "Stack analitico Bronze/Silver/Gold com KPIs de negocio e insights de retencao.",
        "language": "Idioma",
        "gold_missing": "Camada Gold nao encontrada. Execute os pipelines primeiro.",
        "gmv": "GMV",
        "aov": "AOV",
        "active_customers": "Clientes Ativos",
        "churn_rate_proxy": "Proxy de Churn",
        "monthly_revenue": "Receita Mensal",
        "cohort_retention": "Retencao por Cohort",
        "customer_360": "Amostra Customer 360",
    },
    "Spanish": {
        "page_title": "Plataforma de Inteligencia de Ingresos",
        "title": "Plataforma de Inteligencia de Ingresos",
        "caption": "Stack analitico Bronze/Silver/Gold con KPIs de negocio e insights de retencion.",
        "language": "Idioma",
        "gold_missing": "Capa Gold no encontrada. Ejecuta los pipelines primero.",
        "gmv": "GMV",
        "aov": "AOV",
        "active_customers": "Clientes Activos",
        "churn_rate_proxy": "Proxy de Churn",
        "monthly_revenue": "Ingresos Mensuales",
        "cohort_retention": "Retencion por Cohorte",
        "customer_360": "Muestra Customer 360",
    },
}


def main() -> None:
    st.set_page_config(page_title="Revenue Intelligence Platform", layout="wide")
    selected_lang = st.sidebar.selectbox("Language / Idioma", options=list(LANGS.keys()), index=0)
    t = LANGS[selected_lang]

    st.sidebar.caption(f"{t['language']}: {selected_lang}")
    st.title(t["title"])
    st.caption(t["caption"])

    if not (GOLD_DIR / "business_kpis.csv").exists():
        st.error(t["gold_missing"])
        return

    metrics = kpi_dict(GOLD_DIR)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t["gmv"], f"{metrics.get('gmv_total', 0):,.2f}")
    col2.metric(t["aov"], f"{metrics.get('aov', 0):,.2f}")
    col3.metric(t["active_customers"], f"{int(metrics.get('active_customers', 0)):,}")
    col4.metric(t["churn_rate_proxy"], f"{metrics.get('churn_rate_proxy', 0):.1%}")

    monthly = pd.read_csv(GOLD_DIR / "kpi_monthly_revenue.csv")
    if not monthly.empty:
        st.subheader(t["monthly_revenue"])
        st.line_chart(monthly.sort_values("order_month").set_index("order_month")["revenue"])

    retention = cohort_retention(GOLD_DIR)
    if not retention.empty:
        st.subheader(t["cohort_retention"])
        st.dataframe(retention, use_container_width=True)

    customer_360 = pd.read_csv(GOLD_DIR / "customer_360.csv")
    st.subheader(t["customer_360"])
    st.dataframe(customer_360.head(25), use_container_width=True)


if __name__ == "__main__":
    main()
