import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from log_x import log_arbiter

logger = log_arbiter(__name__)


LATEX_COMPILER = Environment(
    block_start_string=r"\BLOCK{",
    block_end_string="}",
    variable_start_string=r"\VAR{",
    variable_end_string="}",
    comment_start_string=r"\#{",
    comment_end_string="}",
    line_statement_prefix="%%",
    line_comment_prefix="%#",
    trim_blocks=True,
    autoescape=False,
)


def compile_latex(resume_data: dict, template_dir: str, output_dir: str) -> None:
    """
    Compile latex templates into tex files.

    This function takes a directory of latex templates and a dictionary of data, and generates tex files from the templates and data. The generated files are placed in the specified output directory, which is created if it does not exist.

    Args:
        resume_data: A dictionary of data to use when rendering the templates.
        template_dir: A string path to the directory containing the latex templates.
        output_dir: A string path to the directory where the generated tex files should be placed.
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        LATEX_COMPILER.loader = FileSystemLoader(template_dir)

        template_files = [
            file_name
            for file_name in listdir(template_dir)
            if isfile(join(template_dir, file_name))
        ]

        for template_file in template_files:
            try:
                template = LATEX_COMPILER.get_template(template_file)
                rendered_tex = template.render(resume_data)
                with (output_dir / template_file).open("w") as file:
                    file.write(rendered_tex)
                logger.debug(f"Generated: {template_file}")
            except Exception as ex:
                logger.error(ex)

        logger.info(f"Generated/Updated {len(template_files)} files in: {output_dir}")
    except Exception as ex:
        logger.error(ex)


if __name__ == "__main__":
    logger.info(f"Hello from compiler.py please run main.py to start the script")
