# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working rules (read first)

1. **Do not edit anything before asking.** Never modify files on your own initiative — always ask and get explicit approval first.
2. **Always check the code before saying anything. No assumptions, no hallucination.** Read the relevant files and verify against the actual code before answering. If something is unverified or unknown, say so rather than guessing.
3. **Discuss and lock the approach before any implementation.** Talk through everything first, agree on the plan, and lock it down. By default, hand me the code to apply myself — do not edit the files unless I explicitly say to implement.

## What this repo is

This is the GitHub profile repository for `extinctCoder` (username == repo name, so `README.md` renders on the GitHub profile page). It serves two purposes:

1. **Resume generator** — a Python pipeline that renders a single source of truth (`resume.yml`) through Jinja2-templated LaTeX into a compiled PDF (`Sabbir_Ahmed_Shourov_resume.pdf`).
2. **Profile decoration** — scheduled GitHub Actions that regenerate the profile README's activity feed, blog posts, language stack, and 3D contribution graphs. These are third-party actions; their output files (`README.md`, `profile-3d-contrib/`, `stack.yml`, etc.) are machine-generated and committed by bots — do not hand-edit them.

## Resume pipeline architecture

The data flows: `resume.yml` → (Python renders) → `latex/*.tex` → (latexmk compiles) → `Sabbir_Ahmed_Shourov_resume.pdf`.

- **`resume.yml`** is the only file a human edits to change resume content. All resume data (links, skills, experience, projects, education) lives here.
- **`templates/*.tex`** are Jinja2 templates. **`latex/*.tex`** are the rendered outputs and are committed — they have identical filenames to `templates/`. Never edit `latex/` by hand; edit the template and re-run the generator.
- **`scripts/`** is the generator, run from inside the `scripts/` directory so its default relative paths (`../resume.yml`, `../templates`, `../latex`) resolve:
  - `main.py` — Click CLI entry point. Orchestrates the SHA-based change check and triggers compilation.
  - `compiler.py` — `compile_latex()` renders every file in `templates/` to `latex/` using a Jinja2 `Environment` configured with **LaTeX-safe delimiters** (`\BLOCK{...}`, `\VAR{...}`, `\#{...}`, `%%` line statements) instead of the default `{{ }}`/`{% %}`, which collide with LaTeX syntax.
  - `utils.py` — `read_sha()`/`update_sha()` implement change detection via GitPython.
  - `log_x.py` — `log_arbiter()` factory for module-level stdout loggers.

### SHA-based change detection

`main.py` only recompiles when `resume.yml` content has changed. It compares the `sha` field stored inside `resume.yml` against the previous commit's SHA of that file (`git log -n 1 --skip 1` of `resume.yml`). On change, it writes the new SHA back into `resume.yml` and recompiles. This is why the CI workflow commits `resume.yml` back after a build.

When editing the Jinja2 environment, template delimiters, or LaTeX structure (e.g. which `\input{}` files `templates/resume.tex` pulls in), keep `templates/` and the rendered `latex/` consistent — the compile step in CI uses `latex/resume.tex` as the root file.

## Commands

Dependencies are managed with **pipenv** (Python 3.12). There is no test suite, lint config, or build script beyond the steps below.

```bash
# Install dependencies
pipenv install

# Render templates -> latex/ (must run from scripts/ for default paths to resolve)
cd scripts && pipenv run python main.py

# Override default paths if needed
python main.py --resume ../resume.yml --template ../templates --output ../latex

# Compile the PDF locally (requires a LaTeX distribution with latexmk)
cd latex && latexmk -pdf -interaction=nonstopmode -jobname=Sabbir_Ahmed_Shourov_resume resume.tex
```

## CI / automation

GitHub Actions in `.github/workflows/` run on cron schedules (no PR-triggered CI):

- **`resume.yml`** — daily; two jobs. `BuildLatexTemplate` runs the Python generator and commits regenerated `latex/`; `CompileUploadLatex` then compiles `latex/resume.tex` to PDF (via `dante-ev/latex-action`) and commits the PDF to repo root.
- **`update-readme.yml`**, **`blog-post-workflow.yml`**, **`profile-stack.yml`**, **`profile-3d.yml`** — periodically regenerate README sections / profile assets using third-party actions. These produce the bot commits ("generated", "Update README with the recent activity") in the history.
