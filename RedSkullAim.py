import os
import sys


def _prepare_import_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    for path in (base_dir, parent_dir):
        if path and path not in sys.path:
            sys.path.insert(0, path)
    # Keep source-mode behavior for self-delete logic.
    os.environ.setdefault("REDSKULL_ENTRY_PATH", os.path.abspath(__file__))


_prepare_import_path()

from RedSkullAim_core import *  # noqa: F401,F403


if __name__ == "__main__":
    main()
