# ADR 0001: Monorepo as a uv workspace of small packages

- Status: Accepted
- Date: 2026-10-15

## Context

castcast has several parts with very different dependencies: scheduled collectors, data pipelines, LLM extraction, model training, a prediction API on AWS Lambda, and a Streamlit UI. They share one data model and have to evolve together.

Each AWS Lambda deployment package has a size limit, so a single package with every dependency would be slow to deploy and could break that limit. The collectors don't need LightGBM, and the UI doesn't need boto3.

## Decision

Use one Git repository organized as a **uv workspace** with one package per component under `packages/`:

| Package | Role | Deploys as |
|---|---|---|
| `core` | Canonical schemas, settings, logging, storage IO | Library |
| `ingest` | Source registry and collectors → bronze | Lambda (scheduled) |
| `pipelines` | Bronze → silver → gold, state unification, features | Lambda / batch job |
| `extract` | LLM extraction of structured reports | Lambda / batch job |
| `ml` | Training, evaluation gate, MLflow, promotion, drift | GitHub Actions job |
| `serving` | Model loading, prediction, batch scoring | Library + Lambda |
| `api` | FastAPI backend for the app | Lambda (Function URL) |
| `app` | Streamlit map UI | Streamlit Community Cloud |

- Every package follows the `src/` layout and has its own `pyproject.toml` with the `uv_build` backend.
- One `uv.lock` pins the whole workspace.
- Tooling config (ruff, mypy, pytest, coverage) lives once, in the root `pyproject.toml`.
- Dependency direction is enforced in CI by **import-linter** contracts:
  - `core` imports nothing else from castcast;
  - the data stages (`ingest`, `pipelines`, `extract`, `ml`) don't import each other and hand off data through storage;
  - `app` reaches data only over HTTP through `api`.

## Consequences

- Each deployable builds with only its own dependency closure, using `uv export --package <name>`.
- Shared contracts (schemas) live in one place, so producers and consumers can't drift apart.
- CI can use path filters to test and deploy only what changed.
- Cost: more `pyproject.toml` files to maintain, and the import contracts need updating whenever a new allowed dependency is added. That is deliberate.

## Alternatives considered

- **A single package:** simplest, but bloats every Lambda and blurs boundaries.
- **A repository per component:** stronger isolation, but versioning shared schemas across repositories is overhead a project this size doesn't need.
