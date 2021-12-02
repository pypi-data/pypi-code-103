PERMISSIVE_BLOCK_REGEX = r"block:[^\}]{6,}"
BLOCK_REGEX = r"block:[A-Za-z0-9]{3,}/[A-Za-z0-9]{3,}/[0-9]+"
UNPINNED_BLOCK_REGEX_ENDLINE = r"block:[A-Za-z0-9]{3,}/[A-Za-z0-9]{3,}$"
UNPINNED_BLOCK_REGEX_INLINE = r"block:[A-Za-z0-9]{3,}/[A-Za-z0-9]{3,}(?=[\s,}])"
GROUPED_BLOCK_REGEX = r"block:([A-Za-z0-9]{3,})/([A-Za-z0-9]{3,})/*([0-9]*)"

PERMISSIVE_OXA_REGEX = r"oxa:[^\}]{3,}"
OXA_REGEX = r"oxa:[A-Za-z0-9]{3,}/[A-Za-z0-9]{3,}\.[0-9]+"
UNPINNED_OXA_REGEX_ENDLINE = r"oxa:[A-Za-z0-9]{3,}/[A-Za-z0-9]{3,}$"
UNPINNED_OXA_REGEX_INLINE = r"oxa:[A-Za-z0-9]{3,}/[A-Za-z0-9]{3,}(?=[\s,}])"

# produces 2 or 3 groups
P1B2V_GROUPED_OXA_REGEX = r"oxa:([A-Za-z0-9]{3,})/([A-Za-z0-9]{3,})\.*([0-9]*)"

# produces 3 or 5 groups
P1B1VB2V_GROUPED_OXA_REGEX = r"oxa:([A-Za-z0-9]{3,})/([A-Za-z0-9]{3,})\.([0-9]+):([A-Za-z0-9]{3,})\.([0-9]+)[#0-9a-zA-Z]*$"

# produces 4 or 6 groups
# P1B1VP2B2V_GROUPED_OXA_REGEX = r"oxa:([A-Za-z0-9]{3,})/([A-Za-z0-9]{3,})\.*([0-9]*):([A-Za-z0-9]{3,})\.*([0-9]*)"

GROUPED_OXA_REGEX = P1B2V_GROUPED_OXA_REGEX

EXTRACT_UNPINNED_OXA_REGEX = r"(.*oxa:.{6,})\.[0-9#a-zA-Z]+"

CAPTION_BLOCK_REGEX = rf"{PERMISSIVE_BLOCK_REGEX}\.caption"
CAPTION_OXA_REGEX = rf"{PERMISSIVE_OXA_REGEX}\.caption"

INLINE_IMAGE_BLOCK_REGEX = (
    r".*\\includegraphics.*{(" + PERMISSIVE_BLOCK_REGEX + r")}.*\\*"
)
INLINE_IMAGE_OXA_REGEX = r".*\\includegraphics.*{(" + PERMISSIVE_OXA_REGEX + r")}.*\\*"

CAPTION_COMMAND_BLOCK_REGEX = r".*\\caption{(" + CAPTION_BLOCK_REGEX + r")}.*\\*"
CAPTION_COMMAND_OXA_REGEX = r".*\\caption{(" + CAPTION_OXA_REGEX + r")}.*\\*"
LABEL_COMMAND_REGEX = r".*\\label{([A-Za-z0-9_-]*)}.*\\*"
HREF_COMMAND_OXA_REGEX = r"\\href{(" + PERMISSIVE_OXA_REGEX + r")}"
REF_COMMAND_OXA_REGEX = r"\\ref{(" + PERMISSIVE_OXA_REGEX + r")}"

OUTPUT_IMAGE_BLOCK_REGEX = (
    r".*\\includegraphics.*{(" + PERMISSIVE_BLOCK_REGEX + r"-output-[0-9]+)}.*\\*"
)
OUTPUT_IMAGE_OXA_REGEX = (
    r".*\\includegraphics.*{(" + PERMISSIVE_OXA_REGEX + r"-output-[0-9]+)}.*\\*"
)

OUTPUT_SVG_BLOCK_REGEX = (
    r".*\\includesvg.*{(" + PERMISSIVE_BLOCK_REGEX + r"-output-[0-9]+)}.*\\*"
)
OUTPUT_SVG_OXA_REGEX = (
    r".*\\includesvg.*{(" + PERMISSIVE_OXA_REGEX + r"-output-[0-9]+)}.*\\*"
)

INLINE_CITATION_BLOCK_REGEX = r"\\cite[pt]?{(" + PERMISSIVE_BLOCK_REGEX + r")}"
INLINE_CITATION_OXA_REGEX = r"\\cite[pt]?{(" + PERMISSIVE_OXA_REGEX + r")}"

## FULL URLS
OXA_LINK = r"oxa:([a-zA-Z0-9]+)/([a-zA-Z0-9]+)\.([0-9]+)"
FULL_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)/([a-zA-Z0-9]{1}[a-zA-Z0-9-]+)/([!a-zA-Z0-9]{1}[a-zA-Z0-9-]+)\.([0-9]+)"
PINNED_BLOCK_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)/([a-zA-Z0-9]{1}[a-zA-Z0-9-]+)/([!a-zA-Z0-9]{1}[a-zA-Z0-9-]+)"
PROJECT_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)/([a-zA-Z0-9-]+)"
TEAM_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)"
