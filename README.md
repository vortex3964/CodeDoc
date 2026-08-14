# CodeDoc

A CLI tool that turns specialized `Doc` comments in your source code into a single markdown document. 

It scans a directory recursively, extracts every `Doc` comment block from the supported languages, and writes the result to a markdown file in the same order as the files on disk.

## Installation

**Linux / macOS** (requires Python 3.10+ and curl):

```
curl -fsSL https://raw.githubusercontent.com/vortex3964/CodeDoc/main/install/install.sh | bash
```

**Windows** (requires Python 3.10+):

```
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/vortex3964/CodeDoc/main/install/install.ps1 | iex"
```

This installs the `codedoc` command to `~/.local/bin` (Linux/macOS) or `%LOCALAPPDATA%\codedoc\bin` (Windows) and adds it to your PATH. Open a new terminal and run `codedoc` from anywhere.

Installer options (`install/install.sh`): `--no-modify-path` to skip touching your shell config, `--local <dir>` to install from a local copy of the project (useful for development).

Uninstall:

```
bash install/uninstall.sh                    # Linux/macOS
powershell -File install/uninstall.ps1       # Windows
```

## Requirements

- Python 3.10 or newer
- no pip needed

## Usage

```
codedoc [path] [-o OUT] [-exd DIRS ...] [-exf FILES ...]
```

| Option | Description |
| --- | --- |
| `path` | directory to scan, defaults to the current directory |
| `-o`, `--output` | output file name, `.md` is appended automatically, defaults to `out` |
| `-exd`, `--exclude-dirs` | directories to skip (in addition to the built-in ignore list) |
| `-exf`, `--exclude-files` | files to skip |
| `-c`, `--clean` | accepted for compatibility, not implemented yet |

Examples:

```
codedoc                            # scan "." and write out.md
codedoc src/ -o docs/api           # scan src/ and write docs/api.md
codedoc . -o out -exd test build -exf setup.py
```

Running from source instead (no install needed):

```
python3 main.py [path] [-o OUT] [-exd DIRS ...] [-exf FILES ...]
```

Notes:

- the output directory must already exist,
- the output file is truncated at the start of every run,
- files without any `Doc` comment are skipped,
- ignored by default: `.git`, `node_modules`, `venv`, `__pycache__`, `dist`, `build`, `out`, `target`, `bin`, `obj`, and other common build/tooling directories, plus a list of binary extensions (`.pyc`, `.o`, `.png`, `.zip`, ...).

## Doc comment syntax

Doc comments look like normal comments, but start with the word `Doc`. The comment token depends on the language .

Three tags are recognized:

| Tag | Meaning |
| --- | --- |
| `Doc` | starts a section with no heading, everything until the next tag is emitted as code |
| `Doc code : name` | starts a section with a `## name` heading; a leading comment block becomes description text, the rest is emitted as code |
| `Doc end` | ends the current section |

Example in C:

```c
//Doc
#include <stdio.h>

//Doc code : hello world program
/*
 * hello world program
 * */

int main(void)
{
    printf("hello world");
    return 0;
}

//Doc end
```

Generates:

````markdown
# main.c

```c
#include <stdio.h>
```

## hello world program

hello world program  

```c
int main(void)
{
    printf("hello world");
    return 0;
}
```

````

## Supported languages

| Extension(s) | Single line | Multi line |
| --- | --- | --- |
| `.c .h .cpp .cc .cxx .hpp .hh .cs .java .js .jsx .ts .tsx .go .rs .d .swift .kt .kts .php .dart .scala .mm` | `//` | `/* */` |
| `.pas .pp .inc .fs` | `//` | `(* *)` |
| `.zig` | `//` | `//` (derived) |
| `.py .pyw .pyi` | `#` | `""" """` |
| `.erlang` | `#` | `#` (derived) |
| `.lua` | `--` | `--[[ ]]` |
| `.hs` | `--` | `{- -}` |
| `.asm .s` | `;` | `;` (derived) |
| `.vb .vbs .bas` | `'` | `'` (derived) |
| `.tex .sty .cls` | `%` | `%` (derived) |
| `.m` | `%` | `%{ }%` |
| `.html .htm .xhtml .xml` | `<!-- -->` (derived) | `<!-- -->` |

Languages with only one comment family derive the other from it: a language with only single line comments treats a run of consecutive comment lines as a multi line block, and a language with only multi line comments uses the pair as a single line comment (e.g. `<!--Doc-->` in HTML).

## Project layout

- `main.py` — argument parsing and file listing
- `parser.py` — comment extraction and markdown generation, runs one async worker per file and preserves the file order in the output
- `langs.py` — supported languages, comment tokens and the extension to family conversion tables
- `install/` — the curl/PowerShell installers and uninstallers for Linux, macOS and Windows

## Generating this project's own docs

The project documents itself with the command:

```
python3 main.py . -o docs -exd test
```
The documentation is in a docs dir in the project
