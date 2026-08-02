from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
CONVERTER = PROJECT_ROOT / "input_processing" / "text_to_json_converter.py"
VALIDATOR = PROJECT_ROOT / "input_processing" / "validator.py"


def run_step(label: str, command: list[str]) -> None:
    print("\n" + "=" * 72)
    print(label)
    print("=" * 72)

    result = subprocess.run(command, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        raise SystemExit(f"{label} failed.")


def main() -> None:
    python = sys.executable

    run_step(
        "CONVERTING INPUT_DATA.txt TO INPUT.json",
        [python, str(CONVERTER)],
    )

    run_step(
        "VALIDATING INPUT.json",
        [python, str(VALIDATOR)],
    )

    run_step(
        "GENERATING PRO PDF",
        [python, "-m", "src.main"],
    )

    print("\n" + "=" * 72)
    print("COMPLETE PRODUCTION PIPELINE FINISHED")
    print("=" * 72)


if __name__ == "__main__":
    main()