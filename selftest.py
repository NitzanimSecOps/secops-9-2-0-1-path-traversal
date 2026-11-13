"""Local tester for server.py - not the hidden grader.

    python3 selftest.py

Starts your server.py in the background and asks it for the names below: files it creates in files/
(with random names, so your own files stay untouched), a subfolder, a symlink that leads outside, a
secret file next to server.py and a folder next to files/. Everything it created is removed at the
end. The downloads/ folder it makes is in a temporary folder, removed at the end, so your own
downloads/ stays untouched. Add your own cases.
"""
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time

HOST = "127.0.0.1"
PORT = 2405


def port_is_taken():
    try:
        socket.create_connection((HOST, PORT), timeout=1).close()
        return True
    except OSError:
        return False


def main():
    if port_is_taken():
        print(f"Something (probably a server.py you started) is already listening on port {PORT}.")
        print("Stop it with Ctrl+C in its window, then run selftest.py again.")
        sys.exit(1)
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
    work = tempfile.mkdtemp()  # download() saves into downloads/ under the current folder
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
        if server.poll() is not None:
            print("server.py stopped right after starting (its error is printed above).")
            sys.exit(1)
        sys.path.insert(0, here)
        from client import download, run_command

        os.chdir(work)

        with socket.create_connection((HOST, PORT)) as s:
            s.settimeout(10)
            for name, should in cases:
                got = download(s, name) is not None
                print(("ok   " if got == should else "WRONG"), name, "- downloaded" if got else "- refused")
            print("still alive:", run_command(s, "echo yes"))
    finally:
        os.chdir(here)
        shutil.rmtree(work, ignore_errors=True)
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
