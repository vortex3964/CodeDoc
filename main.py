# DESC: main.py is purely here to process the flags and start the procedure
# for the files in the right mode

import argparse
import os
from pathlib import Path
from parser import dispatch

#  list of ignored files extensions etch
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


# recursively list all the files under root dir
def list_files_req(root_dir, exc_dirs: list, exc_files: list):
    files = []

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

            # make path relative to the project root since it will be displayed in the end file
            dirpath = os.path.relpath(dirpath, root_dir)
            files.append(os.path.join(dirpath, fname))

    files.sort()
    return files


def help():
    pass


def main():
    # init the parser
    parser = argparse.ArgumentParser(
        description="cli tool to parse specialized comments from code files into markdown to help with documentation",
        epilog="codedoc <path> -o doc -exd test/ docs/ -exf test.py code.py",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to read from defaults to ( current directory )",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="out",
        nargs="?",
        default="out.md",
        required=False,
        help="output path",
    )

    parser.add_argument(
        "-exd",
        "--exclude-dirs",
        dest="exc_d",
        nargs="*",
        help="directores to exclude from reading",
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
        dest="clean_doc",
        nargs="?",
        default="None",
        help="remove doc end comments from codebase",
    )

    args = parser.parse_args()

    file_list = list_files_req(args.path, args.exc_d, args.exc_f)
    
    clean = True

    if args.clean_doc == "None":
        clean = False

    # print(file_list)
    dispatch(file_list,args.out,clean)


if __name__ == "__main__":
    main()
