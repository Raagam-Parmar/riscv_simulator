import sys
from pathlib import Path

# add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.cli.simulate import run_simulation

if __name__ == "__main__":
    run_simulation()
