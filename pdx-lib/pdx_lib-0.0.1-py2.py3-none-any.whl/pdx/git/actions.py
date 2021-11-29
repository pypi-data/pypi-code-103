from pdx import Session
from pdx import Console
from pdx import utility_service
from pdx.git import utility
from pdx.git import repo
from pdx.git import remote
import os
import re

# Console shared by all commands
out = Console.get()


def add(path="."):
    """Add uncommitted changes to the current branch"""
    out.trace("add", [path])

    # Add to Git
    exe = utility.run_git_cmd(["git", "add", "--all", path])

    return exe.return_code == 0


def remove(path):
    """Delete a file from Git"""
    out.trace("remove", [path])

    # Remove from Git
    exe = utility.run_git_cmd(["git", "rm", path])

    return exe.return_code == 0


def commit(commit_msg, amend=False):
    """Commit changes to git repository"""
    out.trace("commit", [commit_msg])
    current_branch = repo.current_branch()

    # Do not allow commits to detached head
    if current_branch == 'HEAD':
        out.put_error("Cannot commit to detached head. Please checkout a new branch.")
        return False

    # Determine command to use
    if amend:
        cmd = ["git", "commit", "--amend", "-m", commit_msg]
    else:
        cmd = ["git", "commit", "-m", commit_msg]

    # Commit changes
    exe = utility.run_git_cmd(cmd)

    return exe.return_code == 0


def get_merged_files(merge_output):
    """
    Get a list of files that were affected by a merge
    """
    out.trace("get_merged_files", [len(merge_output)])
    file_list = []

    try:
        # Test each line for a merged file path
        file_pattern = r'^\s+(\S+)\s+\|\s+\w+.*$'
        file_exp = re.compile(file_pattern)
        for line in merge_output.split("\n"):
            try:
                result = file_exp.match(line)

                # If this is a rename
                if " => " in line and "mode change" not in line:
                    old_path = None
                    new_path = None
                    try:
                        # If the path (or part of it) is listed once for both names
                        if "{" in line:
                            pieces = line.split('{')
                            base_path = pieces[0].replace('rename ', '').strip()
                            names = pieces[1].split('}')[0].split(' => ')
                            old_path = os.path.join(base_path, names[0])
                            new_path = os.path.join(base_path, names[1])

                        # If a file with a shared shortened path has been renamed
                        elif '}' in line:
                            # Old name cannot be located, since it has already been renamed
                            # Print a warning that the old file could not be processed
                            # This should be a rare case, and very unlikely to occur in Banner repo
                            msg = "Old version of a renamed file could not be determined.\n"
                            msg += "If some processing must happen on the old file path, it must be done manually.\n"
                            msg += "File info:\n\t{0}".format(line.strip())
                            out.put_warning(msg)
                            continue

                        # Otherwise, each name has its own path
                        else:
                            names = line.split(" => ")
                            old_path = names[0]
                            new_path = names[1]

                    except Exception as ee:
                        out.unexpected_error(ee, "Error detecting renamed file paths")

                    if old_path and new_path:
                        file_list.append(old_path)
                        file_list.append(new_path)
                        continue

                # If this line matched the test
                if result:
                    # Get the file path and append it to the list
                    file_list.append(result.group(1))

            except Exception as ee:
                out.unexpected_error(ee, "Error handling merge output line: {0}".format(line))

    except Exception as ee:
        out.unexpected_error(ee, "Error handling merge output")

    return file_list


def merge_preview(into_branch, from_branch, rollback_conflicts=True):
    """
    Get a list of files that will be affected by a merge
    """
    out.trace("merge_preview", [from_branch, into_branch])

    start_branch = repo.current_branch()
    file_list = []

    # If merging from remote branch, make sure remote branch exists
    if "origin/" in from_branch:
        if not remote.remote_branch_exists(from_branch.replace("origin/", "")):
            out.put_error("Cannot merge non-existing remote branch: {0}".format(from_branch))
            return None

    # If merging local branch, make sure local branch exists
    elif not repo.branch_exists(from_branch):
        out.put_error("Cannot merge non-existing branch: {0}".format(from_branch))
        return None

    # Cannot merge into a remote branch
    if "origin/" in into_branch:
        out.put_error("Cannot merge into a remote branch ({0})".format(into_branch))
        return None

    # Checkout the branch to merge into
    if not repo.checkout_branch(into_branch):
        out.put_error("Could not checkout branch: {0}".format(into_branch))
        return None

    # Create a temporary branch to perform the merge on
    timestamp = utility_service.get_timestamp_string()
    tmp_branch = '{0}/{1}-{2}'.format(Session.username, into_branch.replace('psu/', ''), timestamp)
    if not repo.create_branch(tmp_branch, into_branch):
        out.put_error("Unable to create temp branch for merge preview")
        repo.checkout_branch(start_branch)
        return None

    # Merge branches
    exe = utility.run_git_cmd(["git", "merge", from_branch])
    if exe.return_code != 0:
        out.put_error("Merging {0} into {1} failed".format(from_branch, into_branch))
        repo.checkout_branch(start_branch)
        repo.delete_branch(tmp_branch)
        return None

    elif 'CONFLICT' in exe.get_output():
        status = repo.status_dict()
        conflicts = status['conflicts']["items"]
        conflict_message = "Merging {0} into {1} resulted in the following conflicts:\n\t{2}".format(
            from_branch,
            into_branch,
            "\n\t".join(conflicts)
        )

        if rollback_conflicts:
            out.put_error(conflict_message)
            if repo.reset():
                repo.checkout_branch(start_branch)
                repo.delete_branch(tmp_branch)
                out.put_info("Merge has been reverted. Repository is clean.")
            else:
                out.put_error(
                    "Merge could not be reverted. You must resolve the conflicts, or manually revert the merge."
                )
            return None

        # If not rolling back conflicts, print some instructions
        else:
            out.clear()
            out.put_warning(conflict_message)
            out.put("\n")

            out.put("""
  You are currently on temporary branch: {0}.

  Resolve the conflicts on this temporary branch by doing the following:
        1. Edit each file listed above to resolve the conflicts.
        2. git add --all .
        3. git commit -m "Resolved merge conflicts"

  If appropriate to add code from the target branch into your feature branch:
        4. git checkout {1}
        5. git merge {0}
        6. git branch -d {0}
        7. git push origin {1}

  To completely abort this merge:
        1. git reset --hard
        2. git checkout {1}
        3. git branch -d {0}

            """.format(tmp_branch, start_branch))

        return None

    # Review the merge output
    else:
        file_list = get_merged_files(exe.get_output())

    # Remove the temp branch
    repo.checkout_branch(start_branch)
    repo.delete_branch(tmp_branch)

    return file_list


def merge(into_branch, from_branch, rollback_conflicts=True, file_list_on_success=False):
    """Merge changes from one branch into another
    :param into_branch: Merge changes into this branch
    :param from_branch: Merge changes from this branch
    :param rollback_conflicts: Rollback the merge if conflicts are encountered (Boolean)
    :param file_list_on_success: Return a list of merged files upon successful merge?
    :return: [S]uccess, [C]onflicts, or None, or a list of merged files (if indicated in parameters)
    """
    out.trace("merge", [from_branch, into_branch, rollback_conflicts, file_list_on_success])
    start_branch = repo.current_branch()

    # Make sure both branches exist
    if "origin/" in from_branch:
        if not remote.remote_branch_exists(from_branch.replace("origin/", "")):
            out.put_error("Cannot merge non-existing remote branch: {0}".format(from_branch))
            return None
    elif not repo.branch_exists(from_branch):
        # If remote branch exists, check it out, and then change back to start branch
        if remote.remote_branch_exists(from_branch) and repo.checkout_branch(from_branch, None):
            repo.checkout_branch(start_branch)
        else:
            out.put_error("Cannot merge non-existing branch: {0}".format(from_branch))
            return None

    if "origin/" in into_branch:
        out.put_error("Cannot merge into a remote branch ({0})".format(into_branch))
        return None

    # Checkout the branch to merge into
    if not repo.checkout_branch(into_branch):
        out.put_error("Could not checkout branch: {0}".format(into_branch))
        return None

    # Merge branches
    exe = utility.run_git_cmd(["git", "merge", from_branch])

    if exe.return_code != 0:
        out.put_error("Merging {0} into {1} failed".format(from_branch, into_branch))
        repo.checkout_branch(start_branch)
        return None

    output = exe.get_output()

    if "CONFLICT " in output:
        status = repo.status_dict()
        conflicts = status['conflicts']["items"]
        conflict_message = "Merging {0} into {1} resulted in the following conflicts:\n\t{2}".format(
            from_branch,
            into_branch,
            "\n\t".join(conflicts)
        )

        if rollback_conflicts:
            out.put_error(conflict_message)
            if repo.reset():
                out.put_info("Merge has been reverted. Repository is clean.")
                repo.checkout_branch(start_branch)
                return None
            else:
                out.put_error(
                    "Merge could not be reverted. You must resolve the conflicts, or manually revert the merge."
                )
        else:
            out.put_warning(conflict_message)

        repo.checkout_branch(start_branch)
        return 'C'

    # Return to original branch
    repo.checkout_branch(start_branch)

    # Return merge success indicator
    if file_list_on_success:
        return get_merged_files(output)

    else:
        return 'S'


def rebase(into_branch, from_branch, rollback_conflicts=True):
    """Rebase changes from one branch onto another
    :param into_branch: Rebase changes onto this branch
    :param from_branch: Rebase changes from this branch
    :param rollback_conflicts: Rollback the rebase if conflicts are encountered (Boolean)
    :return: [S]uccess (changes were made), [s]uccess (already up-to-date), [C]onflicts, or None
    """
    out.trace("rebase", [into_branch, from_branch, rollback_conflicts])
    start_branch = repo.current_branch()

    # Make sure both branches exist
    if "origin/" in from_branch:
        if not remote.remote_branch_exists(from_branch.replace("origin/", "")):
            out.put_error("Cannot rebase from non-existing remote branch: {0}".format(from_branch))
            return None
    elif not repo.branch_exists(from_branch):
        # If remote branch exists, check it out, and then change back to start branch
        if remote.remote_branch_exists(from_branch) and repo.checkout_branch(from_branch, None):
            repo.checkout_branch(start_branch)
        else:
            out.put_error("Cannot rebase from non-existing branch: {0}".format(from_branch))
            return None

    if "origin/" in into_branch:
        out.put_error("Cannot rebase onto a remote branch ({0})".format(into_branch))
        return None
    elif not repo.branch_exists(into_branch):
        out.put_error("Cannot rebase onto non-existing branch: {0}".format(into_branch))
        return None

    # Checkout the branch to rebase onto
    if not repo.checkout_branch(into_branch):
        out.put_error("Could not checkout branch: {0}".format(into_branch))
        return None

    # Rebase branch
    exe = utility.run_git_cmd(["git", "rebase", from_branch])

    if exe.return_code != 0:
        out.put_error("Rebasing {0} onto {1} failed".format(from_branch, into_branch))
        repo.checkout_branch(start_branch)
        return None

    output = exe.get_output()

    if "CONFLICT " in output:
        status = repo.status_dict()
        conflicts = status['conflicts']["items"]
        conflict_message = "Rebasing {0} from {1} resulted in conflicts:\n{2}".format(
            into_branch,
            from_branch,
            out.format_list(conflicts, indent=4)
        )

        if rollback_conflicts:
            out.put_error(conflict_message)
            utility.run_git_cmd(['git', 'rebase', '--abort'])
            if repo.reset():
                out.put_info("Rebase has been reverted. Repository is clean.")
                repo.checkout_branch(start_branch)
            else:
                out.put_error(
                    "Rebase could not be reverted. You must resolve the conflicts, or manually revert the rebase."
                )
                return None
        else:
            out.put_warning(conflict_message)

        repo.checkout_branch(start_branch)
        return 'C'

    # Return to original branch
    repo.checkout_branch(start_branch)

    # Return merge success indicator
    if "Applying:" not in output and "is up to date" in output:
        # Suucess: Nothing to rebase
        return 's'
    else:
        # Success: Branch was rebased
        return 'S'


def tag(version, remote_name="origin", push_tags=True):
    """Create a tag on the current branch"""
    out.trace("tag", [version, remote_name, push_tags])

    # Create tag
    exe = utility.run_git_cmd(["git", "tag", str(version)])

    if push_tags and exe.return_code == 0:
        remote.push_tags(remote_name)

    return exe.return_code == 0


def most_recent_tag():
    """get the most-recent tag in a repo"""
    out.trace("most_recent_tag", [])
    exe = utility.run_git_cmd(["git", "describe", "--abbrev=0", "--tags"], suppress_errors=True)
    if exe.return_code == 0:
        return exe.get_output()
    elif 'No names found' in exe.get_stderr():
        out.put_warning("No tags exist")
    else:
        out.put_error(exe.get_stderr())
    return None


def stash():
    """Stash all changes"""
    out.trace("stash", [])
    exe = utility.run_git_cmd(["git", "stash"])
    return exe.return_code == 0


def pop():
    """Pop all stashed changes"""
    out.trace("pop", [])
    exe = utility.run_git_cmd(["git", "stash", "pop"])
    return exe.return_code == 0


def get_previous_version(file_path, tag_or_commit="HEAD~1"):
    """Checkout a previous version of a file"""
    out.trace("get_previous_version", [file_path, tag_or_commit])
    exe = utility.run_git_cmd(["git", "checkout", tag_or_commit, '--', file_path])
    return exe.return_code == 0
