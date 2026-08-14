# ./langs.py

## Description

lists every supported language and casts each file extension  
to a general comment family  

## MultCommentPair

```py
# start and close delimiters of a multiline comment pair


@dataclass
class MultCommentPair:
    start: str | None
    close: str | None
```

## Logic of the dictionarys

the main idea is that we have dictionaries that point  
to the way comments start for the programming languages  
and appoint a leader (the standard they follow) to access those  
we do the same for multiline comments and then we have 2 more  
dictionaries to convert file extensions to the apropriate   
comment family the language follows so they can get access   
to the syntax of the comments for example:  
.cpp , .c , .rs maps to the c-family comments (c key) and   
and we use the key to access the comment syntax c maps to // or {* *}  

## comment families and conversion tables

single_comments holds the keys that lead to the right syntax for single line comments  
mult_comments does the same but for multiline comments  
conv_table_single converts diferent filetypes to comment families for single line comments  
conv_table_mult does the same as conv_table_single but for multi line comments   
some languages map to diferent multiline comments and single line comments or dont have them  

## CommentFam

the single and multiline comment families of a language  
used in GetCommentFamily to return the comment sayntax   
to parser.py so that it can use regex operations to parse  
the files  

## GetCommentFamily

```py
# looks up the comment families of a file extension in the
# conversion tables, can return None, None for unknown extensions


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
dispatcher to generate the documentation  

## list of ignored directories, extensions and files

we keep lists called IGNORE_DIRS IGNORE_EXTENSIONS IGNORE_FILES of the  
files we would like to ignore like hiden files(.git) or .exe files we  
shouldnt bothe reading  

## recursive listing of all the files in the directories

```py
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
```

## main

parses the command line arguments, builds the file list and  
starts the dispatcher
# ./parser.py

## Description

thread pool and parsing logic that turns doc comments into  
markdown, dispatch runs one worker per file  

## global variables we reuse for multithreading

```py
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
```

## remove_head_from_list

```py
# pops the first entry of the order list and wakes up the
# workers waiting for their turn


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

## read_file

parses a file looking for doc comments and returns the  
markdown text for it, or None if the file is unsupported  
or has no doc comments  

## worker

```py
# parses a file, waits until it is the worker's turn to write
# and then writes the markdown to the output file


async def worker(filename: str):
    # read the contents of the file
    md = await read_file(filename)

    # finish if you found nothing, drop the file from the order list
    # so it never blocks the workers behind it
    if md is None:
        await remove_item_from_list(filename)
        return

    # wait until it's this worker's turn to write
    async with cond:
        await cond.wait_for(lambda: l and l[0] == filename)

    await write_file(md, out)
```

## dispatcher thread

```py
# sets up the order list and the output file, then starts one
# worker task per file and waits for all of them to finish


async def dispatch(list_files: list, out_path: str, _clean: bool):
    global l
    l = list_files
    global out
    out = out_path

    # truncate the output file once so reruns don't duplicate
    # the previous docs, workers still append afterwards
    open(out_path, "w").close()

    # create tasks for every file in the list and don't finish without them
    gathered_tasks = [asyncio.create_task(worker(filename)) for filename in list_files]
    await asyncio.gather(*gathered_tasks)
```
