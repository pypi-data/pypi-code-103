from pdx import Session
from pdx import Console
from pdx.git import utility
from pdx.git import repo
import os
import re

# Console shared by all commands
out = Console.get()


def list_remotes():
    """Get a list of defined remotes"""
    out.trace('listRemotes', [])
    exe = utility.run_git_cmd(["git", "remote"], trace_level="debug")

    remote_list = []
    for line in exe.get_output().split(os.linesep):
        if line.strip() != "":
            remote_list.append(line.strip())

    return remote_list


def add_remote(url, remote_name="origin"):
    """Add a remote to a repo"""
    out.trace('add_remote', [url, remote_name])
    exe = utility.run_git_cmd(["git", "remote", "add", remote_name, url])
    return exe.return_code == 0


def get_remote_url(remote_name="origin"):
    """Get the URL of an existing remote"""
    out.trace('get_remote_url', [remote_name])
    exe = utility.run_git_cmd(["git", "config", "--get", "remote.{0}.url".format(remote_name)], "debug")
    return exe.get_output().strip()


def get_remote_repo_name(remote_name="origin"):
    """Get the repository name of an existing git repository"""
    out.trace('get_remote_repo_name', [remote_name])
    url = get_remote_url(remote_name)
    if url is not None:
        url = os.path.basename(url).replace('.git', '')
    return url


def set_remote_url(url, remote_name="origin"):
    """Update the URL of an existing remote"""
    out.trace('set_remote_url', [url, remote_name])
    exe = utility.run_git_cmd(["git", "remote", "set-url", remote_name, url])
    return exe.return_code == 0


def clone(repo_url, repo_dir_name=None):
    """Clone a Git repository"""
    out.trace('clone', [repo_url, repo_dir_name])

    # Cannot clone from PSU when not on PSU network
    if ("pdx.edu" in repo_url) and (not repo.on_psu_network):
        repo.remote_disabled(skip_remote_check=True)
        return False

    # Get name of repo from parameter, or from the URL
    repo_name = repo_dir_name if repo_dir_name else utility.get_repo_from_url(repo_url)

    # Check for existing directory (or file)
    if os.path.exists(repo_name):
        out.put_error(
            "Cannot clone {0} repo because a file or directory by that name already exists.".format(repo_name)
        )
        return None

    # Clone the repo
    exe = utility.run_git_cmd(["git", "clone", repo_url, repo_name])

    # Only return true if the repo directory exists
    return exe.return_code == 0 and os.path.isdir(repo_name)


def fetch():
    """Fetch all (to see if anything changed remotely)"""
    out.trace('fetch', [])
    return_value = None
    # Suppress output, but return it to calling function
    suppress_before = out.suppressConsoleOutput
    out.suppressConsoleOutput = True
    if not repo.remote_disabled():
        exe = utility.run_git_cmd(['git', 'fetch', '--all'])
        return_value = exe.get_output()

    out.suppressConsoleOutput = suppress_before
    return return_value


def branch_tracking():
    """Get a dict of branches and what remote branch they track (or None)"""
    out.trace('branch_tracking', [])
    exe = utility.run_git_cmd(['git', 'branch', '-vv'])

    if exe.return_code == 0:
        tracking_dict = {}

        # Regex for tracking line
        regex_pattern = re.compile('^\*?\s+(\S+)\s+\S+\s+\[([A-Za-z0-9_]+)/([A-Za-z0-9_]+)\]\s+.*$')

        # For each line of output
        for line in exe.get_output().split(os.linesep):
            regex_result = regex_pattern.match(line)

            # If this line matched the test, add it to the dict
            if regex_result:
                local_branch = regex_result.group(1).strip()
                # remote_name = regex_result.group(2).strip()
                remote_branch = regex_result.group(3).strip()
                tracking_dict[local_branch] = remote_branch

        return tracking_dict

    return None


def track_remote(remote_name="origin"):
    """Check if current branch is set up to track existing remote. Set up tracking if necessary/possible"""
    out.trace('track_remote', [])
    remotes = list_remote_branches()
    current = repo.current_branch()

    # Only need to check when current branch has an existing remote
    if current in remotes:
        # get branch tracking info
        tracking = branch_tracking()

        # if tracking is not set up
        if current not in tracking:
            # set up tracking now
            exe = utility.run_git_cmd(
                ['git', 'branch', "--set-upstream-to={0}/{1}".format(remote_name, current), current]
            )
            return exe.return_code == 0

    # If tracking not needed, or already set up
    return True


def pull_needed(status_output=None, warnings_in_session=False):
    """Does current branch need to pull from remote?"""
    warnings = []
    answer = None

    # If not on PSU network, and remote is PSU hosted, then pull is disabled
    if repo.remote_disabled():
        warnings.append("Remote functions are disabled.")
        answer = False

    else:

        # If status output not provided, get it now
        if status_output is None:
            status_output = repo.status()

        if "the upstream is gone" in status_output:
            warnings.append("Upstream branch was deleted")
            answer = False

        elif "Your branch is behind" in status_output:
            answer = True

        elif 'use "git pull"' in status_output:
            answer = True

        elif "branch is up-to-date" in status_output:
            answer = False

        elif "branch is up to date" in status_output:
            answer = False

    if answer is None:
        # Check if branch is local-only
        try:
            tracked_remote = branch_tracking()[repo.current_branch()]
            if tracked_remote is None:
                warnings.append("Local Only")
                answer = False
        except:
            warnings.append("No branch tracking info was found")
            answer = False

    if answer is None:
        warnings.append("Unsure if pull is needed.")
        answer = True

    # Put warnings in session, if desired
    if warnings_in_session:
        Session.data['pull_needed_warnings'] = warnings
    del warnings

    return answer


def push_needed(status_output=None):
    """Does current branch need to push to remote?"""
    if repo.remote_disabled():
        return False

    if status_output is None:
        status_output = repo.status()

    return "Your branch is ahead" in status_output


def pull(local_branch=None, remote_branch=None, remote_name="origin", rollback_conflicts=False, suppress_stderr=True):
    """Pull changes from Stash
    :param local_branch: Pull changes into this branch
    :param remote_branch: Pull changes from this branch
    :param remote_name: Name of remote to pull from (i.e. origin)
    :param rollback_conflicts: Rollback the merge if conflicts are encountered (Boolean)
    :param suppress_stderr: Do not print stderr, unless a fatal error occurs (Boolean)
    :return: [S]uccessfully pulled changes, [s]uccessful (up-to-date), [C]onflicts, or None"""
    out.trace('pull', [local_branch, remote_branch, remote_name, rollback_conflicts, suppress_stderr])
    start_branch = repo.current_branch()

    if repo.remote_disabled():
        return False

    # Determine branches
    if local_branch is None:
        local_branch = repo.current_branch()
    if remote_branch is None:
        remote_branch = local_branch

    # Make sure we're on the specified branch
    if repo.checkout_branch(local_branch):

        # Pull changes
        exe = utility.run_git_cmd(["git", "pull", remote_name, remote_branch])
        output = exe.get_output()
        stderr = exe.get_stderr()
        success = exe.return_code == 0

        # If command failed, return now
        if not success:
            repo.checkout_branch(start_branch)
            return None

        # Test other indications of failure
        fail_strings = [
            "permission denied",
            "in the middle of another rebase",
        ]
        for ss in fail_strings:
            if ss.lower() in output.lower() or ss.lower() in stderr.lower():
                repo.checkout_branch(start_branch)
                return None

        # If up-to-date, consider it a success
        if "up to date" in output.lower() or "up-to-date" in output.lower():
            repo.checkout_branch(start_branch)
            return 's'  # lowercase indicates up-to-date with no changes pulled

        if "CONFLICT " in output or "CONFLICT " in stderr:
            status = repo.status_dict()
            conflicts = status['conflicts']["items"]
            conflict_message = "Pulling {0}/{1} into {2} resulted in the following conflicts:\n\t{3}".format(
                remote_name,
                remote_branch,
                local_branch,
                "\n\t".join(conflicts)
            )

            if rollback_conflicts:
                out.put_error(conflict_message)

                # If the pull initiated a rebase, abort it
                if status['rebasing']['items']:
                    utility.run_git_cmd(['git', 'rebase', '--abort'])

                # Reset any modifications
                if repo.reset():
                    out.put_info("Pull has been reverted. Repository is clean.")
                else:
                    out.put_error(
                        "Pull could not be reverted. You must resolve the conflicts, or manually revert the pull."
                    )
            else:
                out.put_warning(conflict_message)

            repo.checkout_branch(start_branch)
            return 'C'

        repo.checkout_branch(start_branch)
        return 'S'  # Uppercase indicates that changes were pulled (rather than already up-to-date)


def push(local_branch=None, remote_name="origin", force=None):
    """Push changes to remote branch of same name
    :param local_branch: Push changes from this branch
    :param remote_name: Name of remote to push to (i.e. origin)
    :param force:       Use the Force, Luke.  Force push to a feature branch when we rebase onto production,
                        i.e. pulling production changes into a feature branch using rebase
    :return: Boolean True or False"""
    out.trace('push', [local_branch, remote_name, force])
    start_branch = repo.current_branch()

    if repo.remote_disabled():
        return False

    # Determine branch
    if local_branch is None:
        local_branch = repo.current_branch()

    # Make sure we're on the specified branch
    if repo.checkout_branch(local_branch):
        existing_remotes = list_remote_branches(remote_name)

        # Pull before pushing (if remote exists and not force pushing)
        if local_branch in existing_remotes:
            if pull_needed() and not force:
                pull_result = pull(local_branch)
                if not pull_result:
                    out.put_error("Local branch must be up-to-date with remote prior to pushing")
                    repo.checkout_branch(start_branch)
                    return False
                elif pull_result == 'C':
                    out.put_error("You must resolve conflicts prior to pushing")
                    repo.checkout_branch(start_branch)
                    return False

        # Push changes (and set up tracking)
        if force:
            exe = utility.run_git_cmd(["git", "push", "-uf", remote_name, local_branch])
        else:
            exe = utility.run_git_cmd(["git", "push", "-u", remote_name, local_branch])

        success = exe.return_code == 0

        # Return to original branch
        repo.checkout_branch(start_branch)

        # If command failed, return now
        return success


def push_tags(remote_name="origin"):
    """Push all tags"""
    out.trace('push_tags', [remote_name])

    if repo.remote_disabled():
        return False

    # Push changes
    exe = utility.run_git_cmd(['git', 'push', '--tags'], suppress_errors=True)
    stderr = exe.get_stderr()
    if "No configured push destination" in stderr:
        out.put_warning("Unable to push tags. No remote configured.")
    elif exe.return_code != 0 and stderr != "":
        out.put_error(stderr)

    return exe.return_code == 0


def list_remote_branches(remote_name="origin"):
    """Get a list of existing remote Git branches"""
    out.trace("list_remote_branches", [remote_name])

    git_cmd = ["git", "branch", "-r"]
    exe = utility.run_git_cmd(git_cmd, "debug")

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
            out.unexpected_error(ee, "Error processing remote branch output")
            branches = None

        # List contains branches from (potentially) multiple remotes
        branch_list = []
        if type(branches) is list:
            for branch in branches:
                if branch.startswith(remote_name + '/'):
                    branch_name = branch.replace(remote_name + '/', '')
                    if not branch_name.startswith('HEAD'):
                        branch_list.append(branch_name)

        return branch_list

    return None


def remote_branch_exists(branch_name):
    """Does remote git branch exist? Return True or False"""
    out.trace("remote_branch_exists", [branch_name])

    branch_list = list_remote_branches()
    return branch_name in branch_list


def delete_remote_branch(remote_branch, remote_name="origin"):
    """Delete a remote branch"""
    out.trace("delete_remote_branch", [remote_branch, remote_name])

    if repo.remote_disabled():
        return False

    if remote_branch.lower() == "master":
        out.put_error("You cannot delete the remote master branch")
        return None

    exe = utility.run_git_cmd(["git", "push", remote_name, "--delete", remote_branch])

    return exe.return_code == 0


def prune_remote(remote_name="origin"):
    """Prune remote references"""
    out.trace("prune_remote", [remote_name])

    if repo.remote_disabled():
        return False

    exe = utility.run_git_cmd(["git", "remote", "prune", remote_name])
    return exe.return_code == 0
