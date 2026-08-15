# Doc : Description
# thread pool and parsing logic that turns doc comments into
# markdown, dispatch runs one worker per file

import asyncio
import pathlib
import re
from langs import GetCommentFamily

# Doc code: global variables we reuse for multithreading
# shared resource to keep track of file order so that files are
# written properly and sorted as we do it in main
l = []
out = ""

# this is the lock to make sure that only one file ever writes to the
# output folder that's a shared resource
file_lock = asyncio.Lock()

# condition for stopping the wait cycle in worker, it also guards the
# shared list l so that waiters wake up when the head changes
cond = asyncio.Condition()

# Doc end

# Doc code : remove_head_from_list
# pops the first entry of the order list and wakes up the
# workers waiting for their turn


async def remove_head_from_list():
    global l
    async with cond:
        if len(l) != 0:
            l.pop(0)
        cond.notify_all()


# Doc end

# Doc  : remove_item_from_list
# removes an entry from the order list without blocking the
# queue, used for files that produced no output


async def remove_item_from_list(item: str):
    global l
    async with cond:
        try:
            l.remove(item)
        except ValueError:
            # do nothing if we don't find the value
            return
        cond.notify_all()


# Doc: sync_write_file
# the write is a sync task so we need a helper function
# run in a thread so we don't wait synchronously for the
# i/o to finish every time and freeze the event loop
def sync_write_file(md_contents: str, out_path: str):
    with open(out_path, "a") as f:
        f.write(md_contents)


# Doc : write_file
# appends the markdown of a file to the output file, the
# file lock serializes the writers so only the head of the
# order list writes at a time


async def write_file(md_contents: str, out_path: str):
    async with file_lock:
        await asyncio.to_thread(sync_write_file, md_contents, out_path)
        await remove_head_from_list()


# Doc  : sync_read_file
# sync file read helper, runs in a thread by read_file


def sync_read_file(name):
    with open(name, "r", errors="replace") as f:
        lines = f.readlines()
        return lines


def sync_rewrite_file(name: str, lines: list):
    with open(name, "w", errors="replace") as f:
        f.writelines(lines)


# Doc code : remove_doc_lines
# returns the file lines with the doc comments removed and the code
# of every section intact, with clean_all every doc tag, description
# block and doc end is dropped, otherwise only the doc end lines

def remove_doc_lines(lines: list, ctx: dict, clean_all: bool) -> list:
    tag_re = ctx["tag_re"]
    doc_end_re = ctx["doc_end_re"]
    single_line_re = ctx["single_line_re"]
    mult_start_re = ctx["mult_start_re"]
    mult_close_re = ctx["mult_close_re"]
    mstart = ctx["mstart"]
    mult_derived = ctx["mult_derived"]

    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # a doc end line is a doc comment in both modes
        if doc_end_re.match(line):
            i += 1
            continue

        tag = tag_re.match(line)
        if not tag:
            result.append(line)
            i += 1
            continue

        # a doc section starts here
        if not clean_all:
            # only the doc end lines are being removed, keep the tag line
            result.append(line)
            i += 1
            continue

        # drop the tag line and the doc comment block
        i += 1

        is_code = tag.group("code") is not None or not tag.group("desc").strip()

        # drop the blank lines between the tag and the description block
        while i < n and not lines[i].strip():
            i += 1
        if i >= n:
            continue

        # drop the leading description block, either a real multiline
        # comment block or a run of single line comments
        if mult_start_re.match(lines[i]):
            if mult_derived:
                while i < n and single_line_re.match(lines[i]):
                    i += 1
            else:
                pos = lines[i].find(mstart)
                rest = lines[i][pos + len(mstart):]
                if not mult_close_re.search(rest):
                    i += 1
                    while i < n and not mult_close_re.search(lines[i]):
                        i += 1
                    if i < n:
                        i += 1
                else:
                    i += 1
        else:
            while i < n and single_line_re.match(lines[i]):
                i += 1

        if not is_code:
            # a plain doc section is made of comment lines only, drop them all
            while i < n:
                line = lines[i]
                if tag_re.match(line) or doc_end_re.match(line):
                    break
                if single_line_re.match(line):
                    i += 1
                else:
                    result.append(line)
                    i += 1

    return result


# Doc code : clean_file
# rewrites the source file without the doc comments, with clean_all
# every doc tag, description block and doc end is removed, otherwise
# only the doc end lines are removed

async def clean_file(name: str, clean_all: bool):
    ctx = make_comment_regexes(pathlib.Path(name).suffix)
    if ctx is None:
        return

    lines = await asyncio.to_thread(sync_read_file, name)
    cleaned = remove_doc_lines(lines, ctx, clean_all)

    if cleaned != lines:
        await asyncio.to_thread(sync_rewrite_file, name, cleaned)


# Doc code : make_comment_regexes
# resolves the comment family of a file extension and builds every
# regex needed to recognize doc comments in that family,
# returns None for unsupported extensions

def make_comment_regexes(f_type: str) -> dict | None:
    com = GetCommentFamily(f_type)
    single = com.single_line
    mult = com.mult_pair

    if single is None and mult is None:
        return None

    mstart = mclose = None
    if mult is not None:
        mstart = mult.start
        mclose = mult.close

    # NOTE: languages with only a multiline comment family use the pair as a
    # single line comment too (e.g. html <!-- -->)
    single_close = None
    if single is None:
        single = mstart
        single_close = mclose

    # NOTE: languages with only a single line comment family use it as the
    # multiline pair too
    mult_derived = mult is None
    if mstart is None:
        mstart = single
        mclose = single

    # NOTE: both families are guaranteed to be set by now, narrow for the checker
    assert single is not None
    assert mstart is not None and mclose is not None

    esc_single = re.escape(single)
    if single_close is not None:
        opt_close = rf"(?:{re.escape(single_close)})?"
    else:
        opt_close = ""

    return {
        # match a full single line comment
        "single_line_re": re.compile(rf"^\s*{esc_single}(.*)$"),
        # match a doc tag line, the code group is set for "Doc code :" and the
        # desc is the text after the colon, a bare "Doc" also matches with no
        # description
        "tag_re": re.compile(
            rf"^\s*{esc_single}\s*[Dd]oc(?P<code>\s+[Cc]ode)?\s*:?\s*(?P<desc>.*?)\s*{opt_close}?\s*$"
        ),
        # match a doc end single line comment
        "doc_end_re": re.compile(rf"^\s*{esc_single}\s*[Dd]oc\s+end\s*{opt_close}?\s*$"),
        # strips a single-line comment marker from the front of a line
        "strip_single_re": re.compile(rf"^\s*{esc_single}\s?(.*)$"),
        # matches a line that opens a multiline block comment
        "mult_start_re": re.compile(rf"^\s*{re.escape(mstart)}"),
        # matches a line containing the closing delimiter
        "mult_close_re": re.compile(re.escape(mclose)),
        # strips a multiline open marker from the front / close marker from the end
        "strip_mstart_re": re.compile(rf"^\s*{re.escape(mstart)}\s?"),
        "strip_mclose_re": re.compile(rf"\s?{re.escape(mclose)}\s*$"),
        "mstart": mstart,
        "mult_derived": mult_derived,
    }


# Doc code : read_file
# parses a file looking for doc comments and returns the
# markdown text for it, or None if the file is unsupported
# or has no doc comments


async def read_file(name: str) -> str | None:
    ctx = make_comment_regexes(pathlib.Path(name).suffix)

    # unsupported file, drop it from the work list
    if ctx is None:
        await remove_item_from_list(name)
        return None

    single_line_re = ctx["single_line_re"]
    tag_re = ctx["tag_re"]
    doc_end_re = ctx["doc_end_re"]
    mult_start_re = ctx["mult_start_re"]
    mult_close_re = ctx["mult_close_re"]
    strip_single_re = ctx["strip_single_re"]
    strip_mstart_re = ctx["strip_mstart_re"]
    strip_mclose_re = ctx["strip_mclose_re"]
    mstart = ctx["mstart"]
    mult_derived = ctx["mult_derived"]

    lines = await asyncio.to_thread(sync_read_file, name)

    def strip_line(line: str):
        text = line.rstrip("\n")
        if strip_mstart_re.match(text):
            text = strip_mstart_re.sub("", text)
        else:
            m = strip_single_re.match(text)
            if m:
                return m.group(1)
        if strip_mclose_re is not None:
            text = strip_mclose_re.sub("", text)
        return text

    # NOTE: find where a doc section ends (next tag, doc end, or EOF)
    def section_end(start: int, n: int):
        j = start
        while j < n:
            line = lines[j]
            if doc_end_re.match(line) or tag_re.match(line):
                return j - 1
            j += 1
        return n - 1

    # NOTE: extract a leading multiline comment block from content,
    # returns (index of the block's last line, text lines to emit) or (-1, [])
    def extract_block(content: list, k: int):
        if k >= len(content) or not mult_start_re.match(content[k]):
            return -1, []

        if mult_derived:
            # NOTE: languages without a real multiline pair treat a run of
            # single line comments as the block
            t = k
            while t < len(content) and single_line_re.match(content[t]):
                t += 1
            block_end = t - 1
        else:
            first = content[k]
            pos = first.find(mstart)
            rest = first[pos + len(mstart) :]

            if mult_close_re.search(rest):
                block_end = k
            else:
                t = k + 1
                while t < len(content) and not mult_close_re.search(content[t]):
                    t += 1
                block_end = t if t < len(content) else len(content) - 1

        emit = []
        for src in content[k : block_end + 1]:
            text = strip_line(src)
            if text.strip():
                emit.append(text + "  ")
        return block_end, emit

    lang_hint = pathlib.Path(name).suffix.lstrip(".") if pathlib.Path(name).suffix else ""

    md_lines = [f"# {name}", ""]
    i = 0
    n = len(lines)
    found_any = False

    while i < n:
        if doc_end_re.match(lines[i]):
            i += 1
            continue

        tag_match = tag_re.match(lines[i])
        if not tag_match:
            i += 1
            continue

        found_any = True

        is_code = tag_match.group("code") is not None
        description = tag_match.group("desc").strip()

        # NOTE: a bare "Doc" with no description captures its content as code
        # without adding a heading
        if not description:
            is_code = True

        end_idx = section_end(i + 1, n)

        if description:
            md_lines.append(f"## {description}")
            md_lines.append("")

        content = lines[i + 1 : end_idx + 1]

        if not is_code:
            # plain doc text made of comment lines
            emit_text = []
            k = 0
            while k < len(content) and not content[k].strip():
                k += 1

            if k < len(content):
                block_end, emit = extract_block(content, k)
                if block_end >= 0:
                    emit_text.extend(emit)
                    k = block_end + 1

            while k < len(content) and single_line_re.match(content[k]):
                text = strip_line(content[k])
                if text.strip():
                    emit_text.append(text + "  ")
                k += 1

            if emit_text:
                md_lines.extend(emit_text)
                md_lines.append("")

        else:
            # code section, a leading multiline comment block becomes the
            # description text and the rest is emitted verbatim in a fence
            k = 0
            while k < len(content) and not content[k].strip():
                k += 1

            if k < len(content):
                block_end, emit = extract_block(content, k)
                if block_end >= 0:
                    md_lines.extend(emit)
                    md_lines.append("")
                    k = block_end + 1

            code = [src.rstrip("\n") for src in content[k:]]
            while code and not code[0].strip():
                code.pop(0)
            while code and not code[-1].strip():
                code.pop()

            if code:
                md_lines.append(f"```{lang_hint}")
                md_lines.extend(code)
                md_lines.append("```")
                md_lines.append("")

        i = end_idx + 1

    # NOTE: no doc comments of any kind were found in the file
    if not found_any:
        return None

    md_text = "\n".join(md_lines).rstrip() + "\n"
    return md_text


# Doc code : worker
# parses a file, waits until it is the worker's turn to write and
# then writes the markdown to the output file, it can also clean
# the doc comments out of the source file if asked for


async def worker(filename: str, clean: bool = False, clean_all: bool = False):
    # read the contents of the file
    md = await read_file(filename)

    # finish if you found nothing, drop the file from the order list
    # so it never blocks the workers behind it
    if md is None:
        await remove_item_from_list(filename)
        return

    # clean the doc comments out of the source file if asked for
    if clean or clean_all:
        await clean_file(filename, clean_all)

    # wait until it's this worker's turn to write
    async with cond:
        await cond.wait_for(lambda: l and l[0] == filename)

    await write_file(md, out)


# Doc end


# Doc code : dispatcher thread
# sets up the order list and the output file, then starts one
# worker task per file and waits for all of them to finish, the
# clean flags are passed to every worker


async def dispatch(list_files: list, out_path: str, clean: bool, clean_all: bool):
    global l
    l = list_files
    global out
    out = out_path

    # truncate the output file once so reruns don't duplicate
    # the previous docs, workers still append afterwards
    # its fine here since there is only the dispatcher running
    open(out_path, "w").close()

    # create tasks for every file in the list and don't finish without them
    gathered_tasks = [
        asyncio.create_task(worker(filename, clean, clean_all))
        for filename in list_files
    ]
    await asyncio.gather(*gathered_tasks)


# Doc end
