from __future__ import annotations

import streamlit as st

LANGS = {
    "English": {
        "title": "Revenue Intelligence Data Platform",
        "caption": "Executive-grade analytics for revenue, retention, and customer health.",
        "hero_kicker": "Revenue Command Center",
        "hero_summary": (
            "Monitoring {active_months} revenue periods and {customer_count} customers "
            "from curated gold datasets."
        ),
        "sidebar_caption": (
            "Configure the workspace view and navigate the curated operating metrics."
        ),
        "source_mode_title": "Workspace Source",
        "source_mode_auto": "Auto",
        "source_mode_live": "Live Data",
        "source_mode_demo": "Demo Data",
        "source_mode_copy": (
            "Switch between primary curated outputs and bundled portfolio demo assets."
        ),
        "filters_title": "Workspace Filters",
        "start_month": "Start month",
        "end_month": "End month",
        "sidebar_help": "How to use this workspace",
        "sidebar_help_copy": (
            "- Use the month range to focus revenue trends.\n"
            "- Review overview metrics first, then drill into customers and operations.\n"
            "- Re-run `ridp run-pipeline all` when curated artifacts are stale or missing."
        ),
        "nav_title": "Workspace",
        "nav_overview": "Executive Overview",
        "nav_customers": "Customer Health",
        "nav_operations": "Operations",
        "nav_run_history": "Run History",
        "no_months": "No monthly revenue periods available.",
        "gold_missing": (
            "Gold layer not found. Run `ridp run-pipeline all` before opening the dashboard."
        ),
        "demo_banner_copy": (
            "Demo mode is active (`{demo_mode}`), so the dashboard is reading curated sample "
            "artifacts bundled with the repository."
        ),
        "load_error": "The dashboard could not load curated gold datasets.",
        "loading": "Loading curated revenue workspace...",
        "metrics_label": "Performance Snapshot",
        "metrics_title": "Core revenue signals",
        "metrics_copy": (
            "A compact executive readout of commercial performance and retention pressure."
        ),
        "delta_up": "up",
        "delta_down": "down",
        "delta_flat": "flat",
        "delta_vs_prior": "vs prior month",
        "gmv": "GMV",
        "aov": "Average Order Value",
        "active_customers": "Active Customers",
        "churn_rate_proxy": "Churn Proxy",
        "gmv_caption": "Total delivered payment value across the selected window.",
        "aov_caption": "Average revenue per unique order in curated gold data.",
        "active_customers_caption": "Unique delivered-order customers currently represented.",
        "churn_caption": "Share of customers inactive for more than 90 days.",
        "trend_label": "Trend Lens",
        "trend_title": "Revenue momentum",
        "trend_copy": "Monthly revenue trend filtered by the period selected in the sidebar.",
        "current_period": "Current period",
        "prior_period": "Prior period",
        "rolling_average": "Rolling 3M average",
        "quarter_delta": "Quarter-over-quarter",
        "retention_label": "Retention Quality",
        "retention_title": "Cohort retention",
        "retention_copy": (
            "Retention proxy by first-purchase cohort to expose stability and decay patterns."
        ),
        "top_cohorts": "Top cohorts",
        "risk_cohorts": "At-risk cohorts",
        "customers_label": "Customer Analytics",
        "customers_title": "Customer 360 monitoring",
        "customers_copy": (
            "Prioritize high-value customers and identify recency deterioration early."
        ),
        "top_customers": "Top customers by spend",
        "customer_table": "Customer 360 sample",
        "customer_search": "Search customer ID",
        "min_orders": "Minimum orders",
        "segments_title": "Customer segments",
        "segments_copy": "Value and recency distributions highlight where attention is needed.",
        "segment_value": "Value tier mix",
        "segment_recency": "Recency mix",
        "customer_priority": "Priority customers",
        "customer_opportunity": "At-risk high value",
        "operations_label": "Operational Readiness",
        "operations_title": "Artifact health and run context",
        "operations_copy": (
            "Visibility into curated assets, freshness indicators, and schema-backed deliverables."
        ),
        "freshness_title": "Data freshness",
        "run_title": "Latest run",
        "artifact_count_title": "Artifacts tracked",
        "freshness_stale": "Refresh recommended",
        "freshness_healthy": "Recently updated curated layer.",
        "freshness_unknown": "No artifact timestamps available.",
        "run_missing": "No tracked run ID",
        "artifact_count_copy": "Gold datasets with metadata sidecars.",
        "artifacts_title": "Curated artifacts available",
        "artifact_name": "Artifact",
        "artifact_rows": "Rows",
        "artifact_updated": "Updated (UTC)",
        "artifact_run": "Run ID",
        "artifacts_empty": "No curated artifacts were found in the gold layer.",
        "quality_title": "Quality notes",
        "quality_copy": (
            "This dashboard reads only curated gold outputs. Missing or stale datasets "
            "should be treated as pipeline issues, not hidden by the presentation layer."
        ),
        "run_history_title": "Execution history",
        "run_history_copy": "Track recent pipeline executions and compare produced artifacts.",
        "run_history_empty": "No pipeline run manifests were found yet.",
        "run_compare_title": "Compare runs",
        "run_compare_left": "Reference run",
        "run_compare_right": "Comparison run",
        "run_compare_summary": "Artifact-level differences between selected runs.",
        "run_compare_only_left": "Only in reference",
        "run_compare_only_right": "Only in comparison",
        "run_compare_shared": "Shared artifacts",
        "run_catalog_title": "Run catalog",
        "run_catalog_copy": "Execution index with artifact counts and snapshot roots.",
        "run_sql_title": "SQL run history",
        "run_sql_copy": "SQLite-backed operational registry for recent pipeline runs.",
        "footer_title": "Operational note",
        "footer_copy": (
            "Dashboard is currently reading `{source_mode}` artifacts from `{gold_dir}` "
            "with run manifests at `{run_dir}`"
        ),
    },
    "Portuguese": {
        "title": "Plataforma de Inteligencia de Receita",
        "caption": "Analytics executiva para receita, retencao e saude da base de clientes.",
        "hero_kicker": "Centro de Controle de Receita",
        "hero_summary": (
            "Monitorando {active_months} periodos de receita e {customer_count} clientes "
            "a partir de datasets gold curados."
        ),
        "sidebar_caption": (
            "Configure a visao do workspace e navegue pelas metricas operacionais curadas."
        ),
        "source_mode_title": "Fonte do Workspace",
        "source_mode_auto": "Auto",
        "source_mode_live": "Dados reais",
        "source_mode_demo": "Dados demo",
        "source_mode_copy": (
            "Alterne entre os artefatos curados principais e os assets demo do portfolio."
        ),
        "filters_title": "Filtros do Workspace",
        "start_month": "Mes inicial",
        "end_month": "Mes final",
        "sidebar_help": "Como usar este workspace",
        "sidebar_help_copy": (
            "- Use o intervalo de meses para focar na tendencia de receita.\n"
            "- Revise os indicadores do overview antes de aprofundar em clientes e operacao.\n"
            "- Reexecute `ridp run-pipeline all` quando os artefatos estiverem ausentes "
            "ou desatualizados."
        ),
        "nav_title": "Workspace",
        "nav_overview": "Overview Executivo",
        "nav_customers": "Saude de Clientes",
        "nav_operations": "Operacao",
        "nav_run_history": "Historico de Runs",
        "no_months": "Nenhum periodo mensal de receita disponivel.",
        "gold_missing": (
            "Camada Gold nao encontrada. Execute `ridp run-pipeline all` "
            "antes de abrir o dashboard."
        ),
        "demo_banner_copy": (
            "O modo demo esta ativo (`{demo_mode}`), entao o dashboard esta lendo artefatos "
            "de exemplo versionados no repositorio."
        ),
        "load_error": "O dashboard nao conseguiu carregar os datasets gold curados.",
        "loading": "Carregando workspace de receita curado...",
        "metrics_label": "Resumo de Performance",
        "metrics_title": "Sinais centrais de receita",
        "metrics_copy": (
            "Leitura executiva compacta da performance comercial e da pressao de churn."
        ),
        "delta_up": "alta",
        "delta_down": "queda",
        "delta_flat": "estavel",
        "delta_vs_prior": "vs mes anterior",
        "gmv": "GMV",
        "aov": "Ticket Medio",
        "active_customers": "Clientes Ativos",
        "churn_rate_proxy": "Proxy de Churn",
        "gmv_caption": "Valor total de pagamentos entregues na janela selecionada.",
        "aov_caption": "Receita media por pedido unico na camada gold.",
        "active_customers_caption": "Clientes unicos com pedidos entregues representados.",
        "churn_caption": "Parcela de clientes inativos ha mais de 90 dias.",
        "trend_label": "Leitura de Tendencia",
        "trend_title": "Momento de receita",
        "trend_copy": "Tendencia mensal de receita filtrada pelo periodo escolhido na sidebar.",
        "current_period": "Periodo atual",
        "prior_period": "Periodo anterior",
        "rolling_average": "Media movel 3M",
        "quarter_delta": "Trimestre contra trimestre",
        "retention_label": "Qualidade de Retencao",
        "retention_title": "Retencao por cohort",
        "retention_copy": (
            "Proxy de retencao por cohort de primeira compra para expor estabilidade e queda."
        ),
        "top_cohorts": "Melhores cohorts",
        "risk_cohorts": "Cohorts em risco",
        "customers_label": "Analiticos de Clientes",
        "customers_title": "Monitoramento Customer 360",
        "customers_copy": "Priorize clientes de maior valor e detecte piora de recencia cedo.",
        "top_customers": "Top clientes por gasto",
        "customer_table": "Amostra Customer 360",
        "customer_search": "Buscar customer ID",
        "min_orders": "Minimo de pedidos",
        "segments_title": "Segmentos de clientes",
        "segments_copy": "Distribuicoes de valor e recencia destacam onde agir primeiro.",
        "segment_value": "Mix por faixa de valor",
        "segment_recency": "Mix por faixa de recencia",
        "customer_priority": "Clientes prioritarios",
        "customer_opportunity": "Alto valor em risco",
        "operations_label": "Prontidao Operacional",
        "operations_title": "Saude dos artefatos e contexto de execucao",
        "operations_copy": (
            "Visibilidade sobre datasets curados, sinais de frescor e entregaveis com contrato."
        ),
        "freshness_title": "Atualizacao dos dados",
        "run_title": "Ultimo run",
        "artifact_count_title": "Artefatos rastreados",
        "freshness_stale": "Atualizacao recomendada",
        "freshness_healthy": "Camada curada atualizada recentemente.",
        "freshness_unknown": "Nao ha timestamps de artefatos disponiveis.",
        "run_missing": "Nenhum run ID rastreado",
        "artifact_count_copy": "Datasets gold com sidecars de metadados.",
        "artifacts_title": "Artefatos curados disponiveis",
        "artifact_name": "Artefato",
        "artifact_rows": "Linhas",
        "artifact_updated": "Atualizado (UTC)",
        "artifact_run": "Run ID",
        "artifacts_empty": "Nenhum artefato curado foi encontrado na camada gold.",
        "quality_title": "Notas de qualidade",
        "quality_copy": (
            "Este dashboard le apenas saidas gold curadas. Datasets ausentes "
            "ou desatualizados devem ser tratados como problema de pipeline, "
            "nao escondidos pela camada de apresentacao."
        ),
        "run_history_title": "Historico de execucoes",
        "run_history_copy": "Acompanhe execucoes recentes do pipeline e compare artefatos gerados.",
        "run_history_empty": "Nenhum manifesto de run do pipeline foi encontrado.",
        "run_compare_title": "Comparar runs",
        "run_compare_left": "Run de referencia",
        "run_compare_right": "Run de comparacao",
        "run_compare_summary": "Diferencas de artefatos entre os runs selecionados.",
        "run_compare_only_left": "Apenas na referencia",
        "run_compare_only_right": "Apenas na comparacao",
        "run_compare_shared": "Artefatos compartilhados",
        "run_catalog_title": "Catalogo de runs",
        "run_catalog_copy": "Indice de execucoes com contagem de artefatos e snapshot roots.",
        "run_sql_title": "Historico SQL de runs",
        "run_sql_copy": "Registro operacional em SQLite para execucoes recentes do pipeline.",
        "footer_title": "Nota operacional",
        "footer_copy": (
            "O dashboard esta lendo artefatos `{source_mode}` de `{gold_dir}` "
            "com manifests em `{run_dir}`"
        ),
    },
    "Spanish": {
        "title": "Plataforma de Inteligencia de Ingresos",
        "caption": "Analitica ejecutiva para ingresos, retencion y salud de clientes.",
        "hero_kicker": "Centro de Control de Ingresos",
        "hero_summary": (
            "Monitoreando {active_months} periodos de ingresos y {customer_count} clientes "
            "desde datasets gold curados."
        ),
        "sidebar_caption": (
            "Configura la vista del workspace y navega por metricas operativas curadas."
        ),
        "source_mode_title": "Fuente del Workspace",
        "source_mode_auto": "Auto",
        "source_mode_live": "Datos reales",
        "source_mode_demo": "Datos demo",
        "source_mode_copy": (
            "Alterna entre los artefactos curados principales y los assets demo del portafolio."
        ),
        "filters_title": "Filtros del Workspace",
        "start_month": "Mes inicial",
        "end_month": "Mes final",
        "sidebar_help": "Como usar este workspace",
        "sidebar_help_copy": (
            "- Usa el rango de meses para enfocar la tendencia de ingresos.\n"
            "- Revisa primero el overview y luego profundiza en clientes y operacion.\n"
            "- Ejecuta `ridp run-pipeline all` cuando los artefactos esten ausentes "
            "o desactualizados."
        ),
        "nav_title": "Workspace",
        "nav_overview": "Resumen Ejecutivo",
        "nav_customers": "Salud de Clientes",
        "nav_operations": "Operacion",
        "nav_run_history": "Historial de Runs",
        "no_months": "No hay periodos mensuales de ingresos disponibles.",
        "gold_missing": (
            "Capa Gold no encontrada. Ejecuta `ridp run-pipeline all` "
            "antes de abrir el dashboard."
        ),
        "demo_banner_copy": (
            "El modo demo esta activo (`{demo_mode}`), por lo que el dashboard esta leyendo "
            "artefactos de ejemplo versionados en el repositorio."
        ),
        "load_error": "El dashboard no pudo cargar los datasets gold curados.",
        "loading": "Cargando workspace curado de ingresos...",
        "metrics_label": "Resumen de Performance",
        "metrics_title": "Senales clave de ingresos",
        "metrics_copy": (
            "Lectura ejecutiva compacta del rendimiento comercial y la presion de churn."
        ),
        "delta_up": "sube",
        "delta_down": "baja",
        "delta_flat": "estable",
        "delta_vs_prior": "vs mes anterior",
        "gmv": "GMV",
        "aov": "Valor Promedio por Orden",
        "active_customers": "Clientes Activos",
        "churn_rate_proxy": "Proxy de Churn",
        "gmv_caption": "Valor total de pagos entregados en la ventana seleccionada.",
        "aov_caption": "Ingreso promedio por orden unica en la capa gold curada.",
        "active_customers_caption": "Clientes unicos con ordenes entregadas representadas.",
        "churn_caption": "Porcentaje de clientes inactivos por mas de 90 dias.",
        "trend_label": "Lectura de Tendencia",
        "trend_title": "Momento de ingresos",
        "trend_copy": (
            "Tendencia mensual de ingresos filtrada por el periodo elegido en la sidebar."
        ),
        "current_period": "Periodo actual",
        "prior_period": "Periodo anterior",
        "rolling_average": "Promedio movil 3M",
        "quarter_delta": "Trimestre contra trimestre",
        "retention_label": "Calidad de Retencion",
        "retention_title": "Retencion por cohorte",
        "retention_copy": (
            "Proxy de retencion por cohorte de primera compra para exponer estabilidad y caida."
        ),
        "top_cohorts": "Mejores cohortes",
        "risk_cohorts": "Cohortes en riesgo",
        "customers_label": "Analitica de Clientes",
        "customers_title": "Monitoreo Customer 360",
        "customers_copy": (
            "Prioriza clientes de alto valor e identifica deterioro de recencia temprano."
        ),
        "top_customers": "Top clientes por gasto",
        "customer_table": "Muestra Customer 360",
        "customer_search": "Buscar customer ID",
        "min_orders": "Minimo de ordenes",
        "segments_title": "Segmentos de clientes",
        "segments_copy": "Las distribuciones de valor y recencia muestran donde actuar primero.",
        "segment_value": "Mix por nivel de valor",
        "segment_recency": "Mix por nivel de recencia",
        "customer_priority": "Clientes prioritarios",
        "customer_opportunity": "Alto valor en riesgo",
        "operations_label": "Preparacion Operativa",
        "operations_title": "Salud de artefactos y contexto de ejecucion",
        "operations_copy": (
            "Visibilidad de datasets curados, frescura y entregables respaldados por contrato."
        ),
        "freshness_title": "Frescura de datos",
        "run_title": "Ultimo run",
        "artifact_count_title": "Artefactos rastreados",
        "freshness_stale": "Actualizacion recomendada",
        "freshness_healthy": "Capa curada actualizada recientemente.",
        "freshness_unknown": "No hay timestamps de artefactos disponibles.",
        "run_missing": "No hay run ID rastreado",
        "artifact_count_copy": "Datasets gold con sidecars de metadata.",
        "artifacts_title": "Artefactos curados disponibles",
        "artifact_name": "Artefacto",
        "artifact_rows": "Filas",
        "artifact_updated": "Actualizado (UTC)",
        "artifact_run": "Run ID",
        "artifacts_empty": "No se encontraron artefactos curados en la capa gold.",
        "quality_title": "Notas de calidad",
        "quality_copy": (
            "Este dashboard lee solo salidas gold curadas. Datasets ausentes "
            "o desactualizados deben tratarse como problema de pipeline, "
            "no ocultarse en la capa de presentacion."
        ),
        "run_history_title": "Historial de ejecuciones",
        "run_history_copy": (
            "Sigue ejecuciones recientes del pipeline y compara artefactos generados."
        ),
        "run_history_empty": "Aun no se encontraron manifiestos de ejecucion.",
        "run_compare_title": "Comparar runs",
        "run_compare_left": "Run de referencia",
        "run_compare_right": "Run de comparacion",
        "run_compare_summary": "Diferencias de artefactos entre los runs seleccionados.",
        "run_compare_only_left": "Solo en referencia",
        "run_compare_only_right": "Solo en comparacion",
        "run_compare_shared": "Artefactos compartidos",
        "run_catalog_title": "Catalogo de runs",
        "run_catalog_copy": "Indice de ejecuciones con conteo de artefactos y snapshot roots.",
        "run_sql_title": "Historial SQL de runs",
        "run_sql_copy": "Registro operativo en SQLite para ejecuciones recientes del pipeline.",
        "footer_title": "Nota operativa",
        "footer_copy": (
            "El dashboard esta leyendo artefactos `{source_mode}` desde `{gold_dir}` "
            "con manifests en `{run_dir}`"
        ),
    },
}


def get_labels() -> dict[str, str]:
    selected_language = st.session_state.get("dashboard_language", "English")
    return LANGS[selected_language]
