from pdx import utility_service
from pdx import Session
from pdx import Console
from pdx import Executor
from pdx.git import utility
import os
import re

# Console shared by all commands
out = Console.get()

# If remote is PSU BitBucket, and not on PSU network, then remote functions will be disabled.
# To avoid the same warning being repeated many times, only print it once, and remember that it was printed
on_psu_network = utility_service.is_on_psu_network()
Session.data['remote_disabled_warning_printed'] = False


def remote_disabled(remote_name="origin", skip_remote_check=False):
    exe = utility.run_git_cmd(["git", "config", "--get", "remote.{0}.url".format(remote_name)], "debug")
    remote_url = exe.get_output() if exe.return_code == 0 else None
    del exe

    # =========================================
    # Disabled when no remote is defined, unless skipping remote check
    # =========================================
    if (remote_url is None or remote_url.strip() == "") and not skip_remote_check:
        # Warn about disabled remote (only once)
        if not Session.data['remote_disabled_warning_printed']:
            out.put_warning(
                "No remote has been defined. Git remote functions (fetch/push/pull/clone) have been disabled."
            )
            Session.data['remote_disabled_warning_printed'] = True
        return True

    # =========================================
    # Never disabled when on PSU network
    # =========================================
    if on_psu_network:
        return False

    # =========================================
    # Only disabled if remote points to PSU BitBucket, or skipping remote check
    # =========================================
    elif skip_remote_check or (".pdx.edu" in remote_url):
        # Warn about disabled remote (only once)
        if not Session.data['remote_disabled_warning_printed']:
            out.put_warning(
                "You are not on the PSU network. Git remote functions (fetch/push/pull/clone) have been disabled."
            )
            Session.data['remote_disabled_warning_printed'] = True
        # Yes, remote is disabled
        return True

    # =========================================
    # Otherwise, not disabled
    # =========================================
    else:
        return False


def is_repo():
    """Is the current directory in a Git repository?"""
    out.trace("is_repo", [])
    exe = Executor.Executor("git rev-parse --show-toplevel")
    return exe.return_code == 0


def current_branch(show_tag_when_detached=False):
    """Get the current Git branch"""
    out.trace("current_branch", [])
    branch_name = None

    # Run command to get current branch
    exe = Executor.Executor(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

    # If command was successful
    if exe.return_code == 0:
        branch_name = exe.get_output()

        # if on detached HEAD, and tag name is desired
        if branch_name == 'HEAD' and show_tag_when_detached:
            exe = Executor.Executor("git branch")
            output = exe.get_output()
            # * (HEAD detached at v0.1)
            # * (HEAD detached at 4c6a3a3)
            pattern = re.compile(r'^\*\s+\(HEAD detached at (\S+)\)', re.IGNORECASE)
            for line in output.splitlines():
                matcher = pattern.match(line)
                if matcher:
                    branch_name = matcher.group(1)
            del pattern
            del output

        elif branch_name.startswith("heads/") and show_tag_when_detached:
            branch_name = branch_name.replace("heads/", "")

    del exe
    return branch_name


def checkout_branch(branch_name, create_from="master"):
    """Checkout the given Git branch"""
    # if already on selected branch, return true
    if current_branch(True) == branch_name:
        return True

    out.trace("checkout_branch", [branch_name, create_from])

    # Create the branch if it does not exist (if create_from is not None or False)
    if create_from and not any_branch_exists(branch_name):
        create_branch(branch_name, create_from)

    utility.run_git_cmd(['git', 'checkout', branch_name])

    # Return true if currently on the branch to be checked out
    return branch_name == current_branch(True)


def create_branch(branch_name, branch_from=None):
    """Get the current Git branch"""
    out.trace("create_branch", [branch_name, branch_from])

    # Check out the source branch, is specified (otherwise branch off current branch)
    if branch_from is not None:
        if not checkout_branch(branch_from):
            return False

    utility.run_git_cmd(['git', 'checkout', '-b', branch_name])

    return current_branch() == branch_name


def delete_branch(rm_branch):
    """Delete a local branch"""
    out.trace("delete_branch", [rm_branch])

    # Get a list of branches
    existing_branches = list_branches()

    # If branch to be deleted does not exist
    if rm_branch not in existing_branches:
        out.put_error("Cannot delete non-existing branch: {0}".format(rm_branch))
        return None

    # Get current branch
    this_branch = current_branch()

    # If deleting the current branch, need to checkout a different branch first
    if this_branch == rm_branch:
        # Use master branch, if possible
        switch_to = 'master'
        # If master is not an option
        if rm_branch == switch_to or switch_to not in existing_branches:
            switch_to = None
            # Use first existing branch that is not the branch being deleted
            for bb in existing_branches:
                if rm_branch != bb:
                    switch_to = bb
                    break
        # If a branch to switch to was determined, check it out now
        if switch_to is not None:
            checkout_branch(switch_to)

    # Get current branch
    this_branch = current_branch()

    # Delete the branch
    if this_branch != rm_branch:
        exe = utility.run_git_cmd(["git", "branch", "-D", rm_branch])
        return exe.return_code == 0

    # If no other branch could be checked out
    out.put_error(
        "Unable to delete '{0}' branch because no other branch could be checked out.".format(rm_branch)
    )
    return None


def list_branches():
    """Get a list of existing git branches"""
    out.trace("list_branches", [])
    branches = None

    exe = utility.run_git_cmd(["git", "branch"], 'debug')

    if exe.return_code == 0:
        output = exe.get_output()

        try:
            branches = list(output.split(os.linesep))
            branches = map(str.strip, branches)

            # Strip the * off of the current branch and filter out blank values
            branches = list(filter(None, [x.strip('* ') for x in branches]))

        except Exception as ee:
            out.put_error("Error processing branch output: {0}".format(ee))
            branches = None

    del exe
    return branches


def branch_exists(branch_name, include_tags=True):
    """Does git branch exist? Return True or False"""
    out.trace("branch_exists", [branch_name, include_tags])

    branch_list = list_branches()
    if include_tags:
        branch_list.extend(list_tags())

    return branch_name in branch_list


def list_all_branches(remote_name="origin"):
    """Get a list of existing local and remote Git branches"""
    out.trace("list_all_branches", [remote_name])

    git_cmd = ["git", "branch", "-a"]
    exe = utility.run_git_cmd(git_cmd, trace_level="debug")

    if exe.return_code == 0:
        output = exe.get_output()

        # If no branches, return empty list
        if output.strip() == "":
            return []

        try:
            branches = list(output.split(os.linesep))
            branches = map(str.strip, branches)

            # Strip and filter out blank values
            branches = list(filter(None, [x.strip() for x in branches]))

        except Exception as ee:
            out.put_error("Error processing branch output: {0}".format(ee))
            branches = None

        # List contains branches from (potentially) multiple remotes
        branch_list = []
        if type(branches) is list:
            for branch in branches:
                branch = branch.strip()

                if branch.startswith("remotes/"):
                    # Remove "remotes/"
                    branch_name = branch.replace('remotes/', '')

                    # Remove remote name
                    ii = branch_name.index('/')
                    # remote_name = branch_name[:ii]
                    branch_name = branch_name[ii+1:]

                    if not branch_name.startswith('HEAD'):
                        branch_list.append(branch_name)

                elif branch.startswith("*"):
                    branch_name = branch.replace('*', '').strip()
                    branch_list.append(branch_name)

                else:
                    branch_list.append(branch)

        return branch_list

    return None


def any_branch_exists(branch_name, include_tags=True):
    """Does local or remote git branch exist? Return True or False"""
    out.trace("any_branch_exists", [branch_name])

    branch_list = list_all_branches()
    if include_tags:
        branch_list.extend(list_tags())
    return branch_name in branch_list


def list_tags():
    """Get a list of existing git tags"""
    out.trace("list_tags", [])
    tags = None

    exe = utility.run_git_cmd(["git", "tag"], 'debug')

    if exe.return_code == 0:
        output = exe.get_output()

        try:
            tags = list(output.split(os.linesep))
            tags = map(str.strip, tags)

            # Strip and filter out blank values
            tags = list(filter(None, [x.strip() for x in tags]))

        except Exception as ee:
            out.put_error("Error processing tag output: {0}".format(ee))
            tags = None

    return tags


def tag_exists(tag_name):
    """Does git tag exist? Return True or False"""
    out.trace("tag_exists", [tag_name])
    return str(tag_name) in list_tags()


def delete_tag(tag_name, remote_name="origin"):
    """Delete a tag (local and remote)"""
    out.trace("delete_tag", [tag_name])

    # No need to delete a non-existing tag, but do print a warning
    if not tag_exists(tag_name):
        out.put_warning("Tag to be deleted does not exist: {0}".format(tag_name))
        return True

    # Delete local tag
    exe = utility.run_git_cmd(["git", "tag", "-d", tag_name])

    # If tag was deleted, also delete remote tag (which may or may not exist)
    if exe.return_code == 0 and not remote_disabled(remote_name):
        utility.run_git_cmd(["git", "push", remote_name, ":refs/tags/{0}".format(tag_name)])

    return exe.return_code == 0


def is_clean(allow_untracked=False):
    """Is the current Git repo/branch 'clean'?"""
    out.trace("is_clean", [])

    # Get status
    exe = utility.run_git_cmd(["git", "status"], trace_level="debug")

    if exe.return_code == 0:
        return (
            "working directory clean" in exe.get_output() or
            "nothing to commit" in exe.get_output() or
            (allow_untracked and "nothing added to commit but untracked files present" in exe.get_output())
        )
    else:
        return None


def is_unmodified():
    """Have changes been made to tracked files?"""
    return is_clean(True)


def status(branch_name=None):
    """Get the status of the current (or specified) Git branch"""
    out.trace("status", [branch_name])
    start_branch = current_branch()

    # Change to branch if one was given
    if branch_name is not None:
        if not checkout_branch(branch_name):
            out.put_error("Could not change to {0}".format(branch_name))
            checkout_branch(start_branch)
            return None

    # Get status, return None if it fails
    exe = utility.run_git_cmd(["git", "status"])

    checkout_branch(start_branch)
    return exe.get_output() if exe.return_code == 0 else None


def status_dict(branch_name=None):
    """Get the status of the current (or specified) Git branch"""
    out.trace("status_dict", [branch_name])

    # Get status
    output = status(branch_name)

    if output is None:
        return None

    status_map = {
        "branch": "",
        "to_commit": {"desc": "Ready to commit:", "items": []},
        "notstaged": {"desc": "Not staged for commit:", "items": []},
        "untracked": {"desc": "Untracked items:", "items": []},
        "conflicts": {"desc": "Conflicted items:", "items": []},
        "rebasing": {"desc": "Rebase in progress:", 'items': "You are currently rebasing branch" in output},
        "unclean": {"desc": "All uncommitted items:", "items": []},
        "errors": {"desc": "Errors:", "items": []}
    }
    pointer = "branch"

    # Format the status output
    rebase_in_progress = False
    for full_line in output.split("\n"):
        line = full_line.strip("# \t")

        try:
            # Is a rebase in progress
            if (not rebase_in_progress) and "You are currently rebasing branch" in line:
                rebase_in_progress = True

            # Figure out what this line is talking about
            if line.startswith("Changes to be committed"):
                pointer = "to_commit"
                continue
            if line.startswith("no changes added to commit"):
                pointer = "to_commit"
                continue
            if line.startswith("nothing added to commit"):
                pointer = "to_commit"
                continue
            if line.startswith("nothing to commit"):
                pointer = "to_commit"
                continue
            if line.startswith("Changes not staged"):
                pointer = "notstaged"
                continue
            if line.startswith("Unmerged paths"):
                pointer = "notstaged"
                continue
            if line.startswith("Untracked files"):
                pointer = "untracked"
                continue
            if line.startswith("("):
                continue
            if line == "":
                continue
            if line.startswith("On branch"):
                pointer = "branch"

            # Pull an item name out of this line
            parts = line.rsplit(":")
            if len(parts) == 2:
                itemname = parts[1].strip()
            else:
                itemname = parts[0].strip()

            # Put that item name into the appropriate list
            if pointer == "branch":
                status_map[pointer] = itemname

            else:
                # Conflicted files are grouped as "Not Staged" files
                if parts[0].strip() == "both modified":
                    status_map["conflicts"]["items"].append(itemname)
                elif parts[0].strip() == "both added":
                    status_map["conflicts"]["items"].append(itemname)
                # When rebasing, Unmerged paths are conflicts
                elif rebase_in_progress and pointer == 'notstaged':
                    status_map["conflicts"]["items"].append(itemname)
                # Otherwise, pointer should be accurate
                else:
                    status_map[pointer]["items"].append(itemname)

                # Add ALL items to the "unclean" pointer
                status_map['unclean']["items"].append(itemname)

        except Exception:
            status_map["errors"]["items"].append(line)
            # continue looping...

    return status_map


def diff_branches(into_branch=None, from_branch=None):
    """Show differences between two branches
    :param into_branch: If branches are to be merged in the future, this is the merge-into branch
    :param from_branch:  If branches are to be merged in the future, this is the merge-from branch
    :return: Dict of changes, with the type of change {A, M, D} as the map key containing a list of files
    """
    out.trace("diff_branches", [into_branch, from_branch])

    # Prepare arguments
    git_cmd = ['git', 'diff', '--name-status']

    # Add branch names as arguments
    if into_branch is not None:
        git_cmd.append(into_branch)
    if from_branch is not None:
        git_cmd.append(from_branch)

    # Prepare map of results
    changes = {
        "A": [],
        "M": [],
        "D": [],
        "status": False,
        "has_differences": False,
        "from_branch": from_branch,
        "into_branch": into_branch
    }

    # Run the command
    exe = utility.run_git_cmd(git_cmd)

    # If command failed, return now
    if exe.return_code != 0:
        return changes

    # Parse the output
    try:

        # Regex for diff line
        regex_pattern = re.compile('^(A|M|D|T|C|R)\w*\s+(.*)$')

        # Sort input into dict by type of change
        for line in exe.get_output().split("\n"):
            regex_result = regex_pattern.match(line)

            # If this line matched the test, add it to the dict
            if regex_result:
                change_type = regex_result.group(1).strip()
                file_path = regex_result.group(2).strip()

                # Change type mapping
                if change_type == 'T':
                    # Change in type of file. Consider this a Modification
                    change_type = 'M'
                elif change_type == 'C':
                    # File copied into a new file. Consider this an Add
                    change_type = 'A'
                elif change_type == 'R':
                    # File file was renamed. Consider this a Modification
                    change_type = 'M'

                changes[change_type].append(file_path)
                changes['has_differences'] = True

        changes['status'] = True

    except Exception as ee:
        out.put_error("Error diffing branches: {0}".format(ee))

    return changes


def merged_branches(target_branch="master"):
    """Get a list of all branches that have been merged into specified branch"""
    out.trace("merged_branches", [target_branch])

    branch_dict = {'local': [], 'remote': []}

    # Get local merged branches
    try:
        git_cmd = ['git', 'branch', '--merged', target_branch]
        exe = utility.run_git_cmd(git_cmd)
        if exe.return_code == 0 and exe.get_output():
            for branch in exe.get_output().splitlines():
                if ' -> ' not in branch:
                    branch_dict['local'].append(branch.strip(' *'))
    except Exception as ee:
        out.put_error("Error listing local merged branches: {0}".format(ee))

    # Get remote merged branches
    try:
        git_cmd = ['git', 'branch', '-r', '--merged', target_branch]
        exe = utility.run_git_cmd(git_cmd)
        if exe.return_code == 0 and exe.get_output():
            for branch in exe.get_output().splitlines():
                if ' -> ' not in branch:
                    branch_dict['remote'].append(branch.strip(' *'))
    except Exception as ee:
        out.put_error("Error listing remote merged branches: {0}".format(ee))

    return branch_dict


def reset(reset_point=None, allow_untracked=True):
    """Reset repository back to previously committed state"""
    out.trace("reset", [reset_point, allow_untracked])
    git_cmd = ['git', 'reset', '--hard']
    if reset_point is not None:
        git_cmd.append(reset_point)
    exe = utility.run_git_cmd(git_cmd)

    if not allow_untracked:
        git_cmd = ['git', 'clean', '-f', '-d']
        exe = utility.run_git_cmd(git_cmd)

    return (exe.return_code == 0) and is_clean(allow_untracked)


def get_commits(branch_name=None, max_commits=None, since_commit=None):
    """Put the results of git log into a list of dicts"""
    out.trace("get_commits", [branch_name, max_commits])

    git_cmd = ['git', 'log']

    # If listing commits since a previous commit
    if since_commit:
        git_cmd.append("{0}..{1}".format(since_commit, branch_name if branch_name else current_branch()))

    # If specifying branch (only one)
    elif branch_name:
        git_cmd.append("{0}".format(branch_name))

    # If limiting number of commits
    if type(max_commits) is int:
        git_cmd.append("-{0}".format(max_commits))

    exe = utility.run_git_cmd(git_cmd)

    commits = []
    commit = {}
    commit_found = False
    for line in exe.get_output().splitlines():

        # Beginning of a new commit
        if line.startswith('commit'):
            # If need to save previous commit
            if commit_found:
                commits.append(commit)

            # Re-initialize commit dict
            git_hash = line.replace('commit', '').strip()
            commit = {'commit': git_hash, 'author': "", 'date': "", 'message': ""}
            commit_found = True

        elif line.startswith('Merge:'):
            continue

        elif line.startswith('Author:'):
            commit['author'] = line.replace('Author:', '').strip()

        elif line.startswith('Date:'):
            commit['date'] = utility.git_string_to_date(line.replace('Date:', '').strip())

        elif line.strip():
            commit['message'] += "{0}\n".format(line.strip())

    # If need to save previous commit
    if commit_found:
        commits.append(commit)

    return commits


def get_last_commit_message(branch_name=None):
    try:
        return get_commits(branch_name, max_commits=1)[0]['message'].strip()
    except IndexError:
        Console.get().put_error("Cannot get last commit message.  No commits have been made.")
        return None


def get_common_ancestor(branch_1, branch_2):
    """Get the best common ancestor of two branches"""
    out.trace("get_common_ancestor", [branch_1, branch_2])

    git_cmd = ['git', 'merge-base', branch_1, branch_2]
    exe = utility.run_git_cmd(git_cmd)
    commit = exe.get_output().strip()
    # If output contains anything other than a commit hash, assume failure
    if " " in commit:
        out.put_warning("Unable to find common ancestor of {0} and {1}".format(branch_1, branch_2))
        return None
    else:
        return commit


def get_common_ancestor_details(branch_1, branch_2):
    """Get details about the last common ancestor between two branches"""
    out.trace("get_common_ancestor_details", [branch_1, branch_2])

    commit = get_common_ancestor(branch_1, branch_2)

    # If common commit not found, cannot get date
    if commit is None:
        return None

    # Show the commit
    cmd = ['git', 'show', commit]
    exe = utility.run_git_cmd(cmd)

    commit_details = {
        'commit': None,
        'author': None,
        'date': None,
        'message': ""
    }

    # Process the output of "git show"
    for line in exe.get_output().splitlines():
        print("- '{0}'".format(line))
        if line.startswith('commit'):
            commit_details['commit'] = line.replace('commit', '').strip()
        elif line.startswith('Author:'):
            commit_details['author'] = line.replace('Author:', '').strip()
        elif line.startswith('Date:'):
            commit_details['date'] = utility.git_string_to_date(line.replace('Date:', '').strip())
        elif line.startswith('diff'):
            break
        elif line.strip() == "":
            continue
        else:
            commit_details['message'] += line.strip() + "\n"

    return commit_details


def get_common_ancestor_date(branch_1, branch_2):
    """Get the approximate date that two branches diverged"""
    out.trace("get_common_ancestor_date", [branch_1, branch_2])

    commit = get_common_ancestor_details(branch_1, branch_2)

    # If common commit not found, cannot get date
    if commit is None:
        return None
    else:
        return commit['date']
