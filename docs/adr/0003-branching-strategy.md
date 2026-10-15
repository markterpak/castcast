# ADR 0003: Branching and promotion: work branch → dev → main

- Status: Accepted
- Date: 2026-10-15

## Context

castcast deploys to two AWS environments: staging and prod. Changes need a predictable promotion path: everything is validated in staging before it reaches prod, and an urgent fix can still reach prod without dragging along unfinished work.

## Decision

| Branch | Purpose | Accepts PRs from | Merge method | Deploys to |
|---|---|---|---|---|
| `feature/*`, `fix/*`, `chore/*`, `docs/*`, `refactor/*`, `test/*`, `ci/*` | One unit of work | n/a | n/a | n/a |
| `dev` | Integration | Work branches | **Squash only** | staging |
| `main` | Release | `dev`, or `hotfix/*` | **Merge commit only** | prod |
| `hotfix/*` | Urgent prod fix | n/a | n/a | n/a |

- **Squash into dev:** each unit of work becomes one reviewable commit, so dev's history reads as a changelog.
- **Merge commits into main:** `dev` → `main` is a merge, so main's history always contains dev's commits and the two branches never diverge. Squashing here would rewrite dev's commits into new ones, and every later promotion would conflict.
- **Hotfixes are cherry-picks:** a fix still lands on dev first, through a normal work-branch PR. A `hotfix/<name>` branch is then cut from `main`, and the dev commit is copied with `git cherry-pick -x`. Dev already has the fix, so no back-merge is needed and the next `dev` → `main` promotion reconciles cleanly.

### Enforcement

1. **Repository rulesets** (`.github/rulesets/*.json`) on `dev` and `main`:
   - a pull request is required, so there are no direct pushes;
   - the required checks must pass, and the branch must be up to date with its target;
   - review threads must be resolved;
   - the merge method is restricted as above;
   - force-pushes and deletion are blocked.
2. **The `Branch policy` workflow** (a required check):
   - rejects a PR whose source branch isn't allowed for its target;
   - for `hotfix/*`, verifies that every commit carries a `(cherry picked from commit <sha>)` trailer whose source commit is on `dev`.

Rulesets are stored as JSON in the repository, so repository settings are reviewed and versioned like code.

## Consequences

- Prod only ever receives code that has passed CI and been integrated on dev, or an audited cherry-pick of such code.
- Required approvals are set to 0 because this is a solo project, and GitHub doesn't let authors approve their own PRs. Raise the count when collaborators join.
- `main` stays the default branch, so the repository landing page shows released code. Work-branch PRs must target `dev` explicitly (`gh pr create --base dev`).
