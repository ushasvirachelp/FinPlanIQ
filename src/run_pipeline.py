import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_step(command):
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main():
    python = sys.executable

    run_step([python, "src/generate_data.py"])
    run_step([python, "src/clean_transform.py"])
    run_step([python, "src/build_duckdb.py"])
    run_step([python, "src/validate_data.py"])

    print("FinPlanIQ pipeline completed successfully.")


if __name__ == "__main__":
    main()