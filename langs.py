# DESC: has every supported lang and casts its extension to a general comment family

from dataclasses import dataclass


# NOTE: used to keep
@dataclass
class MultCommentPair:
    start: str | None
    close: str | None


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
    # haskel
    **dict.fromkeys([".hs"], "haskell"),
    # html
    **dict.fromkeys([".html", ".htm", ".xhtml", ".xml"], "html"),
    # pascal
    **dict.fromkeys([".pas", ".pp", ".inc", ".fs"], "pascal"),
    # matlab has different multiline comments
    ".m": "matlab",
}


# NOTE: we use this to cast single and multiline comments of a lib to another
@dataclass
class CommentFam:
    single_line: str | None
    mult_pair: MultCommentPair | None


# returns the comment family the language belongs to
# WARN: can return None,None so better handle it
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
