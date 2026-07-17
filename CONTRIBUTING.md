# Contributing to OpenVIDA

Thanks for contributing.

## Before You Start

- Search existing issues before opening a new one.
- For larger changes, open an issue first to align on approach.
- Keep pull requests focused and small when possible.

## Development Setup

1. Clone the repository.
2. Create a `.env` file from `.env.example`.
3. Install development dependencies:
   ```bash
   pip install -r requirements/dev.txt
   ```
4. Run locally (Docker or `flask --app autoapp.py run`).

## Pull Request Checklist

- [ ] Code changes are scoped to the stated goal.
- [ ] Linting passes.
- [ ] Type checks pass.
- [ ] Tests pass or rationale is provided.
- [ ] README/docs are updated when behavior or setup changes.

## Local Quality Checks

```bash
ruff check openvida
mypy openvida
pytest
```

## Coding Style

- Follow existing project style and naming conventions.
- Prefer clear, maintainable code over clever patterns.
- Avoid unrelated refactors in feature/fix PRs.

## Commit Messages

Use clear, imperative messages. Example:

- `Fix document URL history handling`
- `Improve resources page layout`

## Reporting Bugs

Please include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, Docker/non-Docker)

## Security

Do not disclose vulnerabilities publicly. See `SECURITY.md` for reporting guidance.
