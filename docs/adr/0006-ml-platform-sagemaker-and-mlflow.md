# ADR 0006: SageMaker for the ML lifecycle, with self-hosted MLflow for tracking

- Status: Accepted
- Date: 2026-10-15

## Context

The model has to be trained, tuned, evaluated against the current production model, registered, promoted, served (daily in batch and on demand), and monitored for drift. All of this must stay near $0.

SageMaker covers the lifecycle end to end, but its always-on options are expensive. A real-time endpoint costs about $150/month even on the cheapest listed instance, and a managed MLflow tracking server costs $0.60/hour (about $430/month).

## Decision

| Concern | Choice | Billing model |
|---|---|---|
| Orchestration | **SageMaker Pipelines**: process → train → evaluate → condition (beats champion) → register | No charge listed; pay for the steps |
| Training | **Training Jobs**, script mode with the `castcast-ml` package, managed spot instances | Per second while running |
| Tuning | **Automatic Model Tuning**, with a capped number of trials | Per training job |
| Registry and promotion | **SageMaker Model Registry**, with `PendingManualApproval` → `Approved` | No charge listed |
| Batch scoring | **Batch Transform** or a Processing job, daily | Per run |
| On-demand prediction | **Serverless Inference**, which scales to zero | Per second of use |
| Monitoring | **Model Monitor**, scheduled data-quality and drift jobs | Per run |
| Experiment tracking | **Self-hosted MLflow**: Postgres metadata store (free tier) and S3 artifacts | ~$0 |
| Tracking UI | MLflow server in a **Lambda container behind a Function URL**, with MLflow basic auth (an admin user and a read-only guest) | ~$0, scales to zero |

- Training jobs log **directly** to the Postgres store and S3 using their IAM role, without going through the UI endpoint. That keeps the Lambda response-size limit out of the write path.
- Credentials live in SSM Parameter Store (SecureString).
- **No real-time endpoints, no always-on MLflow, no Studio apps left running.** SCPs (ADR 0004) and a nightly janitor Lambda enforce this.
- SageMaker managed MLflow may be run for a single session to capture documentation, then deleted the same day.

## Consequences

- Every SageMaker component bills per use, so cost tracks activity rather than time.
- Serverless Inference has a cold start of several seconds after idle periods. That's acceptable, because the map reads precomputed batch scores and only what-if queries hit the endpoint.
- The MLflow UI cold-starts in about 5–10 seconds after idle. If Lambda limits block the UI, the same container moves to a free container host; the store doesn't change.
- Moving away from SageMaker would mean replacing Pipelines and the Registry. The training code itself is plain Python in `castcast-ml` and isn't tied to SageMaker.
