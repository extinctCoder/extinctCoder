import json
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent


def _validator() -> Draft7Validator:
    schema = json.loads((ROOT / "resume.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


def _resume_data() -> dict:
    return yaml.safe_load((ROOT / "resume.yml").read_text(encoding="utf-8"))


def test_resume_yml_matches_schema():
    errors = list(_validator().iter_errors(_resume_data()))
    assert not errors, [e.message for e in errors]


def test_unknown_top_level_field_rejected():
    data = _resume_data()
    data["unexpected_field"] = True
    assert list(_validator().iter_errors(data))


def test_missing_required_name_rejected():
    data = _resume_data()
    del data["name"]
    assert list(_validator().iter_errors(data))


def test_links_must_be_an_array():
    data = _resume_data()
    data["links"] = "not-an-array"
    assert list(_validator().iter_errors(data))


def test_featured_must_be_boolean():
    data = _resume_data()
    data["project"]["projects"][0]["featured"] = "yes"
    assert list(_validator().iter_errors(data))


def test_experience_end_date_accepts_null():
    data = _resume_data()
    data["pro_experience"]["experiences"][0]["end_date"] = None
    assert not list(_validator().iter_errors(data))
