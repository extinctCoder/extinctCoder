from click.testing import CliRunner

from resume.builder.__main__ import main


def test_cli_errors_on_missing_resume(tmp_path):
    result = CliRunner().invoke(main, ["--resume", str(tmp_path / "nope.yml")])
    assert result.exit_code != 0


def test_cli_renders_to_output(tmp_path):
    resume = tmp_path / "resume.yml"
    resume.write_text("name: Tester\n", encoding="utf-8")
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "heading.tex").write_text(r"\VAR{name}", encoding="utf-8")
    output = tmp_path / "output"

    result = CliRunner().invoke(
        main,
        ["--resume", str(resume), "--template", str(templates), "--output", str(output)],
    )
    assert result.exit_code == 0, result.output
    assert (output / "heading.tex").read_text(encoding="utf-8") == "Tester"
