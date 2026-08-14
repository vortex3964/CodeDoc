# DESC: main.py is purely here to process the flags and start the procedure
# for the files in the right mode

import os
from pathlib import Path

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
def list_files_req(root_dir, exc):
    files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if (d not in exc and d not in IGNORE_DIRS)]

        for fname in filenames:
            if fname in IGNORE_FILES:
                continue

            ext = Path(fname).suffix.lower()

            if ext in IGNORE_EXTENSIONS:
                continue

            # make path relative to the project root since it will be displayed in the end file
            dirpath = os.path.relpath(dirpath, root_dir)
            files.append(os.path.join(dirpath, fname))

    files.sort()
    return files


def main():
    # exclude list leave till we add flags
    exc = []
    # current working dir needs to change
    path = Path().parent.resolve()
    print(path)
    file_list = list_files_req(path, exc)
    print(file_list)


if __name__ == "__main__":
    main()
