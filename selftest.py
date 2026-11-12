"""Local tester for server.py - not the hidden grader.

    python3 selftest.py

Starts your server.py in the background and asks it for the names below: files it creates in files/
(with random names, so your own files stay untouched), a subfolder, a symlink that leads outside, a
secret file next to server.py and a folder next to files/. Everything it created is removed at the
end. Add your own cases.
"""
import os
import secrets
import shutil
import socket
import subprocess
import sys
import time

HOST = "127.0.0.1"
PORT = 2405


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    files = os.path.join(here, "files")
    tag = secrets.token_hex(4)
    plain = f"selftest_{tag}.txt"
    folder = f"selftest_{tag}"
    secret = f"secret_{tag}.txt"
    sibling = f"files_selftest_{tag}"
    link = f"link_{tag}"

    # name, whether it should download
    cases = [
        (plain, True),
        (f"{folder}/a.txt", True),
        (f"{folder}/a..b.txt", True),
        (f"../{secret}", False),
        ("/etc/passwd", False),
        (f"{folder}/../../{secret}", False),
        (f"../{sibling}/x.txt", False),
        (link, False),
    ]

    created = []  # exactly what this run made, removed again at the end
    files_existed = os.path.isdir(files)
    server = None
    try:
        os.makedirs(files, exist_ok=True)
        os.makedirs(os.path.join(files, folder))
        created.append(os.path.join(files, folder))
        os.makedirs(os.path.join(here, sibling))
        created.append(os.path.join(here, sibling))
        for path, text in [
            (os.path.join(files, plain), "meow\n"),
            (os.path.join(files, folder, "a.txt"), "in a subfolder\n"),
            (os.path.join(files, folder, "a..b.txt"), "dots\n"),
            (os.path.join(here, secret), "top secret\n"),
            (os.path.join(here, sibling, "x.txt"), "top secret too\n"),
        ]:
            with open(path, "w") as f:
                f.write(text)
            if os.path.dirname(path) == files or path == os.path.join(here, secret):
                created.append(path)
        os.symlink(os.path.join(here, secret), os.path.join(files, link))
        created.append(os.path.join(files, link))

        server = subprocess.Popen([sys.executable, os.path.join(here, "server.py")], cwd=here)
        time.sleep(1)
        sys.path.insert(0, here)
        from client import download, run_command

        with socket.create_connection((HOST, PORT)) as s:
            s.settimeout(10)
            for name, should in cases:
                dest = os.path.join(here, f"downloaded_{tag}.tmp")
                got = download(s, name, dest) is not None
                if os.path.exists(dest):
                    os.remove(dest)
                print(("ok   " if got == should else "WRONG"), name, "- downloaded" if got else "- refused")
            print("still alive:", run_command(s, "echo yes"))
    finally:
        if server is not None:
            server.kill()
        for path in created:
            if os.path.islink(path) or os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
        if not files_existed:
            try:
                os.rmdir(files)
            except OSError:
                pass


if __name__ == "__main__":
    main()
