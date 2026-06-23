from resume.builder.compiler import compile_latex


def _render(tmp_path, name, template, data):
    templates = tmp_path / "templates"
    templates.mkdir(exist_ok=True)
    (templates / name).write_text(template, encoding="utf-8")
    output = tmp_path / "output"
    compile_latex(data, str(templates), str(output))
    return (output / name).read_text(encoding="utf-8")


def test_var_substitution(tmp_path):
    assert _render(tmp_path, "s.tex", r"Hello \VAR{name}", {"name": "World"}) == "Hello World"


def test_for_loop(tmp_path):
    out = _render(
        tmp_path, "l.tex", r"\BLOCK{for x in items}\VAR{x} \BLOCK{endfor}", {"items": ["a", "b", "c"]}
    )
    assert "a b c" in out


def test_if_true_branch(tmp_path):
    out = _render(tmp_path, "c.tex", r"\BLOCK{if show}YES\BLOCK{else}NO\BLOCK{endif}", {"show": True})
    assert out.strip() == "YES"


def test_if_false_branch(tmp_path):
    out = _render(tmp_path, "c.tex", r"\BLOCK{if show}YES\BLOCK{else}NO\BLOCK{endif}", {"show": False})
    assert out.strip() == "NO"


def test_default_jinja_braces_left_literal(tmp_path):
    # LaTeX-safe delimiters: {{ }} must NOT be treated as a variable.
    out = _render(tmp_path, "d.tex", "keep {{ this }} literal", {"this": "X"})
    assert out == "keep {{ this }} literal"


def test_output_dir_is_created(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "a.tex").write_text("static", encoding="utf-8")
    output = tmp_path / "nested" / "output"
    compile_latex({}, str(templates), str(output))
    assert (output / "a.tex").exists()


def test_all_templates_are_rendered(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "a.tex").write_text("A", encoding="utf-8")
    (templates / "b.tex").write_text("B", encoding="utf-8")
    output = tmp_path / "output"
    compile_latex({}, str(templates), str(output))
    assert (output / "a.tex").exists() and (output / "b.tex").exists()
