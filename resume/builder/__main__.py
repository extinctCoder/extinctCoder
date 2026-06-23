from pathlib import Path

from click import command, option
from yaml import safe_load

from .compiler import compile_latex
from .logger import log_arbiter

logger = log_arbiter(__name__)

# resume/builder/__main__.py -> resume/ (package) -> repo root
PACKAGE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_DIR.parent


@command()
@option(
    "--resume",
    "-r",
    default=str(REPO_ROOT / "resume.yml"),
    help="location of resume.yml file",
)
@option(
    "--template",
    "-t",
    default=str(PACKAGE_DIR / "templates"),
    help="LaTeX TEMPLATE directory",
)
@option(
    "--output",
    "-o",
    default=str(PACKAGE_DIR / "output"),
    help="LaTeX OUTPUT directory",
)
def main(resume: str, template: str, output: str):
    """Render the LaTeX templates from resume.yml. Builds every run."""
    resume_path = Path(resume).resolve()
    if not resume_path.is_file():
        raise SystemExit(f"resume file not found: {resume}")

    with open(resume_path, "r", encoding="utf-8") as file:
        resume_data = safe_load(file)
    logger.info(f"Loaded resume data from {resume_path}")

    compile_latex(resume_data=resume_data, template_dir=template, output_dir=output)
    logger.info(f"Done — rendered LaTeX into {output}")


if __name__ == "__main__":
    main()
