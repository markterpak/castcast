# ADR 0002: Provider-agnostic LLM extraction, defaulting to an open-weight model

- Status: Proposed. To be finalized in Phase 3.
- Date: 2026-10-15

## Context

Fishing reports from state agencies and community sources are free text, such as "Bass are also starting to bite." The model needs structured fields from them: waterbody, species, bite rating, water temperature, clarity, depth and techniques. The project's target cost is $0.

Open-weight models such as gpt-oss can do schema-constrained extraction. But gpt-oss-20b needs about 16 GB of memory, which rules out Lambda and the free GitHub-hosted runners.

## Decision

- The extractor uses the **OpenAI-compatible chat completions interface** with JSON-schema output. The base URL and model name come from configuration.
- Every response is validated against the canonical Pydantic `FishingReport` schema. Invalid output is retried, then quarantined, never written to silver.
- Results are cached by a hash of the source text, so unchanged text is never sent again.
- Defaults by environment:
  - **local:** a small local model through Ollama, or the hosted free tier;
  - **dev/prod:** gpt-oss on a hosted free tier, with AWS Bedrock gpt-oss as the low-cost fallback.
- A hand-labeled evaluation set scores each candidate model on field accuracy, cost and latency. The model is chosen on that evidence.

## Consequences

- Switching providers means changing config, not code.
- Free tiers have rate limits and terms that need reviewing before use. The one-time historical backfill should run in batches.
- The evaluation set takes effort to label, but it is what makes the model choice defensible.
