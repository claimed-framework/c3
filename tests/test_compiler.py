import os
import subprocess
import pytest
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from src.c3.utils import convert_notebook, increase_image_version, get_image_version
from src.c3.pythonscript import Pythonscript

TEST_NOTEBOOK_PATH = 'example_notebook.ipynb'
TEST_SCRIPT_PATH = 'example_script.py'
DUMMY_REPO = 'test'

test_convert_notebook_input = [
    (
        TEST_NOTEBOOK_PATH,
        ['input_path', 'batch_size', 'debug', 'output_path']
    )
]

@pytest.mark.parametrize(
    "notebook_path, env_values",
    test_convert_notebook_input,
)
def test_convert_notebook(
        notebook_path: str,
        env_values: List,
):
    # convert notebook
    script_path = convert_notebook(notebook_path)

    assert os.path.isfile(script_path), f"Error! No file {script_path}"

    # check if script runs with errors
    for env in env_values:
        os.environ[env] = '0'
    subprocess.run(['python', script_path], check=True)

    # check if converted script is processable for create_operator
    py = Pythonscript(script_path)
    name = py.get_name()
    assert isinstance(name, str), "Name is not a string."
    description = py.get_description()
    assert isinstance(description, str), "Description is not a string."
    inputs = py.get_inputs()
    assert isinstance(inputs, dict), "Inputs is not a dict."
    outputs = py.get_outputs()
    assert isinstance(outputs, dict), "Ouputs is not a dict."
    requirements = py.get_requirements()
    assert isinstance(requirements, list), "Requirements is not a list."

    # remove temporary file
    os.remove(script_path)


test_increase_version_input = [
    ('0.1', '0.2'),
    ('2.1.13', '2.1.14'),
    ('0.1beta', '0.1beta.1'),
    ('0.1beta.1', '0.1beta.2'),
]


@pytest.mark.parametrize(
    "last_version, expected_version",
    test_increase_version_input,
)
def test_create_operator(
        last_version: str,
        expected_version: str,
):
    new_version = increase_image_version(last_version)
    assert new_version == expected_version, \
        f"Mismatch between new version {new_version} and expected version {expected_version}"


test_create_operator_input = [
    (
        TEST_NOTEBOOK_PATH,
        DUMMY_REPO,
        [],
    ),
    (
        TEST_SCRIPT_PATH,
        DUMMY_REPO,
        [TEST_NOTEBOOK_PATH],
    )
]
@pytest.mark.parametrize(
    "file_path, repository, args",
    test_create_operator_input,
)
def test_create_operator(
        file_path: str,
        repository: str,
        args: List,
):
    subprocess.run(['python', '../src/c3/create_operator.py', file_path, *args, '-r', repository], check=True)

    file = Path(file_path)
    file.with_suffix('.yaml').unlink()
    file.with_suffix('.job.yaml').unlink()