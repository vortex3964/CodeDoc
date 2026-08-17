# ./langs.py

## Description

lists every supported language and casts each file extension  
to a general comment family  

## MultCommentPair

start and close delimiters of a multiline comment pair  

```py
@dataclass
class MultCommentPair:
    start: str | None
    close: str | None
```

## Logic of the dictionaries

the main idea is that we have dictionaries that point  
to the way comments start for the programming languages  
and appoint a leader (the standard they follow) to access those  
we do the same for multiline comments and then we have 2 more  
dictionaries to convert file extensions to the appropriate  
comment family the language follows so they can get access  
to the syntax of the comments for example:  
.cpp, .c, .rs map to the c-family comments (c key) and  
we use the key to access the comment syntax c maps to // or /* */  

## comment families and conversion tables

single_comments holds the keys that lead to the right syntax for single line comments  
mult_comments does the same but for multiline comments  
conv_table_single converts different filetypes to comment families for single line comments  
conv_table_mult does the same as conv_table_single but for multi line comments  
some languages map to different multiline comments and single line comments or don't have them  

## CommentFam

the single and multiline comment families of a language  
used in GetCommentFamily to return the comment syntax  
to parser.py so that it can use regex operations to parse  
the files  

## GetCommentFamily

looks up the comment families of a file extension in the  
conversion tables, can return None, None for unknown extensions  

```py
def GetCommentFamily(type: str) -> CommentFam:
    single = None
    mult = None

    fam_single = conv_table_single.get(type)
    if fam_single is not None:
        single = single_comments.get(fam_single)

    fam_mult = conv_table_mult.get(type)
    if fam_mult is not None:
        mult = mult_comments.get(fam_mult)

    return CommentFam(single, mult)
```
# ./main.py

## Description

main.py processes the command line flags and starts the  
dispatcher to generate the documentation, it also checks  
for updates at the end of every run and can update itself  

## list of ignored directories, extensions and files

we keep lists called IGNORE_DIRS IGNORE_EXTENSIONS IGNORE_FILES of the  
files we would like to ignore like hidden files (.git) or .exe files we  
shouldn't bother reading  

## recursive listing of all the files in the directories

walks the root directory recursively and returns the sorted  
list of files to parse, skipping the ignored directories,  
extensions, files and the user excluded ones  

```py
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
```

## update helpers

the update check compares the installed copy against the latest  
commit on github, it runs at the end of main so the file reading  
is never slowed down by the network, it stays quiet when there  
is no connection or a rate limit and it skips dev checkouts  

## main

parses the command line arguments, builds the file list and  
starts the dispatcher, the update flag only updates the tool  
itself and skips the documentation run
# ./parser.py

## Description

thread pool and parsing logic that turns doc comments into  
markdown, dispatch runs one worker per file  

## global variables we reuse for multithreading

shared resource to keep track of file order so that files are  
written properly and sorted as we do it in main  

```py
l = []
out = ""

# this is the lock to make sure that only one file ever writes to the
# output folder that's a shared resource
file_lock = asyncio.Lock()

# condition for stopping the wait cycle in worker, it also guards the
# shared list l so that waiters wake up when the head changes
cond = asyncio.Condition()
```

## remove_head_from_list

pops the first entry of the order list and wakes up the  
workers waiting for their turn  

```py
async def remove_head_from_list():
    global l
    async with cond:
        if len(l) != 0:
            l.pop(0)
        cond.notify_all()
```

## remove_item_from_list

removes an entry from the order list without blocking the  
queue, used for files that produced no output  

## sync_write_file

the write is a sync task so we need a helper function  
run in a thread so we don't wait synchronously for the  
i/o to finish every time and freeze the event loop  

## write_file

appends the markdown of a file to the output file, the  
file lock serializes the writers so only the head of the  
order list writes at a time  

## sync_read_file

sync file read helper, runs in a thread by read_file  

## remove_doc_lines

returns the file lines with the doc comments removed and the code  
of every section intact, with clean_all every doc tag, description  
block and doc end is dropped, otherwise only the doc end lines  

## clean_file

rewrites the source file without the doc comments, with clean_all  
every doc tag, description block and doc end is removed, otherwise  
only the doc end lines are removed  

```py
async def clean_file(name: str, clean_all: bool):
    ctx = make_comment_regexes(pathlib.Path(name).suffix)
    if ctx is None:
        return

    lines = await asyncio.to_thread(sync_read_file, name)
    cleaned = remove_doc_lines(lines, ctx, clean_all)

    if cleaned != lines:
        await asyncio.to_thread(sync_rewrite_file, name, cleaned)
```

## make_comment_regexes

resolves the comment family of a file extension and builds every  
regex needed to recognize doc comments in that family,  
returns None for unsupported extensions, the result is cached  
per extension so that files of the same language don't rebuild it  

## read_file

parses a file looking for doc comments and returns the  
markdown text for it, or None if the file is unsupported  
or has no doc comments  

## end or EOF, the lines in between are the section content

## worker

parses a file, waits until it is the worker's turn to write and  
then writes the markdown to the output file, it can also clean  
the doc comments out of the source file if asked for  

```py
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
```

## dispatcher thread

sets up the order list and the output file, then starts one  
worker task per file and waits for all of them to finish, the  
clean flags are passed to every worker  

```py
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
```
