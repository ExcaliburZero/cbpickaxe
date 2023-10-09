import pathlib
import inspect
import sys

from .util import Util, rel_data, update_baselines


class TestRegressionGenerateDocsBuildEmptyMod(Util.TestRegression):
    name = "generate_docs_build_empty_mod"
    command = [
        "cbpickaxe_generate_docs",
        "build",
        "--config",
        rel_data("docs_empty.toml"),
    ]
    expected_files = ["docs/index.html"]


class TestRegressionGenerateDocsBuildModWithMoves(Util.TestRegression):
    name = "generate_docs_build_mod_with_moves"
    command = [
        "cbpickaxe_generate_docs",
        "build",
        "--config",
        rel_data("docs_moves.toml"),
    ]
    expected_files = ["docs/index.html", "docs/moves/Fire Spit.html"]


if __name__ == "__main__":
    tests = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and obj != Util:
            tests.append(obj)

    update_baselines(tests)
