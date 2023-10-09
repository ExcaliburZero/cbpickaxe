import inspect
import sys

from .util import Util, rel_data, update_baselines


class TestRegressionGenerateDocsNew(Util.TestRegression):
    name = "generate_docs_new_basic"
    command = [
        "cbpickaxe_generate_docs",
        "new",
    ]
    expected_files = ["docs.toml"]
    stdin = ["Traffikrabdos", "y", "n", "../my_cassette_beasts"]


class TestRegressionGenerateDocsYesToEverything(Util.TestRegression):
    name = "generate_docs_new_yes_to_everything"
    command = [
        "cbpickaxe_generate_docs",
        "new",
    ]
    expected_files = ["docs.toml"]
    stdin = ["Traffikrabdos", "y", "y", "../my_cassette_beasts"]


class TestRegressionGenerateDocsNoToEverything(Util.TestRegression):
    name = "generate_docs_new_no_to_everything"
    command = [
        "cbpickaxe_generate_docs",
        "new",
    ]
    expected_files = ["docs.toml"]
    stdin = ["Traffikrabdos", "n", "n", "../my_cassette_beasts"]


class TestRegressionGenerateDocsSpacesInName(Util.TestRegression):
    name = "generate_docs_new_spaces_in_name"
    command = [
        "cbpickaxe_generate_docs",
        "new",
    ]
    expected_files = ["docs.toml"]
    stdin = ["Traffikrabdos is Cool", "n", "n", "../my_cassette_beasts"]


if __name__ == "__main__":
    tests = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and obj != Util:
            tests.append(obj)

    update_baselines(tests)
