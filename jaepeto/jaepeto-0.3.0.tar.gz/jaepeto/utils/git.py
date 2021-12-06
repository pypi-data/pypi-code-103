import re
import subprocess
from datetime import datetime

leading_4_spaces = re.compile("^    ")


def get_commits():
    """
    Notes
    -----
    https://gist.github.com/simonw/091b765a071d1558464371042db3b959
    """
    lines = (
        subprocess.check_output(["git", "log", "--stat"], stderr=subprocess.STDOUT)
        .decode("utf-8")
        .split("\n")
    )

    commits = []
    current_commit = {}

    def save_current_commit():
        title = current_commit["message"][0]
        message = current_commit["message"][1:]
        changed_files = []

        if message and message[0] == "":
            del message[0]

        current_commit["title"] = title
        current_commit["message"] = "\n".join(message)
        current_commit["files"] = [
            _m.split("|")[0].strip() for _m in message if "|" in _m
        ]
        commits.append(current_commit)

    for line in lines:
        if not line.startswith(" "):
            if line.startswith("commit "):
                if current_commit:
                    save_current_commit()
                    current_commit = {}
                current_commit["hash"] = line.split("commit ")[1]
            else:
                try:
                    key, value = line.split(":", 1)
                    current_commit[key.lower()] = value.strip()
                except ValueError:
                    pass
        else:
            current_commit.setdefault("message", []).append(
                leading_4_spaces.sub("", line)
            )

    if current_commit:
        save_current_commit()

    commits.reverse()  # earliest commit first
    return commits


def find_earliest_commit_with_file(file: str, commits):
    # Assume commits are ordered earliest to latest
    for commit in commits:
        for commit_file in commit["files"]:
            if file in commit_file.lower():
                # Accepts partial match e.g. .travis -> .travis.yml
                return convert_datetime_to_date_string(commit["date"])

    raise RuntimeError(f"No commits involve file {file}")


def get_diff_for_file(file: str, commits):
    changes = []

    for i in range(1, len(commits)):
        main_commit = commits[i]

        if file not in main_commit["files"]:
            continue

        previous_commit_hash = commits[i - 1]["hash"]
        main_commit_hash = main_commit["hash"]

        lines = (
            subprocess.check_output(
                ["git", "diff", previous_commit_hash, main_commit_hash, file],
                stderr=subprocess.STDOUT,
            )
            .decode("utf-8")
            .split("\n")
        )

        lines = [l for l in lines if re.match("[+-][a-zA-Z]", l)]

        formatted_date = convert_datetime_to_date_string(main_commit["date"])
        changes.append((main_commit_hash, formatted_date, lines))

    return changes


def convert_datetime_to_date_string(datetime_string):
    return datetime.strptime(datetime_string, "%a %b %d %H:%M:%S %Y %z").strftime(
        "%Y-%m-%d"
    )


def get_line_changes_for_file(file: str):
    lines = (
        subprocess.check_output(
            ["git", "log", "--stat", '--since="4 weeks ago"', "--", file],
            stderr=subprocess.STDOUT,
        )
        .decode("utf-8")
        .split("\n")
    )

    commits = []
    current_commit = {}

    def _save_current_commit():
        title = current_commit["message"][0]
        message = current_commit["message"][1:]
        changed_files = []

        if message and message[0] == "":
            del message[0]

        current_commit["title"] = title
        commit_message = "\n".join(message)

        _added = re.search("([0-9]+) insertion", commit_message)
        _removed = re.search("([0-9]+) deletion", commit_message)

        if _added:
            lines_added = int(_added.group(1))
        else:
            lines_added = 0
        if _removed:
            lines_removed = int(_removed.group(1))
        else:
            lines_removed = 0

        commits.append((lines_added, lines_removed, current_commit["author"]))

    for line in lines:
        if not line.startswith(" "):
            if line.startswith("commit "):
                if current_commit:
                    _save_current_commit()
                    current_commit = {}
                current_commit["hash"] = line.split("commit ")[1]
            else:
                try:
                    key, value = line.split(":", 1)
                    current_commit[key.lower()] = value.strip()
                except ValueError:
                    pass
        else:
            current_commit.setdefault("message", []).append(
                leading_4_spaces.sub("", line)
            )

    if current_commit:
        _save_current_commit()

    authors = [c[2] for c in commits]
    if authors:
        common_author = max(set(authors), key=authors.count)
    else:
        common_author = None

    return sum([c[0] for c in commits]), sum([c[1] for c in commits]), common_author
