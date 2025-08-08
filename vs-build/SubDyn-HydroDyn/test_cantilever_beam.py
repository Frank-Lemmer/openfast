"""Test for Subdyn-Hydrodyn coupling, used as a preprocessor for generating substructure SID matrices
Simple beam in air and in water. With 0 gravity and increased structural mass gives same results as in water"""
from colorama import Fore, Style
from functools import wraps
import sys

from pathlib import Path
import subprocess, os
from ruamel.yaml import YAML
import numpy as np


# Global list to store all registered test functions
test_registry = []

EXE = Path(rf"..\..\build\bin\SubDyn-HydroDyn_x64.exe")

def verification_test(func):
    """
    Decorator to register a function as a verification test.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Add the function to the global registry
    test_registry.append(func)

    return wrapper


class VerificationFramework:
    """
    Framework to run and verify multiple simulations.
    """

    def __init__(self):
        self.simulations = []

    def run_all(self):
        """
        Runs all registered verification tests and prints pass/fail for each one, with color coding.
        """
        print("Running all verification simulations...\n")
        passed = 0
        failed = 0

        # Loop through all registered test functions
        for test_func in test_registry:
            result, reason = test_func()
            if result:
                print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL} {test_func.__name__}\t{reason}")
                passed += 1
            else:
                print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} {test_func.__name__}\tReason: {reason}")
                failed += 1

        print(f"\nSummary: {Fore.GREEN}{passed} passed{Style.RESET_ALL}, {Fore.RED}{failed} failed{Style.RESET_ALL}")

        # Return 0 if all tests passed, otherwise return 1
        if failed == 0:
            return 0
        else:
            return 1

@verification_test
def test_cantilever_beam_cyl():

    cases = {"INPUT_CYL_REF": Path("test_cantilever_beam_sd_cyl.dvr"),
            "INPUT_CYL_HDOFFA": Path("test_cantilever_beam_sd_cyl_hdoffA.dvr")}

    return compare_cases(cases, 0)

@verification_test
def test_cantilever_beam_vert():

    cases = {"INPUT_REC_REF": Path("test_cantilever_beam_sd.dvr"),
            "INPUT_REC_VERT_REF": Path("test_cantilever_beam_sd_vert.dvr")}

    return compare_cases(cases, 0)

@verification_test
def test_cantilever_beam_rectA():

    cases = {"INPUT_REC_REF": Path("test_cantilever_beam_sd.dvr"),
            "INPUT_REC_HDOFFA": Path("test_cantilever_beam_sd_hdoffA.dvr")}

    return compare_cases(cases, 0)

@verification_test
def test_cantilever_beam_rectB():

    cases = {"INPUT_REC_REF": Path("test_cantilever_beam_sd.dvr"),
            "INPUT_REC_HDOFFB": Path("test_cantilever_beam_sd_hdoffB.dvr")}

    return compare_cases(cases, 1)

def compare_cases(cases, ifreq):
    results = []
    yaml = YAML()
    for case in cases:
        print(rf"Running {case} ...")
        # os.system(rf"{EXE} {cases[case]}")
        subprocess.call(rf"{EXE} {cases[case]}", stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        yaml_file = Path(cases[case].stem + ".SD.sum.yaml")
        with open(yaml_file, 'r') as f:
            data = yaml.load(f)
            results.append(data["CB_frequencies"][0][ifreq])
    if np.isclose(results[1], results[0], atol=0.05):
        return True, rf"Diff={results[1]-results[0]}"
    else:
        return False, rf"Diff={results[1]-results[0]}"


if __name__ == "__main__":
    framework = VerificationFramework()

    exit_code = framework.run_all()
    sys.exit(exit_code)  # Exit with the appropriate code (0 for success, 1 for failure)