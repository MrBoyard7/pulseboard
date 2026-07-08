# Contributing to PulseBoard

Thanks for considering a contribution! This project follows a fairly standard
GitHub flow.

## Getting started

1. Fork the repository and clone your fork.
2. Follow the local setup instructions in the [README](README.md).
3. Create a branch: `git checkout -b feature/short-description`.

## Development workflow

- **Backend**: format with `black`, sort imports with `isort`, lint with
  `flake8`, and type-check with `mypy` before opening a PR. Run `pytest` and
  keep coverage from regressing.
- **Frontend**: run `npm run lint` and `npm run test`. Run `npm run build` to
  confirm the production bundle compiles cleanly.
- Keep commits focused and write descriptive commit messages
  (e.g. `fix(api): correct timeline health calculation for closed projects`).

## Pull requests

- Describe *what* changed and *why*, not just *how*.
- Link any related issue.
- Make sure CI is green before requesting review.
- Small, focused PRs are easier to review than large ones — feel free to
  split up bigger changes.

## Reporting bugs

Open an issue with steps to reproduce, expected vs. actual behavior, and
relevant logs. For security issues, see [SECURITY.md](SECURITY.md) instead of
filing a public issue.

## Code of conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Please read
it before participating.
