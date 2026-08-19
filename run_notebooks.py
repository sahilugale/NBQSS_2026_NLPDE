"""Execute the four notebooks in place.

Uses nbclient directly rather than `jupyter nbconvert`, which is broken on this
machine by a stale jupyter_contrib_nbextensions plugin.

    python3 run_notebooks.py                  # all four
    python3 run_notebooks.py variational      # only matching paths
"""

import os
import sys
import time

import nbformat
from nbclient import NotebookClient

NOTEBOOKS = [
    "carleman_qsvt/Burgers_Carlemann_qiskit.ipynb",
    "carleman_qsvt/KdV_Carlemann_qiskit.ipynb",
    "variational/Burgers_variational_qiskit.ipynb",
    "variational/KdV_variational_qiskit.ipynb",
]

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(rel_path, timeout=7200):
    path = os.path.join(ROOT, rel_path)
    print(f"--- {rel_path}", flush=True)
    t0 = time.time()
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": os.path.dirname(path)}},
    )
    client.execute()
    nbformat.write(nb, path)
    print(f"    ok ({time.time() - t0:.0f}s)", flush=True)


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else ""
    targets = [n for n in NOTEBOOKS if pattern in n]
    for rel in targets:
        try:
            run(rel)
        except Exception as exc:  # keep going so one failure doesn't block the rest
            print(f"    FAILED: {type(exc).__name__}: {exc}", flush=True)
    print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
