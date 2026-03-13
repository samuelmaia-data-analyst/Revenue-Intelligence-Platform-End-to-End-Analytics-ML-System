# Revenue Intelligence Platform

Plataforma end-to-end de revenue intelligence que transforma dados de comportamento em analytics reproduzível, KPIs de negócio, previsões de machine learning e ações executivas priorizadas.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.43-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-pronto-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://github.com/samuelmaia-analytics/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/actions/workflows/ci.yml/badge.svg)](https://github.com/samuelmaia-analytics/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/actions/workflows/ci.yml)

[Read in English](README.md)

## App Ao Vivo

Streamlit Cloud:

- https://revenue-intelligence-platform.streamlit.app/

## Por Que Este Projeto Se Destaca

- Construído como plataforma, não como notebook isolado: camadas claras de ingestão, transformação, analytics, ML, reporting, API e dashboard
- Outputs orientados a negócio: risco de churn, propensão de recompra, eficiência por canal, ações priorizadas e simulação de impacto
- Execução reproduzível e com padrão de produção: manifesto de pipeline, quality report, model registry, testes e API versionada

## Resumo Executivo

- Problema de negócio: transformar dados comportamentais em decisões de proteção de receita e crescimento
- Usuários principais: Revenue Ops, Marketing, Finanças, Customer Success e liderança
- Entregas centrais: carteira priorizada, KPIs centralizados, modelos interpretáveis e storytelling executivo

## Problema de Negócio

Times comerciais raramente precisam de mais um notebook. Eles precisam de um sistema de decisão que responda:

- Quais clientes têm maior risco de churn e merecem esforço de retenção?
- Quais segmentos têm maior chance de recomprar e merecem estratégia de upsell?
- Quais canais de aquisição são eficientes o suficiente para ganhar orçamento?
- Qual é o impacto esperado das próximas 10 ações prioritárias?

Este repositório foi estruturado como uma plataforma analítica real, e não como um experimento isolado. O escopo original foi preservado, mas o fluxo agora está explícito de ponta a ponta: `raw -> transformed -> analytics -> ML -> insights`.

## Visão da Plataforma

```mermaid
flowchart LR
    A[Dados Brutos de Comportamento] --> B[Ingestão]
    B --> C[Bronze]
    C --> D[Silver]
    D --> E[Feature Engineering]
    D --> F[Gold Star Schema]
    E --> G[Treinamento e Scoring]
    D --> H[Camada de KPIs]
    G --> I[Recomendações]
    H --> J[Reporting Executivo]
    I --> J
    F --> K[Dashboard / API / SQL]
    J --> K
```

## Arquitetura

### Camadas principais

- `src/ingestion.py`: ingestão e persistência da camada bronze
- `src/transformation.py`: padronização silver e base analítica de clientes
- `src/warehouse.py`: publicação da camada gold em star schema
- `src/metrics.py`: centralização de KPIs de receita e snapshot de negócio
- `src/analytics.py`: geração de artefatos analíticos desacoplados do treinamento
- `src/modeling.py`: pré-processamento, treino, scoring, registry e interpretação executiva
- `src/recommendation.py`: priorização da próxima melhor ação
- `src/reporting.py`: outputs executivos e simulações de impacto
- `src/quality.py`: validações de qualidade e integridade
- `src/orchestration.py`: pipeline reproduzível ponta a ponta
- `src/config.py`: configuração de runtime e paths

### Controles de reprodutibilidade

- `PipelineConfig` com seed determinística
- diretórios explícitos para `raw`, `bronze`, `silver`, `gold` e `processed`
- `pipeline_manifest.json` com estágios, tempos e inventário de saídas
- `quality_report.json` com duplicidades, nulos e integridade referencial
- model registry versionado em `data/processed/registry`

Documentação complementar:

- [docs/architecture.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/architecture.md)

## Workflow Analítico

### Fluxo `raw -> transformed -> analytics -> ML -> insights`

1. A fonte é carregada de `data/raw/` ou gerada sinteticamente como fallback determinístico.
2. A camada bronze preserva linhagem com metadados de ingestão.
3. A camada silver aplica checagem de colunas, tipagem, deduplicação, tratamento básico e integridade.
4. O feature engineering gera uma base cliente-nível com recência, frequência, monetário, ARPU e janelas futuras.
5. A camada gold publica `dim_*` e `fact_orders.csv` para consumo analítico desacoplado de ML.
6. A camada de métricas centraliza LTV, CAC, RFM, coorte, unit economics e snapshot executivo.
7. A camada de ML treina churn e próxima compra com avaliação temporal e leitura orientada ao negócio.
8. A camada de recomendação converte score em ação.
9. A camada de reporting empacota os outputs para liderança, operação e dashboard.

## Abordagem de Machine Learning

### Targets

- `is_churned`: ausência de compra na janela futura de 90 dias
- `next_purchase_30d`: propensão de compra na janela futura de 30 dias

### Features

- comportamento: `recency_days`, `frequency`, `monetary`, `avg_order_value`
- ciclo de vida: `tenure_days`, `arpu`
- contexto de negócio: `channel`, `segment`

### Modelagem

- churn: `RandomForestClassifier`
- próxima compra: `LogisticRegression`
- pré-processamento: escala numérica + one-hot encoding
- avaliação: split temporal com fallback estratificado

### Valor para o negócio

- risco de churn apoia alocação de budget de retenção
- propensão de compra apoia timing de upsell e CRM
- scores são traduzidos em ação recomendada
- `metrics_report.json` agora inclui drivers relevantes para leitura executiva

## KPIs de Receita Centralizados

A lógica de métricas agora está tratada como contrato de negócio.

Principais métricas:

- `LTV`
- `CAC`
- `LTV/CAC`
- `ARPU`
- `RFM`
- `Retenção por coorte`
- `Contribution margin`
- `Payback period`
- `% de clientes em alto risco`
- `Simulação de impacto do top 10`

Código principal:

- [src/metrics.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/metrics.py)
- [src/business_rules.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/business_rules.py)

## Outputs Executivos

Saídas principais em `data/processed/`:

- `customer_features.csv`
- `scored_customers.csv`
- `recommendations.csv`
- `ltv.csv`
- `cac_by_channel.csv`
- `rfm_segments.csv`
- `cohort_retention.csv`
- `unit_economics.csv`
- `kpi_snapshot.json`
- `metrics_report.json`
- `executive_report.json`
- `executive_summary.json`
- `business_outcomes.json`
- `top_10_actions.csv`
- `quality_report.json`
- `pipeline_manifest.json`

Uso por público:

- operação: carteira priorizada e lista de ação
- growth/finanças: eficiência por canal e unit economics
- liderança: resumo executivo e simulação de impacto
- engenharia: qualidade de dados, registry e manifesto de pipeline

## Dashboard e Storytelling

O app Streamlit funciona como camada executiva de operação.

Entregas atuais:

- cards de contexto de negócio
- visão consolidada de KPIs
- eficiência por canal
- retenção por coorte
- lens de risco e crescimento
- sumário de performance dos modelos
- drivers dos modelos
- carteira priorizada
- simulação de impacto das top 10 ações

Entrypoint:

- [app/streamlit_app.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/app/streamlit_app.py)

## API

Camada FastAPI com:

- endpoint de health com telemetria e metadados do registry
- endpoint autenticado de scoring
- rotas versionadas em `/api/v1/*`

Serviço principal:

- [services/api/main.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/services/api/main.py)

## Estrutura do Repositório

```text
.
|- app/
|- contracts/
|- data/
|  |- raw/
|  |- bronze/
|  |- silver/
|  |- gold/
|  \- processed/
|- docs/
|- notebooks/
|- services/
|  \- api/
|- sql/
|- src/
|- tests/
|- main.py
\- README.md
```

## Como Rodar

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
python main.py
python -m streamlit run .\app\streamlit_app.py
python -m uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

## CLI

```powershell
python -m src.pipeline run
python -m src.pipeline run --seed 123 --log-level DEBUG
```

### Variáveis de ambiente

- `RIP_DATA_DIR`
- `RIP_SEED`
- `RIP_LOG_LEVEL`
- `RIP_APP_LANG_MODE`
- `RIP_MODEL_DIR`
- `RIP_API_AUTH_MODE`
- `RIP_API_KEYS`

## Testes e Qualidade

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Cobertura automatizada atual:

- contratos de saída do pipeline
- comportamento da API
- integridade de transformação
- outputs executivos
- KPIs centralizados
- pré-processamento
- quality gate

## Por Que o Projeto Está Mais Sênior

- separação clara entre analytics e ML
- camada de métricas tratada como fonte única de verdade
- execução reproduzível com manifesto e registry
- qualidade de dados embutida no pipeline
- modelagem ligada a decisão de negócio
- storytelling executivo e outputs prontos para operação
- visão de plataforma em vez de notebook isolado

## Melhorias Futuras

- orquestração com Airflow ou Prefect
- persistência em warehouse em vez de somente CSV
- monitoramento de drift e calibração
- scenario planning interativo no dashboard
- camada semântica de métricas para governança financeira mais forte
