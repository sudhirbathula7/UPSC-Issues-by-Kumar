from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Final


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent

CONVERTER: Final[Path] = (
    PROJECT_ROOT
    / "input_processing"
    / "text_to_json_converter.py"
)

VALIDATOR: Final[Path] = (
    PROJECT_ROOT
    / "input_processing"
    / "validator.py"
)


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_banner(label: str) -> None:
    print()
    print("=" * 72)
    print(label)
    print("=" * 72)


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f} seconds"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    return (
        f"{minutes} minute(s), "
        f"{remaining_seconds:.1f} seconds"
    )


# ============================================================
# VALIDATION HELPERS
# ============================================================

def require_file(
    path: Path,
    label: str,
) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"{label} was not found:\n{path}"
        )

    if not path.is_file():
        raise FileNotFoundError(
            f"{label} is not a file:\n{path}"
        )


# ============================================================
# PROCESS RUNNER
# ============================================================

def run_step(
    label: str,
    command: list[str],
) -> None:
    print_banner(label)

    started_at = time.perf_counter()

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(
            f"{label} could not be started: {exc}"
        ) from exc

    duration = time.perf_counter() - started_at

    if result.returncode != 0:
        print()
        print(f"{label} failed.")
        print(
            f"Exit code: {result.returncode}"
        )
        print(
            f"Time: {format_duration(duration)}"
        )

        raise SystemExit(
            result.returncode
            if result.returncode != 0
            else 1
        )

    print()
    print(
        f"{label} completed in "
        f"{format_duration(duration)}."
    )


# ============================================================
# PRODUCTION PIPELINE
# ============================================================

def main() -> int:
    pipeline_started_at = time.perf_counter()

    python_executable = sys.executable

    try:
        require_file(
            CONVERTER,
            "Input converter",
        )

        require_file(
            VALIDATOR,
            "Input validator",
        )

        # ----------------------------------------------------
        # STEP 1 — CONVERT INPUT_DATA.txt TO INPUT.json
        # ----------------------------------------------------

        run_step(
            "CONVERTING INPUT_DATA.txt TO INPUT.json",
            [
                python_executable,
                str(CONVERTER),
            ],
        )

        # ----------------------------------------------------
        # STEP 2 — VALIDATE INPUT.json
        # ----------------------------------------------------

        run_step(
            "VALIDATING INPUT.json",
            [
                python_executable,
                str(VALIDATOR),
            ],
        )

        # ----------------------------------------------------
        # STEP 3 — GENERATE STANDARD AND PRO PDFs
        # ----------------------------------------------------

        run_step(
            "GENERATING STANDARD AND PRO PDFs",
            [
                python_executable,
                "-m",
                "src.main",
            ],
        )

    except FileNotFoundError as exc:
        print_banner(
            "PRODUCTION PIPELINE FAILED"
        )
        print(exc)
        return 1

    except RuntimeError as exc:
        print_banner(
            "PRODUCTION PIPELINE FAILED"
        )
        print(exc)
        return 1

    total_duration = (
        time.perf_counter()
        - pipeline_started_at
    )

    print_banner(
        "COMPLETE PRODUCTION PIPELINE FINISHED"
    )

    print(
        "Input conversion : PASSED"
    )
    print(
        "Input validation : PASSED"
    )
    print(
        "Standard PDF     : GENERATED"
    )
    print(
        "Pro PDF          : GENERATED"
    )
    print(
        f"Total time       : "
        f"{format_duration(total_duration)}"
    )

    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())