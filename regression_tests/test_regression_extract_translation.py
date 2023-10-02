import inspect
import sys

from .util import Util, rel_data, update_baselines


class TestRegressionExtractTranslationBasic(Util.TestRegression):
    name = "extract_translation_basic"
    command = [
        "cbpickaxe_extract_translation",
        "--translation_files",
        rel_data("test.pr.translation"),
        "--strings_text_files",
        rel_data("test_strings.txt"),
        "--output_file",
        "translated_strings.csv",
    ]
    expected_files = ["translated_strings.csv"]


if __name__ == "__main__":
    tests = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and obj != Util:
            tests.append(obj)

    update_baselines(tests)
