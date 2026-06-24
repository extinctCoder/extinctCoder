# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working rules (read first)

1. **Do not edit anything before asking.** Never modify files on your own initiative — always ask and get explicit approval first.
2. **Always check the code before saying anything. No assumptions, no hallucination.** Read the relevant files and verify against the actual code before answering. If something is unverified or unknown, say so rather than guessing.
3. **Discuss and lock the approach before any implementation.** Talk through everything first, agree on the plan, and lock it down. By default, hand me the code to apply myself — do not edit the files unless I explicitly say to implement.

## What this repo is

This is the GitHub profile repository for `extinctCoder` (username == repo name, so `README.md` renders on the GitHub profile page). It serves two purposes:

1. **Résumé generator** — a Python package (`resume/builder/`) that renders a single source of truth (`resume.yml`, at repo root) through Jinja2-templated LaTeX into a compiled PDF (`Sabbir_Ahmed_Shourov_resume.pdf` at repo root).
2. **Profile README** — `README.md` is hand-written and intentionally minimal. Three marker blocks are machine-filled: `latest_blogs.yml` → `<!-- BLOG-POST-LIST -->`, `python -m readme` → `<!-- PROJECTS -->` (featured projects), and `python -m readme.oss` → `<!-- OSS -->` (recent open-source PRs). See below.

`USAGE.md` explains how to fork and adapt this whole setup for another person's profile (the per-user values, what to edit, how to run it).

## Résumé pipeline architecture

`resume.yml` (the single source of truth) lives at the **repo root**, next to its `resume.schema.json` (validated live via the `# yaml-language-server` directive at the top of the file). Two independent packages read it.

Data flow: `resume.yml` → (`resume/builder` renders) → `resume/output/*.tex` → (latexmk compiles) → `Sabbir_Ahmed_Shourov_resume.pdf` at repo root.

- **`resume.yml`** (root) is the only file a human edits to change résumé content (links, skills, experience, projects, education).
- **`resume/templates/*.tex`** are the Jinja2 source templates. **`resume/output/*.tex`** are the rendered outputs — **git-ignored** and regenerated on every build. Never edit `output/` by hand; edit the template and re-run the builder.
- **`resume/builder/`** — the PDF builder package, run from repo root as `python -m resume.builder`. Paths resolve from the package: data from `REPO_ROOT/resume.yml`, templates/output from `resume/`. No `cd` needed.
  - `__main__.py` — Click CLI entry point. Loads `resume.yml` and renders on every run (no change detection).
  - `compiler.py` — `compile_latex()` renders every file in `templates/` to `output/` using a Jinja2 `Environment` with **LaTeX-safe delimiters** (`\BLOCK{...}`, `\VAR{...}`, `\#{...}`, `%%` line statements) instead of the default `{{ }}`/`{% %}`, which collide with LaTeX syntax.
  - `logger.py` — `log_arbiter()` factory for module-level stdout loggers.
- **`readme/`** — a separate, self-contained package (its own `logger.py`) with two README updaters:
  - `python -m readme` — reads the root `resume.yml`, takes every project marked `featured: true`, and writes a comma-separated linked list into the `<!-- PROJECTS -->` markers. Projects with a `url` are linked; others render as plain text.
  - `python -m readme.oss` — queries the GitHub Search API (stdlib `urllib`, no extra deps; uses `GITHUB_TOKEN` if set) for recent PRs authored by the user in repos they don't own, and writes them into the `<!-- OSS -->` markers. On API failure it logs and leaves the README untouched.

When editing the Jinja2 environment, template delimiters, or which `\input{}` files `resume/templates/resume.tex` pulls in, keep `templates/` and the rendered `output/` consistent — CI compiles `resume/output/resume.tex` as the root file.

## Commands

Everything lives in `pyproject.toml`: runtime deps in `[project.dependencies]`, dev tools (`pytest`, `jsonschema`, `ruff`) in the `dev` optional group, and ruff/pytest config under `[tool.*]`. Python 3.13. The repo installs as an **editable** package (`pip install -e .`) — editable is required so the `resume.yml`-at-root path logic (`REPO_ROOT = __file__/../..`) still resolves; a normal install would relocate the code and break it. A `Makefile` wraps the common tasks (`make venv` / `build` / `readme` / `test` / `lint` / `fmt`).

```bash
# Set up environment (editable install + dev tools)
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Render templates -> resume/output/ (run from repo root)
python -m resume.builder

# Update the README projects list from resume.yml (featured: true)
python -m readme

# Run the test suite
pytest -q

# Lint + format check (ruff)
ruff check . && ruff format --check .

# Override builder default paths if needed
python -m resume.builder --resume resume.yml --template resume/templates --output resume/output

# Compile the PDF locally (requires a LaTeX distribution with latexmk)
cd resume/output && latexmk -pdf -interaction=nonstopmode -jobname=Sabbir_Ahmed_Shourov_resume resume.tex
```

## CI / automation

GitHub Actions in `.github/workflows/`:

- **`resume_builder.yml`** — push to `resume.yml` / `resume/**` / `pyproject.toml` / the workflow, plus manual dispatch (no cron). Three staged jobs passing files via artifacts: **render** (`python -m resume.builder` → uploads `.tex`) → **compile** (`xu-cheng/latex-action` → PDF) → **publish** (downloads the PDF, commits it).
- **`readme_projects.yml`** — push to `resume.yml` / `readme/**` / the workflow, plus manual dispatch. Runs `python -m readme` and commits the refreshed `README.md`.
- **`latest_blogs.yml`** — scheduled; pulls latest posts from the blog feed (`extinctcoder.github.io/feed.xml`) into `README.md`'s `<!-- BLOG-POST-LIST -->` markers.
- **`oss_contributions.yml`** — scheduled (daily); runs `python -m readme.oss` to refresh recent open-source PRs in the `<!-- OSS -->` markers, then commits `README.md`.
- **`tests.yml`** — push to code / `resume.yml` / `tests/` / `pyproject.toml`; `pip install -e ".[dev]"`, then `ruff` (lint + format check), then `pytest` (unit tests for the builder + readme, plus schema validation of `resume.yml`).

Dependency hygiene is automated via `.github/dependabot.yml`, which opens weekly PRs to keep GitHub Actions and (via `pyproject.toml`) pip dependencies current.

All four workflows that commit to the repo (`resume_builder`, `readme_projects`, `latest_blogs`, `oss_contributions`) share a `concurrency: repo-writes` group, so they run one-at-a-time instead of racing on `git push`. The PDF is only built in CI — there is no local LaTeX engine.
