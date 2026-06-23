# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working rules (read first)

1. **Do not edit anything before asking.** Never modify files on your own initiative — always ask and get explicit approval first.
2. **Always check the code before saying anything. No assumptions, no hallucination.** Read the relevant files and verify against the actual code before answering. If something is unverified or unknown, say so rather than guessing.
3. **Discuss and lock the approach before any implementation.** Talk through everything first, agree on the plan, and lock it down. By default, hand me the code to apply myself — do not edit the files unless I explicitly say to implement.

## What this repo is

This is the GitHub profile repository for `extinctCoder` (username == repo name, so `README.md` renders on the GitHub profile page). It serves two purposes:

1. **Résumé generator** — a Python package (`resume/builder/`) that renders a single source of truth (`resume/resume.yml`) through Jinja2-templated LaTeX into a compiled PDF (`Sabbir_Ahmed_Shourov_resume.pdf` at repo root).
2. **Profile README** — `README.md` is hand-written and intentionally minimal. One scheduled GitHub Action (`latest_blogs.yml`) injects latest blog posts between the `<!-- BLOG-POST-LIST -->` markers; a parked `<!-- PROJECTS -->` marker block is reserved for a future projects pipeline.

## Résumé pipeline architecture

Everything for the résumé builder lives under `resume/`. Data flow: `resume/resume.yml` → (Python renders) → `resume/output/*.tex` → (latexmk compiles) → `Sabbir_Ahmed_Shourov_resume.pdf` at repo root.

- **`resume/resume.yml`** is the only file a human edits to change résumé content (links, skills, experience, projects, education).
- **`resume/templates/*.tex`** are the Jinja2 source templates. **`resume/output/*.tex`** are the rendered outputs — **git-ignored** and regenerated on every build. Never edit `output/` by hand; edit the template and re-run the builder.
- **`resume/builder/`** is a Python package, run from the repo root as `python -m resume.builder`. Default paths resolve from the package location (`PROJECT_DIR = resume/`), so no `cd` is needed:
  - `__main__.py` — Click CLI entry point. Loads `resume.yml` and triggers compilation on every run (no change detection); defaults point at `resume/resume.yml`, `resume/templates`, `resume/output`.
  - `compiler.py` — `compile_latex()` renders every file in `templates/` to `output/` using a Jinja2 `Environment` with **LaTeX-safe delimiters** (`\BLOCK{...}`, `\VAR{...}`, `\#{...}`, `%%` line statements) instead of the default `{{ }}`/`{% %}`, which collide with LaTeX syntax.
  - `logger.py` — `log_arbiter()` factory for module-level stdout loggers.

When editing the Jinja2 environment, template delimiters, or which `\input{}` files `resume/templates/resume.tex` pulls in, keep `templates/` and the rendered `output/` consistent — CI compiles `resume/output/resume.tex` as the root file.

## Commands

Dependencies: plain `pip` + `requirements.txt` (Python 3.12). No test suite, lint config, or build script beyond the steps below.

```bash
# Set up environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Render templates -> resume/output/ (run from repo root)
python -m resume.builder

# Override default paths if needed
python -m resume.builder --resume resume/resume.yml --template resume/templates --output resume/output

# Compile the PDF locally (requires a LaTeX distribution with latexmk)
cd resume/output && latexmk -pdf -interaction=nonstopmode -jobname=Sabbir_Ahmed_Shourov_resume resume.tex
```

## CI / automation

GitHub Actions in `.github/workflows/` run on cron schedules (no PR-triggered CI):

- **`resume_builder.yml`** — daily; a single job: installs `requirements.txt`, runs `python -m resume.builder` (renders the `.tex`), compiles `resume/output/resume.tex` to PDF (via `dante-ev/latex-action`), moves the PDF to repo root, and commits the PDF. The PDF is only built in CI — there is no local LaTeX engine.
- **`latest_blogs.yml`** — pulls latest posts from the blog feed (`extinctcoder.github.io/feed.xml`) into `README.md`'s `<!-- BLOG-POST-LIST -->` markers.
