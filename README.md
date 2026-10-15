# castcast

**A cast forecast:** which lakes will fish well for bass today?

castcast collects public fisheries, water and weather data from several states and unifies it into one standard schema. It uses an LLM to extract structured signals from free-text fishing reports, trains and monitors a model with MLflow, and serves daily predictions to a color-coded map. Everything runs serverless on AWS, built entirely in Python.

> **Status:** Phase 1 (foundation) in progress. See [Roadmap](#roadmap).

## Scope

- **States:** Texas, Minnesota and New York. *TODO: expand states through the same adapter interface.*
- **Species:** largemouth, smallmouth, spotted and Guadalupe bass. *TODO: expand species.*

## Architecture

```
Ingest              Lakehouse (S3, Iceberg)      LLM extraction       Train / MLOps                Serve                    UI
Lambda collectors → bronze → silver → gold   →   report text →    →   SageMaker Pipelines      →   Batch Transform +    →   Streamlit map
(EventBridge)       Glue Catalog + Athena        structured JSON      LightGBM, MLflow tracking    Serverless Inference     color-coded lakes
                    unified multi-state schema                        Model Registry, Monitor      FastAPI on Lambda
```

## Repository layout

| Package | Responsibility |
|---|---|
| [`core`](packages/core) | Canonical schemas, settings, structured logging, storage IO |
| [`ingest`](packages/ingest) | Source registry and collectors that land raw data in bronze |
| [`pipelines`](packages/pipelines) | State adapters, unification, entity resolution, features |
| [`extract`](packages/extract) | LLM extraction of structured fishing reports |
| [`ml`](packages/ml) | Training, evaluation gate, MLflow registry, drift monitoring |
| [`serving`](packages/serving) | Model loading, prediction, batch scoring |
| [`api`](packages/api) | FastAPI backend on AWS Lambda |
| [`app`](packages/app) | Streamlit map UI |

Each package declares only its own dependencies. CI enforces the dependency direction between packages with [import-linter](https://import-linter.readthedocs.io/); see `[tool.importlinter]` in `pyproject.toml`. The decisions behind the layout are in [`docs/adr`](docs/adr).

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # create .venv with every package and dev tool
uv run pre-commit install    # run the checks on every commit

uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy                  # strict type checking
uv run lint-imports          # architecture contracts
uv run pytest --cov          # tests with coverage
```

### Branching

Work branches → `dev` (squash, deploys to the dev account) → `main` (merge commit, deploys to the prod account). Hotfixes reach `main` only as cherry-picks from `dev`. Both protected branches require a PR and passing checks. See [CONTRIBUTING.md](CONTRIBUTING.md) and [ADR 0003](docs/adr/0003-branching-strategy.md).

## Roadmap

1. **Foundation:** workspace, tooling, CI, infrastructure as code, AWS accounts and guardrails, first Lambda in dev.
2. **Ingestion and lakehouse:** collectors and the bronze, silver and gold layers.
3. **Unification and LLM extraction:** canonical schema, entity resolution, evaluated extraction.
4. **Modeling and MLOps:** baselines, LightGBM, MLflow, evaluation gate, scheduled retraining.
5. **Serving and UI:** batch scoring, API, map, catch log.
6. **Monitoring and production:** drift detection, prediction vs. outcome tracking, prod environment.

## Data sources and responsible use

castcast uses public government and scientific data, plus community sources that are accessed only through official APIs or where a site's terms and robots.txt allow it. Each source's license and terms are recorded in the source registry, and collectors refuse to run against sources that aren't marked compliant.

## License

[MIT](LICENSE)
