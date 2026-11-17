# Copy your server.py from 9.0.0.3 here, and replace its find_file with the version below.

import pathlib

FILES = pathlib.Path(__file__).resolve().parent / "files"


def find_file(name: str) -> pathlib.Path | None:
    # the path of name if it is a real file inside FILES or one of its subfolders, otherwise None
    # (a file in a subfolder and a name like a..b.txt are fine; ../x, an absolute path and a
    # symlink that leads outside FILES are not)
    pass
