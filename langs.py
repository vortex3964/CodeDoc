# Doc : Description
# lists every supported language and casts each file extension
# to a general comment family

from dataclasses import dataclass

# Doc code : MultCommentPair
# start and close delimiters of a multiline comment pair


@dataclass
class MultCommentPair:
    start: str | None
    close: str | None

#Doc end

#Doc: Logic of the dictionaries
# the main idea is that we have dictionaries that point
# to the way comments start for the programming languages
# and appoint a leader (the standard they follow) to access those
# we do the same for multiline comments and then we have 2 more
# dictionaries to convert file extensions to the appropriate
# comment family the language follows so they can get access
# to the syntax of the comments for example:
# .cpp, .c, .rs map to the c-family comments (c key) and
# we use the key to access the comment syntax c maps to // or /* */

# Doc : comment families and conversion tables
# single_comments holds the keys that lead to the right syntax for single line comments
# mult_comments does the same but for multiline comments
# conv_table_single converts different filetypes to comment families for single line comments
# conv_table_mult does the same as conv_table_single but for multi line comments
# some languages map to different multiline comments and single line comments or don't have them

# NOTE: these are the major single line comment families we support
single_comments = {
    "c": "//",
    "python": "#",
    "lua": "--",
    "assembly": ";",
    "visual_basic": "'",
    "latex": "%",
}

# NOTE: these are the major multi line comment families we support
mult_comments = {
    "c": MultCommentPair(start="/*", close="*/"),
    "python": MultCommentPair(start='"""', close='"""'),
    "lua": MultCommentPair(start="--[[", close="]]"),
    "haskell": MultCommentPair(start="{-", close="-}"),
    "html": MultCommentPair(start="<!--", close="-->"),
    "pascal": MultCommentPair(start="(*", close="*)"),
    "matlab": MultCommentPair(start="%{", close="}%"),
}

# NOTE: the dictionary we use to convert a file to a file type that we use as a key for single line comments
conv_table_single = {
    # c family
    **dict.fromkeys(
        [
            ".c",
            ".h",
            ".cpp",
            ".cc",
            ".cxx",
            ".hpp",
            ".hh",
            ".cs",
            ".java",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".d",
            ".swift",
            ".kt",
            ".kts",
            ".php",
            ".dart",
            ".scala",
            ".pas",
            ".pp",
            ".inc",
            ".mm",
            ".fs",
            ".zig",
        ],
        "c",
    ),
    # python family
    **dict.fromkeys([".py", ".pyw", ".pyi", ".erlang"], "python"),
    # lua family
    **dict.fromkeys([".lua", ".hs"], "lua"),
    # asm family
    **dict.fromkeys([".asm", ".s"], "assembly"),
    # visual basic
    **dict.fromkeys([".vb", ".vbs", ".bas"], "visual_basic"),
    # latex
    **dict.fromkeys([".tex", ".sty", ".cls", ".m"], "latex"),
}

# NOTE: the dictionary we use to convert a file to a file type that we use as a key for multi line comments
conv_table_mult = {
    **dict.fromkeys(
        [
            ".c",
            ".h",
            ".cpp",
            ".cc",
            ".cxx",
            ".hpp",
            ".hh",
            ".cs",
            ".java",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".d",
            ".swift",
            ".kt",
            ".kts",
            ".php",
            ".dart",
            ".scala",
            ".mm",
        ],
        "c",
    ),
    # python
    **dict.fromkeys([".py", ".pyw", ".pyi"], "python"),
    # lua
    **dict.fromkeys([".lua"], "lua"),
    # haskell
    **dict.fromkeys([".hs"], "haskell"),
    # html
    **dict.fromkeys([".html", ".htm", ".xhtml", ".xml"], "html"),
    # pascal
    **dict.fromkeys([".pas", ".pp", ".inc", ".fs"], "pascal"),
    # matlab has different multiline comments
    ".m": "matlab",
}


# Doc : CommentFam
# the single and multiline comment families of a language
# used in GetCommentFamily to return the comment syntax
# to parser.py so that it can use regex operations to parse
# the files

@dataclass
class CommentFam:
    single_line: str | None
    mult_pair: MultCommentPair | None


# Doc code : GetCommentFamily
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


# Doc end
