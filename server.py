# Copy your server.py from 9.0.0.3 here, and replace its find_file with the version below.

import os

FILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")


def find_file(name):
    # the path of name if it is a real file inside FILES or one of its subfolders, otherwise None
    # (a file in a subfolder and a name like a..b.txt are fine; ../x, an absolute path and a
    # symlink that leads outside FILES are not)
    pass
