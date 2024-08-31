from pathlib import Path

import click
from git import Repo
from log_x import log_arbiter
from yaml import dump, safe_load

logger = log_arbiter(__name__)


def read_sha(resume_path: Path):
    """
    Gets the latest commit SHA of the given file in the local repository.

    Args:
        resume_path (Path): The path to the resume.yml file.

    Returns:
        str: The latest commit SHA of the file.
    """
    try:
        repo = Repo(resume_path.parent, search_parent_directories=True)
        relative_path = resume_path.relative_to(repo.working_tree_dir)
        return repo.git.log(
            "-n", "1", "--skip", "1", "--pretty=format:%h", "--", str(relative_path)
        )
    except Exception as ex:
        logger.error(ex)


def update_sha(resume_data: dict, sha: str, resume_path: Path) -> None:
    """
    Stores the latest SHA in resume.yml

    Parameters
    ----------
    resume_data : dict
        The loaded yaml data from resume.yml
    sha : str
        The latest SHA of the current branch
    resume_path : Path
        The path to the resume.yml file
    """
    logger.debug("Generating SHA for resume.yml")
    resume_data["sha"] = sha
    logger.debug(f"Storing latest SHA {sha} in {resume_path}")
    with resume_path.open("w", encoding="utf-8") as file:
        dump(
            resume_data,
            file,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
    logger.info(f"Updated or Stored {resume_path} with SHA {sha}")


if __name__ == "__main__":
    logger.info(f"Hello from utils.py please run main.py to start the script")
