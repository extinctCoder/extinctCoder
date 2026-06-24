# Use this for your own profile

This repo is a clean, self-updating GitHub **profile README** plus a YAML→LaTeX **résumé builder**. Here's how to make it yours.

## 1. Fork & rename

GitHub renders `README.md` on your profile only when the repo name **equals your username**. So:

1. Fork this repo (or "Use this template" if enabled).
2. Rename the fork to **exactly your GitHub username** (Settings → Repository name).

## 2. Edit your data — `resume.yml`

`resume.yml` (repo root) is the single source of truth for both the résumé PDF and the README projects list. Replace its contents with yours. Your editor validates it live against `resume.schema.json`, so it'll flag typos and missing fields.

- Mark any project you want shown on the profile with `featured: true`.
- A project with a `url` becomes a link in the README; without one it shows as plain text.

## 3. Set the two per-user values

Almost everything auto-detects your username (`GITHUB_REPOSITORY_OWNER` in CI). Only two values need editing — each is a single, clearly-commented line at the top of its workflow:

| File | Line to change | What it is |
|---|---|---|
| `.github/workflows/latest_blogs.yml` | `BLOG_FEED:` | your blog/RSS feed URL (or remove this workflow if you don't blog) |
| `.github/workflows/resume_builder.yml` | `PDF_NAME:` | base filename for the generated PDF (no extension) |

For **local** runs of the OSS section, `readme/oss.py` falls back to a hardcoded username — set `GITHUB_REPOSITORY_OWNER` in your shell, or edit the fallback. In CI it's automatic.

## 4. Rewrite the README content

`README.md` is hand-written (the parts between the `<!-- ... -->` markers are auto-filled). Edit:

- the intro, headings, and "how I work" text to your voice;
- the **Résumé button URL** in the first line — it points at `raw.githubusercontent.com/<user>/<repo>/master/<PDF_NAME>.pdf`, so update the username and PDF name.

Leave the marker blocks (`BLOG-POST-LIST`, `PROJECTS`, `OSS`) — the workflows fill them.

## 5. License & metadata (optional)

- `LICENSE` — update the copyright name.
- `pyproject.toml` `[project].name` — rename if you like.

## 6. Enable & run

1. Enable Actions on your fork (Actions tab → enable).
2. Trigger each workflow once via **Run workflow** (or just push):
   - **Résumé Builder** → renders + compiles the PDF, commits it to the repo root.
   - **README Projects** → fills the projects list from `resume.yml`.
   - **Open-Source Contributions** → fills your recent external PRs.
   - **Latest Blog Posts** → fills your latest posts.

After that they run on their own (résumé on change, the rest on a daily schedule).

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

make build     # render LaTeX templates -> resume/output/
make readme    # refresh the README projects list
make test      # run the test suite
make lint      # ruff lint + format check
```

> **Note:** the PDF is only compiled in CI (it needs a LaTeX install). Locally, `make build` produces the `.tex` files; GitHub compiles them to PDF.
