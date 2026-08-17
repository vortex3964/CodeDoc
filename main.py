# Doc : Description
# main.py processes the command line flags and starts the
# dispatcher to generate the documentation, it also checks
# for updates at the end of every run and can update itself

import argparse
import asyncio
import json
import os
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from parser import dispatch

# Doc : list of ignored directories, extensions and files
# we keep lists called IGNORE_DIRS IGNORE_EXTENSIONS IGNORE_FILES of the
# files we would like to ignore like hidden files (.git) or .exe files we
# shouldn't bother reading
IGNORE_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "vendor",
    "bower_components",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".nuxt",
    "bin",
    "obj",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".idea",
    ".vscode",
    ".vs",
    ".gradle",
    ".terraform",
    "coverage",
    "site-packages",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".class",
    ".o",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".rar",
    ".7z",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".webp",
    ".mp3",
    ".mp4",
    ".wav",
    ".avi",
    ".mov",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".bin",
    ".lock",
    ".mod",
}

IGNORE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    ".gitignore",
}


# Doc code : recursive listing of all the files in the directories
# walks the root directory recursively and returns the sorted
# list of files to parse, skipping the ignored directories,
# extensions, files and the user excluded ones


def list_files_req(root_dir, exc_dirs: list, exc_files: list):
    files = []
    exc_dirs = exc_dirs or []
    exc_files = exc_files or []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            d for d in dirnames if (d not in exc_dirs and d not in IGNORE_DIRS)
        ]

        for fname in filenames:
            if fname in IGNORE_FILES or fname in exc_files:
                continue
            ext = Path(fname).suffix.lower()

            if ext in IGNORE_EXTENSIONS:
                continue

            # keep the walk path as-is so workers can open the file
            # from the current working directory, it also gets
            # displayed in the end file
            files.append(os.path.join(dirpath, fname))

    files.sort()
    return files


# Doc end

# Doc : update helpers
# the update check compares the installed copy against the latest
# commit on github, it runs at the end of main so the file reading
# is never slowed down by the network, it stays quiet when there
# is no connection or a rate limit and it skips dev checkouts

REPO = "vortex3964/CodeDoc"
BRANCH = "main"
COMMITS_URL = f"https://api.github.com/repos/{REPO}/commits/{BRANCH}"
TARBALL_URL = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.tar.gz"


def get_install_dir() -> str | None:
    # the launcher runs main.py from the install dir, so the script's
    # own location is the install, a dev checkout has a .git folder
    d = os.path.dirname(os.path.realpath(__file__))
    if os.path.isdir(os.path.join(d, ".git")):
        return None
    return d


def fetch_latest_commit() -> str | None:
    try:
        with urllib.request.urlopen(COMMITS_URL, timeout=5) as resp:
            data = json.load(resp)
        return data.get("sha")
    except Exception:
        return None


def apply_update(install_dir: str, latest: str) -> bool:
    tmp = tempfile.mkdtemp(prefix="codedoc-")
    try:
        tarball = os.path.join(tmp, "codedoc.tar.gz")
        urllib.request.urlretrieve(TARBALL_URL, tarball)
        with tarfile.open(tarball, "r:gz") as tf:
            tf.extractall(tmp)

        src = next(
            os.path.join(tmp, entry)
            for entry in os.listdir(tmp)
            if os.path.isfile(os.path.join(tmp, entry, "main.py"))
        )

        for entry in os.listdir(src):
            source = os.path.join(src, entry)
            target = os.path.join(install_dir, entry)
            if os.path.isdir(source):
                shutil.rmtree(target, ignore_errors=True)
                shutil.copytree(source, target)
            else:
                try:
                    os.replace(source, target)
                except OSError:
                    shutil.copy2(source, target)

        with open(os.path.join(install_dir, ".commit"), "w") as f:
            f.write(latest)
        return True
    except Exception:
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


async def check_for_update(apply: bool):
    install_dir = get_install_dir()
    if install_dir is None:
        if apply:
            print("codedoc --update only works on an installed copy, use git pull in a dev checkout")
        return

    latest = await asyncio.to_thread(fetch_latest_commit)
    if latest is None:
        if apply:
            print("couldn't check for updates, check your network connection")
        return

    commit_file = os.path.join(install_dir, ".commit")
    current = None
    if os.path.isfile(commit_file):
        with open(commit_file) as f:
            current = f.read().strip()

    if current == latest:
        if apply:
            print(f"codedoc is already up to date ({current[:7]})")
        return

    if not apply:
        print("a new version of codedoc is available, run 'codedoc --update' to update")
        return

    if await asyncio.to_thread(apply_update, install_dir, latest):
        print(f"codedoc updated: {current[:7] if current else 'unknown'} -> {latest[:7]}")
    else:
        print("update failed, try again later")


# Doc: main
# parses the command line arguments, builds the file list and
# starts the dispatcher, the update flag only updates the tool
# itself and skips the documentation run


async def main():
    # init the parser
    parser = argparse.ArgumentParser(
        description="cli tool to parse specialized comments from code files into markdown to help with documentation",
        epilog="codedoc <path> -o doc -exd test/ docs/ -exf test.py code.py",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to read from, defaults to (current directory)",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="out",
        nargs="?",
        default="out",
        required=False,
        help="output path",
    )

    parser.add_argument(
        "-exd",
        "--exclude-dirs",
        dest="exc_d",
        nargs="*",
        help="directories to exclude from reading",
    )

    parser.add_argument(
        "-exf",
        "--exclude-files",
        dest="exc_f",
        nargs="*",
        help="files to exclude from reading",
    )

    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="remove doc end comments from the source files",
    )

    parser.add_argument(
        "-ca",
        "--cleanall",
        action="store_true",
        help="remove every doc comment and doc end from the source files",
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="check for and apply the latest version, skips the documentation run",
    )

    args = parser.parse_args()

    # the update flag only updates the tool, nothing else runs
    if args.update:
        await check_for_update(apply=True)
        return

    file_list = list_files_req(args.path, args.exc_d, args.exc_f)

    # make sure the output is an md file
    args.out = f"{args.out}.md"

    # print(file_list)
    await dispatch(file_list, args.out, args.clean, args.cleanall)

    # the success message comes first, the update check runs at the
    # end so the file reading is never slowed down by the network
    print(f"documentation written to {args.out}")
    await check_for_update(apply=False)


if __name__ == "__main__":
    asyncio.run(main())

# Doc end
