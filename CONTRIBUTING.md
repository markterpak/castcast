# Contributing

## Branch flow

```
feature/<name>  ──squash──▶  dev  ──merge──▶  main
                             dev acct          prod acct
hotfix/<name> (cherry-picks of dev commits)  ──merge──▶  main
```

`dev` and `main` are protected. Every change arrives through a pull request that passes the `CI` and `Branch policy` checks. The rationale is in [ADR 0003](docs/adr/0003-branching-strategy.md).

### A normal change

```bash
git switch dev && git pull
git switch -c feature/ny-dec-collector     # or fix/, chore/, docs/, refactor/, test/, ci/
# ... commit work ...
git push -u origin HEAD
gh pr create --base dev --fill             # merged with "Squash and merge"
```

### Release to prod

```bash
gh pr create --base main --head dev --title "Release: <summary>"   # merged with "Create a merge commit"
```

### Hotfix

Land the fix on `dev` first through a normal PR, then:

```bash
git switch main && git pull
git switch -c hotfix/<name>
git cherry-pick -x <sha-of-the-squashed-commit-on-dev>   # -x is required; the policy check verifies it
git push -u origin HEAD
gh pr create --base main --fill
```

## Before you push

```bash
uv run pre-commit install   # once; runs the checks below on every commit
uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run lint-imports && uv run pytest --cov
```

## Commit messages

Use the imperative mood ("Add NY DEC collector"). The squashed PR title becomes the commit on `dev`, so write it as a changelog line.
