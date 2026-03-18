# Revenue Intelligence Platform

Plataforma batch orientada a engenharia séria para transformar dados de comportamento de clientes em saídas reproduzíveis de inteligência de receita.

Este repositório é propositalmente pequeno. O objetivo não é simular um stack enterprise grande. O objetivo é demonstrar disciplina de engenharia em um workflow analítico realista: ingerir, validar, curar, pontuar, reportar, persistir e rastrear cada execução.

[English version](README.md)

## O Que Este Repositório Demonstra

- um único entrypoint oficial para o pipeline batch
- outputs curados reprocessáveis e determinísticos
- manifests, logs, snapshots e retenção por execução
- escrita atômica para artefatos críticos
- configuração por ambiente via `.env`
- governança leve, porém real, via contratos e data dictionary gerado
- quality gates com lint, formatação, type-check, testes, build de pacote e validação de container

## Escopo do Sistema

A plataforma transforma dados brutos de clientes e pedidos em:

- churn risk
- propensão de próxima compra
- eficiência por canal e unit economics
- cohort retention
- snapshots executivos de KPI
- recomendações priorizadas de ação
- tabelas de warehouse consultáveis

Este é um sistema batch-first. Streamlit, FastAPI, dbt, Airflow e Prefect são consumidores ou wrappers opcionais do core batch, não fontes concorrentes de verdade orquestracional.

## Caminho Oficial de Operação

Execute o pipeline com:

```powershell
python -m src.pipeline run
```

Esse é o caminho primário suportado.

Módulos principais:

- [src/pipeline.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/pipeline.py): CLI
- [src/orchestration.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/orchestration.py): pipeline end-to-end
- [src/config.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/config.py): configuração de runtime
- [src/ingestion.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/ingestion.py): ingestão raw e bronze
- [src/transformation.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/transformation.py): silver e feature engineering
- [src/modeling.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/modeling.py): treino, scoring e registry
- [src/reporting.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/reporting.py): artefatos executivos
- [src/persistence.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/persistence.py): persistência em warehouse
- [src/governance.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/governance.py): governança gerada

## Arquitetura

```text
raw input
  -> ingestion
  -> bronze
  -> silver validation
  -> customer features
  -> gold warehouse tables
  -> ML scoring
  -> métricas curadas e recomendações
  -> reporting
  -> manifests, logs, snapshots e retenção
```

Notas arquiteturais:

- o projeto usa camadas explícitas baseadas em arquivos porque isso facilita reprodutibilidade e inspeção local
- SQLite é o warehouse padrão porque mantém o sistema executável sem infraestrutura externa
- a governança é propositalmente leve e concentrada nos outputs de maior sinal

Veja também:

- [docs/architecture.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/architecture.md)
- [docs/repository_structure.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/repository_structure.md)

## Artefatos Operacionais

Uma execução bem-sucedida gera, no mínimo:

- `data/processed/pipeline_manifest.json`
- `data/processed/raw_input_metadata.json`
- `data/processed/quality_report.json`
- `data/processed/freshness_report.json`
- `data/processed/kpi_snapshot.json`
- `data/processed/data_dictionary.json`
- `data/warehouse/revenue_intelligence.db`
- `data/runs/<run_id>/pipeline.log`
- `data/snapshots/<run_id>/`
- `data/manifests/<run_id>.success.json`

Em caso de falha:

- `data/manifests/<run_id>.failure.json`

## Modelo de Confiabilidade

Este repositório foi desenhado para mostrar operação batch disciplinada, não apenas lógica de negócio.

Controles implementados:

- escrita atômica de CSV e JSON
- substituição atômica do SQLite
- `run_id` explícito
- fingerprint de input
- metadata dos inputs raw
- freshness checks orientados à fonte
- manifests de sucesso e falha
- retenção de snapshots por quantidade e idade
- retenção de manifests de falha por idade

## Setup Local

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
python -m src.pipeline run
```

Comandos úteis:

```powershell
make pipeline
make dictionary
make lint
make type-check
make test
make quality
make package
```

## Configuração

As configurações de runtime são lidas de `.env` e de variáveis de ambiente.

Variáveis principais:

- `RIP_ENV`
- `RIP_DATA_DIR`
- `RIP_SEED`
- `RIP_LOG_LEVEL`
- `RIP_FRESHNESS_MAX_AGE_HOURS`
- `RIP_SNAPSHOT_RETENTION_RUNS`
- `RIP_SNAPSHOT_RETENTION_DAYS`
- `RIP_FAILURE_RETENTION_DAYS`
- `RIP_WAREHOUSE_TARGET`
- `RIP_WAREHOUSE_URL`
- `RIP_SEMANTIC_METRICS_PATH`

Template de referência:

- [.env.example](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/.env.example)

## Padrões de Qualidade

O repositório deve permanecer verde em:

- `ruff`
- `black`
- `isort`
- `mypy`
- `pytest`
- `build`

A CI também valida:

- build da imagem Docker
- execução real da CLI oficial no container
- upload dos artefatos do smoke run

## Interfaces Opcionais

Existem interfaces opcionais, mas secundárias ao core batch:

- Streamlit UI: `python -m streamlit run app/streamlit_app.py`
- FastAPI service: `python -m uvicorn services.api.main:app --reload`
- dbt project: `dbt --project-dir dbt run`
- exemplos de Airflow e Prefect em `orchestration/`

## Contribuição

Use o repositório como um sistema pequeno, porém sério, e não como um lugar para empilhar features.

Leia:

- [CONTRIBUTING.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/CONTRIBUTING.md)
- [.github/pull_request_template.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/.github/pull_request_template.md)

## Trade-offs Técnicos

- os modelos em scikit-learn são suficientes para o escopo pretendido, mas este repositório não se apresenta como serving system online de larga escala
- governança baseada em arquivos melhora a reprodutibilidade, mas não substitui uma plataforma completa de metadata
- exemplos de scheduler existem para reforçar o aspecto operacional, mas o repositório continua CLI-first por design

## Roadmap

Próximos passos de maior impacto:

- reforçar ainda mais a evidência de execução em container na CI
- aprofundar a validação de integração do SQLite
- suportar backfill explícito na CLI
- adicionar uma superfície upstream governada por contrato
- apertar ainda mais as fronteiras do core batch

Artefatos de planejamento:

- [docs/staff_upgrade_master_issue.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/staff_upgrade_master_issue.md)
- [docs/issues/project_board.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/issues/project_board.md)
