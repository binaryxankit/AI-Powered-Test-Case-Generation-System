# Contributing

Thanks for your interest in **TestForge AI**! This project is an MVP
and we welcome improvements that keep the scope focused, the code
clean, and the developer experience great.

## Ground rules

1. **Keep it small.** A focused, atomic change is easier to review
   than a 500-line drop.
2. **Type everything.** Python uses type hints everywhere; TypeScript
   is in strict mode. Avoid `any` and bare `object` types.
3. **One thing per commit.** Squash local noise before opening a PR.
4. **No secrets.** Never commit API keys, tokens, or real database
   URLs. Use `.env.example` for new variables.

## Development setup

1. Fork & clone the repository.
2. Follow the setup steps in `README.md` to install dependencies.
3. Create a new branch: `git checkout -b feat/short-description`.

## Backend workflow

* Run the test suite before opening a PR:

  ```bash
  make test
  ```

* Add a test alongside every non-trivial change. New features without
  tests will be asked to add them.
* New database columns **must** ship as an Alembic migration:

  ```bash
  make migration name="add_users_table"
  ```

  Then edit the generated file to remove the `op.create_table`
  autofill noise and keep only the meaningful diff.

* All public functions and methods take type hints. New service
  classes should expose their collaborators through `__init__` to
  make them easy to stub in tests.

## Frontend workflow

* Run typecheck and lint before pushing:

  ```bash
  make typecheck
  make lint
  ```

* Prefer Shadcn UI primitives (`components/ui/*`) and the existing
  copy/markdown utilities over one-off implementations.
* Use `"use client"` only on files that actually need it. Server
  components are cheaper and easier to reason about.
* For new pages, add a `layout.tsx` next to the page that exports a
  `Metadata` object for SEO.

## Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body — what & why, not how>

<footer — references, breaking changes>
```

Valid types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`,
`perf`, `ci`, `build`, `style`.

Examples from this repo:

```
feat(backend): add retry logic to Gemini client
fix(backend): graceful startup without database
test(frontend): add hook unit tests
```

## Pull requests

* Reference the issue you are addressing in the PR body.
* Include a screenshot or short screen recording for any UI change.
* Keep PRs under ~400 lines of diff when possible. Split bigger
  work into stacked PRs.

## Reporting issues

Use GitHub issues. For security problems, email the maintainers
directly — do **not** open a public issue.
