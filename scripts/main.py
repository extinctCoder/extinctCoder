from pathlib import Path

from click import command, option
from compiler import compile_latex
from log_x import log_arbiter
from utils import read_sha, update_sha
from yaml import safe_load

logger = log_arbiter(__name__)


@command
@option("--resume", "-r", default="../resume.yml", help="location of resume.yml file")
@option("--template", "-t", default="../templates", help="Latex TEMPLATE directory")
@option("--output", "-o", default="../latex", help="Latex OUTPUT directory")
def main(resume: str, template: str, output: str):
    try:
        resume_path = Path(resume).resolve()
        if not resume_path.is_file():
            raise Exception(f"RESUME FILE not found at {resume}")
        with open(resume_path, "r", encoding="utf-8") as file:
            resume_data = safe_load(file)
            logger.debug(f"resume data loaded from {resume}")
        sha = read_sha(resume_path)
        if not resume_data["sha"] or resume_data["sha"] != sha:
            logger.info("RESUME IS OUT-OF-DATE or FIRST RUN")
            update_sha(resume_data=resume_data, sha=sha, resume_path=resume_path)
            logger.debug("Starting LaTeX compiler to compile resume")
            compile_latex(
                resume_data=resume_data, template_dir=template, output_dir=output
            )
            logger.info("RESUME COMPILE COMPILED SUCCESSFULLY")
            return
        logger.info("RESUME IS UP-TO-DATE")
    except Exception as ex:
        logger.error(ex)
    finally:
        logger.debug("Shutting down resume builder")


if __name__ == "__main__":
    logger.info("Starting resume generator...")
    main()
