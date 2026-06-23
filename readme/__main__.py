from pathlib import Path

from yaml import safe_load

from .logger import log_arbiter

logger = log_arbiter(__name__)

# readme/__main__.py -> repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
RESUME_YML = REPO_ROOT / "resume.yml"
README = REPO_ROOT / "README.md"

START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"
HEADING = "### 🛠️ things I've built"


def render_block(projects: list) -> str:
    """Render featured projects as a comma-separated, linked list.

    Returns the markdown that goes *between* the PROJECTS markers (empty
    string when nothing is featured, so no orphan heading is shown).
    """
    featured = [p for p in projects if p.get("featured")]
    if not featured:
        return ""

    items = []
    for project in featured:
        title = project["title"]
        url = project.get("url")
        items.append(f"[{title}]({url})" if url else title)

    return f"\n\n---\n\n{HEADING}\n\n{', '.join(items)}\n"


def main():
    data = safe_load(RESUME_YML.read_text(encoding="utf-8"))
    projects = (data.get("project") or {}).get("projects", [])

    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise SystemExit(f"PROJECTS markers not found in {README}")

    before = readme.split(START)[0]
    after = readme.split(END)[1]
    readme = f"{before}{START}{render_block(projects)}{END}{after}"

    README.write_text(readme, encoding="utf-8")
    count = sum(1 for p in projects if p.get("featured"))
    logger.info(f"Updated README — {count} featured project(s)")


if __name__ == "__main__":
    main()
