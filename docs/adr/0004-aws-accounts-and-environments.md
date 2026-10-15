# ADR 0004: One AWS account per environment, under AWS Organizations

- Status: Accepted
- Date: 2026-10-15
- Amends: ADR 0003 (environment names)

## Context

castcast deploys from two long-lived branches: `dev` and `main`. A bug or a runaway cost in pre-production must not affect production data or uptime. The project also has to stay close to $0, so guardrails must stop expensive resources from being created, not just report them afterwards.

## Decision

Use an AWS Organization with three accounts, all in **us-east-1**, on the Paid plan:

| Account | Purpose | Deployed from |
|---|---|---|
| management | Billing, IAM Identity Center, Organizations, SCPs. **No workloads.** | n/a |
| `castcast-dev` | Integration environment | `dev` branch |
| `castcast-prod` | Production | `main` branch, with an environment approval |

Environment names now match the branches and accounts:

- `local`: a developer laptop;
- `dev`: the `castcast-dev` account;
- `prod`: the `castcast-prod` account.

These replace the earlier `dev` (laptop) / `staging` / `prod` names.

- **Access:** IAM Identity Center, with one MFA-protected user and a permission set per account. No IAM users and no long-lived access keys.
- **CI/CD:** GitHub Actions assumes a per-account IAM role through **OIDC**, and each role's trust policy is limited to its branch.
- **Guardrails:** Service Control Policies on the `workloads` OU, stored as code in the repository. They:
  - deny every region except us-east-1;
  - deny SageMaker real-time endpoints on instances (Serverless Inference stays allowed);
  - deny NAT gateways and large instance types;
  - deny leaving the organization and disabling logging.
- **Cost:** budgets and Cost Anomaly Detection in the management account, plus a budget action that restricts SageMaker if spending passes the threshold.

## Consequences

- dev and prod are isolated by a hard account boundary, so a broken deploy or a bad IAM policy in dev can't touch prod.
- SCPs make expensive mistakes impossible to create, not just visible after the fact.
- Each account is bootstrapped for CDK separately, and IaC is parameterized by environment.
- **Data:** prod runs the canonical ingestion. Sources without archives (such as the NY DEC weekly hotlines) are captured only there, so they're never fetched twice. dev runs on a small sample of lakes.
- AWS Control Tower was considered and rejected. It is free itself, but it enables billed services (such as AWS Config) that a two-account hobby project doesn't need.
