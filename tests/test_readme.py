import readme.__main__ as rm
from readme.__main__ import render_block

README_TEMPLATE = "before\n<!-- PROJECTS:START -->\n<!-- PROJECTS:END -->\nafter\n"


def test_no_featured_returns_empty():
    projects = [{"title": "A"}, {"title": "B", "featured": False}]
    assert render_block(projects) == ""


def test_empty_list_returns_empty():
    assert render_block([]) == ""


def test_featured_with_url_is_linked():
    block = render_block([{"title": "Site", "url": "https://x.dev", "featured": True}])
    assert "[Site](https://x.dev)" in block
    assert "things I've built" in block


def test_featured_without_url_is_plain_text():
    block = render_block([{"title": "Internal", "url": None, "featured": True}])
    assert "Internal" in block
    assert "[Internal]" not in block


def test_multiple_featured_are_comma_joined_in_order():
    block = render_block(
        [
            {"title": "A", "url": "https://a", "featured": True},
            {"title": "B", "featured": True},
        ]
    )
    assert "[A](https://a), B" in block


def _setup(tmp_path, monkeypatch, resume_text):
    resume = tmp_path / "resume.yml"
    resume.write_text(resume_text, encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text(README_TEMPLATE, encoding="utf-8")
    monkeypatch.setattr(rm, "RESUME_YML", resume)
    monkeypatch.setattr(rm, "README", readme)
    return readme


def test_main_injects_block_and_preserves_surroundings(tmp_path, monkeypatch):
    resume = "project:\n  projects:\n    - title: X\n      url: https://x.dev\n      featured: true\n"
    readme = _setup(tmp_path, monkeypatch, resume)
    rm.main()
    out = readme.read_text(encoding="utf-8")
    assert out.startswith("before")
    assert out.rstrip().endswith("after")
    assert "[X](https://x.dev)" in out
    assert out.count(rm.START) == 1 and out.count(rm.END) == 1


def test_main_is_idempotent(tmp_path, monkeypatch):
    resume = "project:\n  projects:\n    - title: X\n      url: https://x.dev\n      featured: true\n"
    readme = _setup(tmp_path, monkeypatch, resume)
    rm.main()
    first = readme.read_text(encoding="utf-8")
    rm.main()
    assert readme.read_text(encoding="utf-8") == first


def test_main_no_featured_leaves_markers_empty(tmp_path, monkeypatch):
    resume = "project:\n  projects:\n    - title: X\n      featured: false\n"
    readme = _setup(tmp_path, monkeypatch, resume)
    rm.main()
    out = readme.read_text(encoding="utf-8")
    assert "things I've built" not in out
    assert f"{rm.START}{rm.END}" in out
