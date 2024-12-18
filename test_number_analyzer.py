import json
import os
import re

import pytest

from number_analyzer import NumberAnalyzer, NumberAnalyzerException
from testdata import *


# All  setup fixtures are in conftest.py
# Test case specific fixtures
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


# Config based tests
@pytest.mark.config_test
def test_valid_initialization(valid_config_file):
    """
    Verifies that a valid configuration file can be loaded and the variables are initialized as expected.
    """
    analyzer = NumberAnalyzer(1, 10, config_file=valid_config_file)
    assert analyzer.start == 1
    assert analyzer.end == 10
    assert len(analyzer.rules) == 4
    assert analyzer.config == json.load(open(valid_config_file))
    assert analyzer.results == EXPECTED_RESULTS
    assert analyzer.results_debug == EXPECTED_RESULTS_DEBUG


@pytest.mark.config_test
def test_invalid_config_directory():
    """
    Verifies that a missing config file can be handled and the exception are raised as expected.
    """
    with pytest.raises(NumberAnalyzerException, match="config file not found"):
        NumberAnalyzer(1, 10, config_file="/nonexistent/config.json")


@pytest.mark.config_test
def test_invalid_config_file(invalid_config_file):
    """
    Verifies that a config file with syntax error can be handled and the exception are raised as expected.
    """
    with pytest.raises(NumberAnalyzerException,
                       match=re.escape(f"error in rule for label Div5: invalid syntax (<string>, line 1)")):
        NumberAnalyzer(1, 10, config_file=invalid_config_file)


@pytest.mark.config_test
def test_valid_config_path(valid_config_file_path):
    """
    Verifies that a valid configuration file at custom location can be loaded.
    """
    na = NumberAnalyzer(1, 10, config_file=valid_config_file_path)
    assert na.config == json.load(open(valid_config_file_path))


@pytest.mark.config_test
def test_default_config():
    """
    Verifies that the default configuration file can be loaded and is working as expected.
    """
    na = NumberAnalyzer(1, 10)
    expected_results = ['Odd',
                        'Even, Prime',
                        'Prime, Odd',
                        'Even',
                        'Prime, Odd',
                        'Even',
                        'Prime, Odd',
                        'Even',
                        'Odd',
                        'Even']
    expected_results_debug = {1: 'Odd',
                              2: 'Even, Prime',
                              3: 'Prime, Odd',
                              4: 'Even',
                              5: 'Prime, Odd',
                              6: 'Even',
                              7: 'Prime, Odd',
                              8: 'Even',
                              9: 'Odd',
                              10: 'Even'}
    assert na.config == json.load(open(os.path.join(os.curdir, "config", "default.json")))
    assert na.results == expected_results
    assert na.results_debug == expected_results_debug


@pytest.mark.config_test
def test_valid_config_full_definition(valid_config_file_full_definition):
    """
    Verifies that a config file containing custom method definition can be loaded and is working as expected.
    """
    na = NumberAnalyzer(1, 10, config_file=valid_config_file_full_definition)
    expected_results = ['Odd',
                        'Prime, Even',
                        'Prime, Odd',
                        'Even',
                        'Prime, Odd',
                        'Even',
                        'Prime, Odd, Div7',
                        'Even',
                        'Odd',
                        'Even']
    expected_results_debug = {1: 'Odd',
                              2: 'Prime, Even',
                              3: 'Prime, Odd',
                              4: 'Even',
                              5: 'Prime, Odd',
                              6: 'Even',
                              7: 'Prime, Odd, Div7',
                              8: 'Even',
                              9: 'Odd',
                              10: 'Even'}
    assert na.config == json.load(open(valid_config_file_full_definition))
    assert na.results == expected_results
    assert na.results_debug == expected_results_debug


@pytest.mark.config_test
def test_invalid_config_full_definition(invalid_config_file_full_definition):
    """
    Verifies that a config file with syntax error in full method definition can be handled and the exception are raised as expected.
    """
    with pytest.raises(NumberAnalyzerException,
                       match=re.escape(f"error in rule for label Div7: invalid syntax (<string>, line 2)")):
        NumberAnalyzer(1, 10, config_file=invalid_config_file_full_definition)


@pytest.mark.config_test
def test_invalid_json(invalid_json_config):
    """
    Verifies that a config file containing invalid JSON can be handled and the exception are raised as expected.
    """
    with pytest.raises(NumberAnalyzerException,
                       match=re.escape(
                           "config file could not be read: Expecting ':' delimiter: line 1 column 40 (char 39)")):
        NumberAnalyzer(1, 10, config_file=invalid_json_config)


# Parameter based tests
@pytest.mark.parameter_test
def test_start_greater_than_end(valid_config_file):
    """
    Verifies that start > end case is handled correctly.
    """
    with pytest.raises(NumberAnalyzerException, match="start must be smaller than end"):
        NumberAnalyzer(10, 1, config_file=valid_config_file)


@pytest.mark.parameter_test
def test_non_integer_start_or_end(valid_config_file):
    """
    Verifies that non-integer start or end case is handled correctly.
    """
    with pytest.raises(NumberAnalyzerException, match="start and end must be integers"):
        NumberAnalyzer("a", 10, config_file=valid_config_file)


# Functional tests
@pytest.mark.functional_test
def test_prime_rule(default_na):
    """
    Verifies that the prime rule works as expected.
    """
    assert default_na.rules["Prime"](2) is True
    assert default_na.rules["Prime"](4) is False


@pytest.mark.functional_test
def test_even_rule(default_na):
    """
    Verifies that the even rule works as expected.
    """
    assert default_na.rules["Even"](2) is True
    assert default_na.rules["Even"](3) is False


@pytest.mark.functional_test
def test_odd_rule(default_na):
    """
    Verifies that the odd rule works as expected.
    """
    assert default_na.rules["Odd"](3) is True
    assert default_na.rules["Odd"](2) is False


@pytest.mark.functional_test
def test_custom_rule(default_na):
    """
    Verifies that the divisible by 5 custom rule works as expected.
    """
    assert default_na.rules["Div5"](5) is True
    assert default_na.rules["Div5"](12) is False


@pytest.mark.functional_test
@pytest.mark.parametrize('start, end, expected_results', [
    (-100, 100, EXPECTED_RESULTS_TC1),
    (0, 10000, EXPECTED_RESULTS_TC2),
    (1, 1, EXPECTED_RESULTS_TC3),
    (2147483647, 2147483647, EXPECTED_RESULTS_TC4),
    (-9223372036854775808, -9223372036854775808, EXPECTED_RESULTS_TC5)
])
def test_input_range(valid_config_file, start, end, expected_results):
    """
    Verifies the function works as expected for various input ranges
    """
    na = NumberAnalyzer(start, end, config_file=valid_config_file)
    assert na.results_debug == expected_results


# Output based test
@pytest.mark.output_test
def test_print_results(capsys, default_na):
    """
    Verifies that results are printed in expected format.
    """
    """Description"""
    default_na.print_results(debug=False)

    captured = capsys.readouterr()
    expected_output = "\n".join(['Odd',
                                 'Prime, Even',
                                 'Prime, Odd',
                                 'Even',
                                 'Prime, Odd, Div5',
                                 'Even',
                                 'Prime, Odd',
                                 'Even',
                                 'Odd',
                                 'Even, Div5\n'])
    assert captured.out == expected_output

    default_na.print_results()

    captured = capsys.readouterr()
    expected_output = "\n".join(['1: Odd',
                                 '2: Prime, Even',
                                 '3: Prime, Odd',
                                 '4: Even',
                                 '5: Prime, Odd, Div5',
                                 '6: Even',
                                 '7: Prime, Odd',
                                 '8: Even',
                                 '9: Odd',
                                 '10: Even, Div5\n'])
    assert captured.out == expected_output
