import json

import readme.oss as oss
from readme.oss import MAX_ITEMS, render_block


def test_empty_returns_empty():
    assert render_block([]) == ""


def test_renders_repo_and_pr_links():
    items = [{"repo": "org/proj", "number": 14, "url": "https://x.dev/pr/14", "title": "Fix bug"}]
    block = render_block(items)
    assert "[org/proj](https://github.com/org/proj)" in block  # repo -> repo
    assert "[#14](https://x.dev/pr/14)" in block  # number -> PR
    assert "— Fix bug" in block  # commit message as plain text
    assert "out in the open" in block


def test_multiple_items_each_on_a_line():
    items = [
        {"repo": "a/b", "number": 1, "url": "https://a", "title": "One"},
        {"repo": "c/d", "number": 2, "url": "https://c", "title": "Two"},
    ]
    assert render_block(items).count("\n- ") == 2


def test_caps_at_max_items():
    items = [
        {"repo": f"o/r{n}", "number": n, "url": f"https://x/{n}", "title": f"t{n}"}
        for n in range(MAX_ITEMS + 5)
    ]
    assert render_block(items).count("\n- ") == MAX_ITEMS


class _FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self, *args):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_fetch_parses_repo_from_api(monkeypatch):
    payload = {
        "items": [
            {
                "repository_url": "https://api.github.com/repos/org/proj",
                "number": 7,
                "html_url": "https://github.com/org/proj/pull/7",
                "title": "Add thing",
            }
        ]
    }
    monkeypatch.setattr(oss.urllib.request, "urlopen", lambda *a, **k: _FakeResponse(payload))
    assert oss.fetch_contributions() == [
        {
            "repo": "org/proj",
            "number": 7,
            "url": "https://github.com/org/proj/pull/7",
            "title": "Add thing",
        }
    ]


_OSS_README = "top\n<!-- OSS:START -->\n<!-- OSS:END -->\nbottom\n"


def test_main_injects_block(tmp_path, monkeypatch):
    readme = tmp_path / "README.md"
    readme.write_text(_OSS_README, encoding="utf-8")
    monkeypatch.setattr(oss, "README", readme)
    monkeypatch.setattr(
        oss,
        "fetch_contributions",
        lambda token=None: [
            {"repo": "org/proj", "number": 7, "url": "https://x/7", "title": "Add thing"}
        ],
    )
    oss.main()
    out = readme.read_text(encoding="utf-8")
    assert "[org/proj](https://github.com/org/proj) [#7](https://x/7) — Add thing" in out
    assert out.startswith("top") and out.rstrip().endswith("bottom")


def test_main_leaves_readme_untouched_on_failure(tmp_path, monkeypatch):
    readme = tmp_path / "README.md"
    readme.write_text(_OSS_README, encoding="utf-8")
    monkeypatch.setattr(oss, "README", readme)

    def boom(token=None):
        raise RuntimeError("api down")

    monkeypatch.setattr(oss, "fetch_contributions", boom)
    oss.main()
    assert readme.read_text(encoding="utf-8") == _OSS_README  # unchanged
