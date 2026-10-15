# ADR 0005: Lakehouse on S3 with Apache Iceberg, Glue Data Catalog and Athena

- Status: Accepted
- Date: 2026-10-15

## Context

Raw data from three states and several kinds of source lands daily, then is cleaned, unified and turned into model features. The layers need:

- atomic writes;
- upserts (late or corrected records);
- schema evolution as sources change;
- time travel to reproduce training data;
- SQL access for exploration.

Data volume is small: thousands of waterbodies × daily weather and reports.

## Decision

- **Layout:** medallion layers in S3:
  - `bronze`: raw, immutable payloads exactly as fetched;
  - `silver`: cleaned and unified to the canonical multi-state schema;
  - `gold`: model features and labels.
- **Table format:** **Apache Iceberg** for silver and gold. Bronze stays as raw files, with the original bytes preserved.
- **Catalog:** the **AWS Glue Data Catalog**, which is free under 1M objects. **Amazon Athena** provides SQL.
- **Compute:**
  - **Step Functions** orchestrate **Lambda** functions that run **Polars** with **PyIceberg**.
  - An optional **Glue PySpark** job handles the one-time historical backfill.
- **Partitioning:** Iceberg hidden partitioning by `state` and `day(observed_at)`.

## Why Iceberg rather than Delta Lake

- **AWS-native:** Athena reads and writes Iceberg, including MERGE, and Glue catalogs it. On AWS, Delta tables are read-only from Athena.
- **Engine-neutral:** the same tables work from Athena, Glue, EMR, Redshift, Snowflake and Trino, so no single engine is a dependency.
- **Hidden partitioning and partition evolution:** queries prune on `observed_at` without knowing the partition scheme, and the scheme can change without rewriting data.
- **Tradeoff:** PyIceberg is younger than delta-rs for Python-only MERGE, and Iceberg requires a catalog. The Glue catalog is free and wanted for Athena anyway.

## Why not Spark for every step

At this volume, Polars on Lambda finishes each step in seconds for fractions of a cent. A Spark cluster would add startup latency and cost for no benefit. Glue is kept for the backfill, where parallelism actually helps.

## Consequences

- Every silver and gold table can be queried with SQL in Athena and is versioned for reproducible training sets.
- Data contracts are enforced with Pandera before each write. Rows that fail validation go to a quarantine table, never to silver.
