import json
import os

import pytest
from pytest_metadata.plugin import metadata_key

from number_analyzer import NumberAnalyzer

# Configs
VALID_CONFIG = {
    "categories": [
        {"label": "Prime", "rule": "prime"},
        {"label": "Even", "rule": "even"},
        {"label": "Odd", "rule": "odd"},
        {"label": "Div5", "rule": "lambda x: x % 5 == 0"}
    ]
}

EXPECTED_RESULTS = ['Odd',
                    'Prime, Even',
                    'Prime, Odd',
                    'Even',
                    'Prime, Odd, Div5',
                    'Even',
                    'Prime, Odd',
                    'Even',
                    'Odd',
                    'Even, Div5']

EXPECTED_RESULTS_DEBUG = {1: 'Odd',
                          2: 'Prime, Even',
                          3: 'Prime, Odd',
                          4: 'Even',
                          5: 'Prime, Odd, Div5',
                          6: 'Even',
                          7: 'Prime, Odd',
                          8: 'Even',
                          9: 'Odd',
                          10: 'Even, Div5'
                          }

VALID_CONFIG_FULL_DEFINITION = {
    "categories": [
        {"label": "Prime", "rule": "prime"},
        {"label": "Even", "rule": "even"},
        {"label": "Odd", "rule": "odd"},
        {"label": "Div7",
         "rule": """def div7(x):
    if x % 7:
        return False
    else:
        return True"""}
    ]
}

INVALID_CONFIG_FULL_DEFINITION = {
    "categories": [
        {"label": "Prime", "rule": "prime"},
        {"label": "Even", "rule": "even"},
        {"label": "Odd", "rule": "odd"},
        {"label": "Div7",
         "rule": """def div7(x):
    if x % :
        return False
    else:
        return True"""}
    ]
}

INVALID_CONFIG = {
    "categories": [
        {"label": "Prime", "rule": "prime"},
        {"label": "Even", "rule": "even"},
        {"label": "Odd", "rule": "odd"},
        {"label": "Div5",
         "rule": "lambda x: x % 5 == "}
    ]
}


# Utils
def create_config_file(base_dir, filename, config_data):
    file_path = os.path.join(base_dir, filename)
    with open(file_path, 'w') as f:
        json.dump(config_data, f)
    return file_path


# Fixtures
@pytest.fixture(scope="session")
def config_path():
    return os.path.abspath('config')


@pytest.fixture(scope="session", autouse=True)
def setup(config_path):
    os.makedirs(config_path, exist_ok=True)  # Ensure the directory exists

    test_data = {
        # Create all required config files
        'valid_config': create_config_file(config_path, 'valid_config.json', VALID_CONFIG),
        'valid_config_full_definition': create_config_file(config_path, 'valid_config_full_definition.json',
                                                           VALID_CONFIG_FULL_DEFINITION),
        'invalid_config_full_definition': create_config_file(config_path, 'invalid_config_full_definition.json',
                                                             INVALID_CONFIG_FULL_DEFINITION),
        'valid_config_path': create_config_file('./', 'valid_config_path.json', VALID_CONFIG),
        'invalid_config': create_config_file(config_path, 'invalid_config.json', INVALID_CONFIG),
    }
    invalid_json_file = os.path.join(config_path, 'invalid_json_config.json')
    with open(invalid_json_file, "w") as outfile:
        outfile.write('{"categories": [{"label": "Even","rule"= "even"}]}')
    test_data['invalid_json_config'] = invalid_json_file

    yield test_data

    # Cleanup after tests
    for file in test_data.values():
        if os.path.exists(file):
            os.remove(file)


@pytest.fixture(scope="module")
def valid_config_file(setup):
    return setup["valid_config"]


@pytest.fixture(scope="module")
def default_na(valid_config_file):
    return NumberAnalyzer(1, 10, config_file=valid_config_file)


@pytest.fixture(scope="module")
def valid_config_file_full_definition(setup):
    return setup["valid_config_full_definition"]


@pytest.fixture(scope="module")
def invalid_config_file_full_definition(setup):
    return setup["invalid_config_full_definition"]


@pytest.fixture(scope="module")
def valid_config_file_path(setup):
    return setup["valid_config_path"]


@pytest.fixture(scope="module")
def invalid_config_file(setup):
    return setup["invalid_config"]


@pytest.fixture(scope="module")
def invalid_json_config(setup):
    return setup["invalid_json_config"]


@pytest.fixture(scope="module")
def expected_results():
    return [EXPECTED_RESULTS, EXPECTED_RESULTS_DEBUG]


# Report
def pytest_html_report_title(report):
    report.title = "Number Analyzer Pytest Report"


def pytest_configure(config):
    config.stash[metadata_key]["Project"] = "Coding task for SharkNinja"
    config.stash[metadata_key]["Author"] = "Aditya Kulkarni"


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Description</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(2, f'<td>{getattr(report, "description", "")}')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.when == "call":  # Only add description for the actual test call phase
        func_args = item.funcargs
        args = []
        for arg_name, arg_value in func_args.items():
            if arg_name in ("start", "end"):
                args.append(f"{arg_name} = {arg_value}")
        if len(args):
            report.description = f"{item.function.__doc__}: {', '.join(args)}."
        else:
            report.description = f"{item.function.__doc__}"
