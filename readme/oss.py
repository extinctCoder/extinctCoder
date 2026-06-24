import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from .logger import log_arbiter

logger = log_arbiter(__name__)

# Auto-detected from the repository owner in CI; the fallback is used for local runs.
USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "extinctCoder")
MAX_ITEMS = 5

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"

START = "<!-- OSS:START -->"
END = "<!-- OSS:END -->"
HEADING = "### 🌍 out in the open"


def _api_url() -> str:
    # PRs authored by USER in repositories USER does not own.
    query = f"author:{USER} type:pr -user:{USER}"
    params = urllib.parse.urlencode(
        {"q": query, "sort": "updated", "order": "desc", "per_page": MAX_ITEMS}
    )
    return f"https://api.github.com/search/issues?{params}"


def fetch_contributions(token: str | None = None) -> list:
    request = urllib.request.Request(
        _api_url(),
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER},
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)

    items = []
    for item in data.get("items", []):
        repo = item["repository_url"].split("/repos/")[-1]
        items.append(
            {
                "repo": repo,
                "number": item["number"],
                "url": item["html_url"],
                "title": item["title"],
            }
        )
    return items


def render_block(items: list) -> str:
    """Render up to MAX_ITEMS contributions as a bulleted list (empty when none)."""
    items = items[:MAX_ITEMS]
    if not items:
        return ""
    lines = [
        f"- [{i['repo']}](https://github.com/{i['repo']}) [#{i['number']}]({i['url']}) — {i['title']}"
        for i in items
    ]
    return f"\n\n---\n\n{HEADING}\n\n" + "\n".join(lines) + "\n"


def main():
    try:
        items = fetch_contributions(os.environ.get("GITHUB_TOKEN"))
    except Exception as ex:
        # Leave the README untouched on a transient API/network failure.
        logger.error(f"Failed to fetch contributions: {ex}")
        return

    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise SystemExit(f"OSS markers not found in {README}")

    before = readme.split(START)[0]
    after = readme.split(END)[1]
    README.write_text(f"{before}{START}{render_block(items)}{END}{after}", encoding="utf-8")
    logger.info(f"Updated README — {len(items)} OSS contribution(s)")


if __name__ == "__main__":
    main()
