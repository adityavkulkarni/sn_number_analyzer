import argparse
import json
import math
import os
import re
from json.decoder import JSONDecodeError


class NumberAnalyzerException(Exception):
    """
    Exception raised when an error occurs inside the number analyzer.
    """
    pass


class NumberAnalyzer(object):
    """
    A class to analyze numbers in a given range based on configurable rules.

    The `NumberAnalyzer` class processes numbers between a start and end value (inclusive),
    applying rules defined in a configuration file to classify them into categories.
    Rules can include built-in checks (e.g., prime, even, odd) or custom rules defined
    as Python functions or lambda expressions in the configuration file.

    Attributes:
        start (int): The starting number of the range.
        end (int): The ending number of the range.
        config_file (str): Path to the JSON configuration file defining rules.
        config (dict): Parsed configuration data from the JSON file.
        rules (dict): A mapping of rule labels to their corresponding functions.
        results (list): A list of results for each number in the range.
        results_debug (dict): A dictionary mapping numbers to their corresponding results for debugging purposes.

    Raises:
        NumberAnalyzerException: If parameters are invalid or if there are issues with the configuration file or rules.
    """

    def __init__(self, start, end, config_file="default.json"):
        """
        Initializes the NumberAnalyzer instance.

        Args:
            start (int): The starting number of the range.
            end (int): The ending number of the range.
            config_file (str): Path to the JSON configuration file. Defaults to "default.json".

        Raises:
            NumberAnalyzerException: If validation fails for parameters or configuration file.
        """
        self.start = start
        self.end = end
        self.config_file = config_file
        self._validate_params()

        self.config = dict()
        self.rules = dict()
        self._parse_config()

        self.results = []
        self.results_debug = dict()
        self._get_results()

    def _validate_params(self):
        """
        Validates input parameters and ensures the configuration directory and file exist.

        Checks:
            - The `start` and `end` parameters are integers.
            - `start` is less than or equal to `end`.
            - The configuration directory exists.
            - The configuration file exists.

        Raises:
            NumberAnalyzerException: If any validation fails.
        """
        config_directory = os.path.abspath('config')
        if not os.path.exists(config_directory):
            raise NumberAnalyzerException("config directory does not exist")
        if not isinstance(self.start, int) or not isinstance(self.end, int):
            raise NumberAnalyzerException("start and end must be integers")
        if self.start > self.end:
            raise NumberAnalyzerException("start must be smaller than end")
        if not os.path.dirname(self.config_file):
            self.config_file = os.path.join(config_directory, self.config_file)
        if not os.path.isfile(self.config_file):
            raise NumberAnalyzerException("config file not found")

    def _parse_config(self):
        """
        Parses the configuration file and sets up rules for number analysis.

        The method reads a JSON configuration file containing categories and their associated rules.
        It maps each rule label to a corresponding function, which could be a built-in check,
        a lambda expression, or a custom function defined in the configuration.

        Raises:
            NumberAnalyzerException: If there is an issue reading or parsing the configuration file,
                                      or if any rule is invalid or contains syntax errors.
        """
        try:
            self.config = json.load(open(self.config_file))
        except JSONDecodeError as e:
            raise NumberAnalyzerException("config file could not be read: {}".format(e))
        for rule in self.config['categories']:
            if rule['rule'] == 'prime':
                self.rules[rule['label']] = self._check_prime
            elif rule['rule'] == 'even':
                self.rules[rule['label']] = self._check_even
            elif rule['rule'] == 'odd':
                self.rules[rule['label']] = self._check_odd
            elif "lambda" in rule['rule']:
                try:
                    eval(rule['rule'])(10)
                except SyntaxError as e:
                    raise NumberAnalyzerException(f"error in rule for label {rule['label']}: {e}")
                self.rules[rule['label']] = eval(rule['rule'])
            elif "def" in rule['rule']:
                try:
                    exec(rule['rule'])
                    method_name = self._get_method_name_from_string(rule['rule'])
                    if len(method_name) == 0:
                        raise SyntaxError
                    method = locals()[method_name]
                    method(10)
                except SyntaxError as e:
                    raise NumberAnalyzerException(f"error in rule for label {rule['label']}: {e}")
                self.rules[rule['label']] = method

    @staticmethod
    def _get_method_name_from_string(method_def_string) -> str:
        """
        Extracts a method name from a string containing a Python function definition.

        Args:
            method_def_string (str): A string containing a Python function definition.

        Returns:
            str: The name of the method if found, otherwise None.

        Example:
            Input: "def my_function(x): return x + 1"
            Output: "my_function"
        """
        match = re.search(r"def\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(", method_def_string)
        if match:
            return match.group(1)  # Return the captured method name
        return ""

    @staticmethod
    def _check_prime(number):
        """
        Checks whether a given number is prime.

        Args:
            number (int): The number to check.

        Returns:
            bool: True if the number is prime, False otherwise.

        Note:
            Handles both positive and negative numbers. Zero and one are not considered prime.
        """
        if abs(number) <= 1:
            return False

        for i in range(2, int(math.sqrt(abs(number))) + 1):
            if abs(number) % i == 0:
                return False

        return True

    @staticmethod
    def _check_odd(number):
        """
        Checks whether a given number is odd.

        Args:
            number (int): The number to check.

        Returns:
            bool: True if the number is odd, False otherwise.

        Note:
            Odd numbers are those not divisible by 2.
        """
        if number % 2 == 0:
            return False
        return True

    @staticmethod
    def _check_even(number):
        """
        Checks whether a given number is even.

        Args:
            number (int): The number to check.

        Returns:
            bool: True if the number is even, False otherwise.

         Note: Even numbers are divisible by 2 without remainder.
         """
        if number % 2 == 1:
            return False
        return True

    def _get_results(self):
        """
        Processes numbers in the specified range and applies rules to categorize them.

        For each number in the range `[start, end]`, this method evaluates all the rules defined
        in the configuration file. Each rule is applied to the number, and if the rule is satisfied,
        the corresponding label is added to the results for that number.

        The results are stored in two attributes:
            - `self.results`: A list where each entry corresponds to a number's categories (as a string).
            - `self.results_debug`: A dictionary mapping each number to its categories (for debugging).

        Workflow:
            1. Iterates through all numbers in the range `[start, end]`.
            2. Applies each rule function to the current number.
            3. Collects labels of rules that pass for that number.
            4. Stores results in both `self.results` and `self.results_debug`.

        Example:
            If `start=1`, `end=3`, and rules include "prime" and "odd":
                - Number 1: No categories (empty string).
                - Number 2: "prime".
                - Number 3: "prime, odd".

            Results:
                self.results = ["odd", "prime", "prime, odd"]
                self.results_debug = {1: "odd", 2: "prime", 3: "prime, odd"}
        """
        for number in range(self.start, self.end + 1):
            number_result = []
            for label, rule in self.rules.items():
                if rule(number):
                    number_result.append(label)
            self.results.append(", ".join(number_result))
            self.results_debug[number] = ", ".join(number_result)

    def print_results(self, debug=True):
        """
        Prints the categorized results of numbers based on applied rules.

        Depending on the `debug` flag, this method prints either a detailed view
        (with numbers and their corresponding categories) or a simplified view
        (only the categories as strings).

        Args:
            debug (bool): If True, prints detailed results with numbers.
                          If False, prints only categorized results without numbers.
                          Defaults to True.

        Examples:
            With `debug=True`:
                Prints:
                    1: odd
                    2: prime
                    3: prime, odd

            With `debug=False`:
                Prints:
                    odd
                    prime
                    prime, odd
        """
        if debug:
            for number, result in self.results_debug.items():
                print(f"{number}: {result}")
        else:
            for result in self.results:
                print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze numbers based on rules from a configuration file.")
    parser.add_argument("--start", type=int, default=None, help="The starting number of the range.")
    parser.add_argument("--end", type=int, default=None, help="The ending number of the range.")
    parser.add_argument("--config_file", type=str, default="default.json", help="The path to the configuration file.")
    args = parser.parse_args()

    if args.start is not None and args.end is not None:
        na = NumberAnalyzer(start=args.start, end=args.end, config_file=args.config_file)
        na.print_results()
    else:
        cont = 'y'
        while cont == 'y':
            start = int(input("Please enter the starting number of the range: "))
            end = int(input("Please enter the ending number of the range: "))
            na = NumberAnalyzer(start=start, end=end, config_file=args.config_file)
            na.print_results()
            cont = input("Continue? (y/n): ").lower()
