import json
from collections import OrderedDict  # noqa
from pathlib import Path


def main():
    answers = {key: value for key, value in {{ cookiecutter }}.items() if not key.startswith("_")}
    filename = Path.cwd() / "cookiecutter-answers.json"
    with filename.open(mode="w") as fobj:
        json.dump({"cookiecutter": answers}, fobj, indent=2)
    print(f"File {filename} saved with all the answers (useful to rebuild with --replay-file).")

if __name__ == "__main__":
    main()
