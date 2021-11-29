from pdx import Console
from pdx import Executor
from git import Repo
from pdx.git import utility
from pdx.git import actions
from pdx.git import repo
from pdx.git import remote
import os


class GitWrapper:
    repo = None
    root_dir = None
    default_remote = 'origin'
    
    # Callable functions from the pdx.git library
    # =========================================================================

    def is_repo(self):
        return self.call_git_function(repo.is_repo)

    def get_repo_base(self):
        return self.call_git_function(utility.get_repo_base)

    def set_config(self, config_var, config_val):
        return self.call_git_function(utility.set_config, (config_var, config_val))

    def get_config(self, config_var):
        return self.call_git_function(utility.get_config, (config_var,))

    def is_clean(self):
        return self.call_git_function(repo.is_clean)

    def is_unmodified(self):
        return self.call_git_function(repo.is_unmodified)

    def current_branch(self, show_tag_when_detached=None):
        show_tag_when_detached = True if show_tag_when_detached is None else show_tag_when_detached
        return self.call_git_function(repo.current_branch, (show_tag_when_detached, ))

    def checkout_branch(self, branch_name, create_from="master"):
        return self.call_git_function(repo.checkout_branch, (branch_name, create_from))

    def create_branch(self, branch_name, branch_from=None):
        return self.call_git_function(repo.create_branch, (branch_name, branch_from))

    def delete_branch(self, branch_name):
        return self.call_git_function(repo.delete_branch, (branch_name,))

    def delete_tag(self, tag_name, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(repo.delete_tag, (tag_name, remote_name))

    def list_branches(self):
        return self.call_git_function(repo.list_branches)

    def list_all_branches(self):
        return self.call_git_function(repo.list_all_branches)

    def list_tags(self):
        return self.call_git_function(repo.list_tags)

    def branch_exists(self, branch_name, include_tags=None):
        include_tags = True if include_tags is None else include_tags
        return self.call_git_function(repo.branch_exists, (branch_name, include_tags))

    def any_branch_exists(self, branch_name, include_tags=None):
        include_tags = True if include_tags is None else include_tags
        return self.call_git_function(repo.any_branch_exists, (branch_name, include_tags))

    def tag_exists(self, tag_name):
        return self.call_git_function(repo.tag_exists, (tag_name,))

    def most_recent_tag(self, ):
        return self.call_git_function(actions.most_recent_tag)

    def status_dict(self, branch_name=None):
        return self.call_git_function(repo.status_dict, (branch_name,))

    def diff_branches(self, into_branch=None, from_branch=None):
        return self.call_git_function(repo.diff_branches, (into_branch, from_branch))

    def merged_branches(self, target_branch="master"):
        return self.call_git_function(repo.merged_branches, (target_branch,))

    # def show_diff(self, into_branch=None, from_branch=None, indent=False):
    #     return self.call_git_function(git_display.show_diff, (into_branch, from_branch, indent))

    # def show_status(self, indent=False):
    #     return self.call_git_function(git_display.show_status, (indent,))

    def reset(self, reset_point=None, allow_untracked=True):
        return self.call_git_function(repo.reset, (reset_point, allow_untracked))

    def get_commits(self, branch_name=None, max_commits=100, since_commit=None):
        return self.call_git_function(repo.get_commits, (branch_name, max_commits, since_commit))

    def get_last_commit_message(self, branch_name=None):
        return self.call_git_function(repo.get_last_commit_message, (branch_name,))

    def get_common_ancestor(self, branch_1, branch_2):
        return self.call_git_function(repo.get_common_ancestor, (branch_1, branch_2,))

    def get_common_ancestor_details(self, branch_1, branch_2):
        return self.call_git_function(repo.get_common_ancestor_details, (branch_1, branch_2,))

    def get_common_ancestor_date(self, branch_1, branch_2):
        return self.call_git_function(repo.get_common_ancestor_date, (branch_1, branch_2,))

    def get_previous_version(self, file_path, tag="HEAD~1"):
        return self.call_git_function(actions.get_previous_version, (file_path, tag))

    def add(self, path=None):
        if path is None:
            path = self.get_repo_base()
        return self.call_git_function(actions.add, (path,))

    def remove(self, path):
        return self.call_git_function(actions.remove, (path,))

    def commit(self, message, amend=False):
        return self.call_git_function(actions.commit, (message, amend))

    def merge_preview(self, into_branch, from_branch, rollback_conflicts=True):
        return self.call_git_function(actions.merge_preview, (into_branch, from_branch, rollback_conflicts))

    def merge(self, into_branch, from_branch, rollback_conflicts=True, file_list_on_success=False):
        return self.call_git_function(actions.merge, (
            into_branch, from_branch, rollback_conflicts, file_list_on_success
        ))

    def rebase(self, into_branch, from_branch, rollback_conflicts=True):
        return self.call_git_function(actions.rebase, (
            into_branch, from_branch, rollback_conflicts
        ))

    def tag(self, version, remote_name=None, push_tags=True):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(actions.tag, (version, remote_name, push_tags))

    def stash(self):
        return self.call_git_function(actions.stash)

    def pop(self):
        return self.call_git_function(actions.pop)

    def list_remotes(self):
        return self.call_git_function(remote.list_remotes)

    def add_remote(self, url, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.add_remote, (url, remote_name))

    def get_remote_url(self, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.get_remote_url, (remote_name, ))

    def get_remote_repo_name(self, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.get_remote_repo_name, (remote_name, ))

    def set_remote_url(self, url, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.set_remote_url, (url, remote_name))

    def fetch(self):
        return self.call_git_function(remote.fetch)

    def branch_tracking(self):
        return self.call_git_function(remote.branch_tracking)

    def track_remote(self, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.track_remote, (remote_name,))

    def pull_needed(self, warnings_in_session=False):
        return self.call_git_function(remote.pull_needed, (None, warnings_in_session))

    def push_needed(self):
        return self.call_git_function(remote.push_needed)

    def pull(self, local_branch=None, remote_branch=None, remote_name=None, rollback_conflicts=False):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(
            remote.pull, (local_branch, remote_branch, remote_name, rollback_conflicts)
        )

    def push(self, local_branch=None, remote_name=None, force=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.push, (local_branch, remote_name, force))

    def push_tags(self, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.push_tags, (remote_name,))

    def delete_remote_branch(self, remote_branch, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.delete_remote_branch, (remote_branch, remote_name))

    def list_remote_branches(self, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.list_remote_branches, (remote_name,))

    def remote_branch_exists(self, branch_name):
        return self.call_git_function(remote.remote_branch_exists, (branch_name, ))

    def prune_remote(self, remote_name=None):
        remote_name = self.default_remote if remote_name is None else remote_name
        return self.call_git_function(remote.prune_remote, (remote_name, ))

    #
    #
    #

    # This function will run any git command on the repo
    def run_git_command(self, command_list, trace_level="info", suppress_errors=False):
        """Call any git command on this repo"""

        # cd to git repo directory, and save previous directory
        before = os.getcwd()
        if before != self.root_dir:
            os.chdir(self.root_dir)

        # Now in git repo directory, run the Git command
        exe = utility.run_git_cmd(command_list, trace_level, suppress_errors)

        # Return to original directory
        if before != self.root_dir:
            os.chdir(before)

        del before

        # Return result from Git function
        return exe

    # This function calls Git functions defined in the pdx.git package
    def call_git_function(self, git_fn, parameters=None):
        """Call a function from the pdx.git module"""

        # cd to git repo directory, and save previous directory
        before = os.getcwd()
        if before != self.root_dir:
            os.chdir(self.root_dir)

        # If now in git repo directory, run the Git command
        if parameters is None:
            result = git_fn()
        else:
            result = git_fn(*parameters)

        # Return to original directory
        if before != self.root_dir:
            os.chdir(before)

        del before

        # Return result from Git function
        return result

    @staticmethod
    def get_ssh_address(project, repo):
        """Get the PSU BitBucket ssh address (i.e. for clone) of a repository"""
        return "ssh://git@git.oit.pdx.edu:7999/{0}/{1}.git".format(project, repo)

    def __init__(self, git_path=None, project_code=None, repo_name=None, init=False):
        out = Console.get()

        # When not specified, use current directory
        if git_path is None:
            git_path = os.getcwd()

        # Make sure given path exists
        if not os.path.isdir(git_path):
            out.put_error("Specified Git repository directory does not exist: {0}".format(git_path))
            return

        # Is this already a Git repository? Also checking for the root level directory of the repo.
        exe = Executor.Executor("git rev-parse --show-toplevel", git_path)
        is_repo = exe.return_code == 0

        # If yes, are we at the root of the repo?
        if is_repo:
            # If project and repo were specified, user may have been expecting to clone the repo
            if project_code and repo_name:
                out.put_warning("""\
Project and repo were specified, but this is already a Git repo.
    
    If you intended to clone a repository, you must do it from a directory
    that does not already contain a Git repository.
                """)
            # Make sure we are using the root directory of the repo
            git_path = exe.get_output().strip()

            # Create Repository object
            self.repo = Repo(git_path)

        # If not a repo, and project/repo were specified, Clone it now
        elif project_code and repo_name:
            before = os.getcwd()
            os.chdir(git_path)
            remote.clone(self.get_ssh_address(project_code, repo_name))
            os.chdir(before)

            # Update git_path to point to the newly cloned directory
            git_path = os.path.join(git_path, repo_name)

            # Verify that the directory was created
            if not os.path.isdir(git_path):
                out.put_error("Unable to clone the repository: {0}/{1}".format(project_code, repo_name))
                return

            # Create Repository object
            self.repo = Repo(git_path)

        # If not a repo, Init a new repo (if deisred)
        elif init:
            # Initialize a new repo
            out.put_color("Initializing a new Git repository at {0}".format(git_path), 'blue')
            self.repo = Repo.init(git_path)

        # Remember the root directory path
        self.root_dir = git_path

        # Fetch from remotes
        self.fetch()

        del exe
        del is_repo
