from pdx import Console
from pdx import utility_service
from pdx import Session
from pdx.git import GitWrapper

import unittest
import os
import shutil
import inspect

# Always run in debug mode
Session.debug_mode = True


class TestGit(unittest.TestCase):
    """
    Test Git Features
    """
    # Root directory of pdx-lib package
    pdx_code = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    # Unit test working directory
    unit_test_sandbox = os.path.join(Session.pdx_home, 'unit-test')

    def test_repository(self):
        """
        Test an existing Repo object
        """
        # pdx_home should be a Git repository
        git = GitWrapper.GitWrapper(self.pdx_code)
        self.assertTrue(git.repo is not None, "PDX Repository is None")

    def test_clone(self):
        """
        Test cloning a Git repository
        """
        # This can only be done on PSU network or VPN
        if utility_service.is_on_psu_network():

            # Repo to clone
            project = 'IG3'
            repo = 'psu'

            # Expected path to new repo clone
            clone_path = os.path.join(self.unit_test_sandbox, repo)

            # Remove directory if it exists
            if os.path.isdir(clone_path):
                shutil.rmtree(clone_path)
            self.assertFalse(os.path.isdir(clone_path), "Unable to remove {0}".format(clone_path))

            # Clone Git repo in the sandbox directory
            git = GitWrapper.GitWrapper(self.unit_test_sandbox, project, repo)
            self.assertTrue(git.repo is not None, "Unit test clone repository is None")
            self.assertFalse(git.repo.bare, "Unit test clone repository should not be bare repo")
            self.assertTrue(not git.repo.is_dirty(), "Clone should be clean repo")

        else:
            print("Skipping git clone test because you're not on the PSU network.")

    def test_init(self):
        """
        Test initializing a new Repo object, and interact with it
        """
        # Path to new repo
        init_path = os.path.join(self.unit_test_sandbox, 'new_repo')
        
        # Include tests for remote functionality?
        test_remote = False
        
        out = Console.get()

        # Remove directory if it exists
        if os.path.isdir(init_path):
            shutil.rmtree(init_path)
        self.assertFalse(os.path.isdir(init_path), "Unable to remove {0}".format(init_path))

        # Create an empty directory for the new repo and cd to it
        os.makedirs(init_path)
        self.assertTrue(os.path.isdir(init_path), "Unable to create {0}".format(init_path))
        os.chdir(init_path)

        # Initialize a new Git repo in the empty directory
        git = GitWrapper.GitWrapper(init_path, init=True)
        self.assertTrue(git.repo is not None, "Unit test repository is None")
        # self.assertTrue(git.repo.bare, "Unit test repository should be bare repo")
        self.assertTrue(not git.repo.is_dirty(), "Should be clean repo")

        # Create a file
        with open('test-1.txt', 'w') as ff:
            ff.write('Hello World\n')

        # Repo is not considered dirty because the change is untracked
        self.assertFalse(git.repo.is_dirty(), "Test repo is not dirty")

        git.add()
        self.assertTrue(git.repo.is_dirty(), "Test repo is now dirty")

        git.commit("Initial commit")
        self.assertFalse(git.repo.is_dirty(), "Test repo is no longer dirty")
        self.assertTrue(git.get_last_commit_message() == "Initial commit", "Incorrect commit message was retrieved")

        # Create a test branch
        test_branch = 'test/unit_test_repo_branch'
        self.assertFalse(git.branch_exists(test_branch), "Test branch already exists.")
        self.assertTrue(git.create_branch(test_branch), "Could not create branch.")
        self.assertTrue(git.branch_exists(test_branch), "New test branch does not exist.")
        self.assertTrue(git.current_branch() == test_branch, "Not on newly created test branch.")

        # List branches
        local_branches = git.list_branches()
        self.assertTrue("master" in local_branches, "Local master branch missing")
        self.assertTrue(len(local_branches) == 2, "Did not list 2 local branches")

        # List remote branches
        if test_remote:
            remote_branches = git.list_remote_branches()
            if test_branch in remote_branches:
                self.assertTrue(git.delete_remote_branch(test_branch), "Could not delete remote test branch")
                remote_branches = git.list_remote_branches()
            num_remotes = len(remote_branches)
            self.assertTrue("master" in remote_branches, "Remote master branch missing")
            self.assertTrue(num_remotes == 1, "Did not list 1 remote branch")

        # Create some new files
        self.assertTrue(git.current_branch() == test_branch, "Not on newly created test branch.")
        for fname in ['hello.txt', 'changeme.txt', 'deleteme.txt', 'moveme.txt']:
            with open(os.path.join(init_path, fname), 'w') as temp_file:
                temp_file.write("This is {0}".format(fname))

        self.assertTrue(os.path.isfile(os.path.join(init_path, 'deleteme.txt')), "Expected file not created")

        # Add and commit
        self.assertFalse(git.is_clean(), "Modified repo shouldn't be clean")
        self.assertTrue(git.add(), "Unable to add files")
        self.assertTrue(git.commit("BASE - 1"), "Unable to make BASE-1 commit")
        self.assertTrue(git.is_clean(), "Committed repo should be clean")

        # Check if tag exists
        self.assertTrue(git.most_recent_tag() is None, "No tags should exist")
        self.assertFalse(git.tag_exists("0.1"), "Tag 0.1 should not exist")
        # Add a tag
        self.assertTrue(git.tag("0.1"), "Unable to tag version 0.1")
        # Check if tag exists
        self.assertTrue(git.tag_exists("0.1"), "Tag 0.1 should exist")
        self.assertTrue(git.most_recent_tag() == '0.1', "0.1 is most-recent tag")

        # re-add a tag (should fail, so do not print error)
        out.suppressConsoleOutput = True
        self.assertFalse(git.tag("0.1"), "Cannot re-tag versions")
        out.suppressConsoleOutput = False

        # Push new branch to remote
        if test_remote:
            self.assertTrue(git.push(test_branch), "Unable to push test branch")
            remote_branches = git.list_remote_branches()
            self.assertTrue(test_branch in remote_branches, "Remote test branch missing")
            self.assertTrue(len(remote_branches) == (num_remotes + 1), "Remote count not as expected")

            # Set up tracking
            self.assertTrue(git.track_remote(), "Unable to set up tracking")

            # Pull, even though nothing changed, just to check for syntax errors
            self.assertTrue(git.pull(test_branch) == 's', "Unable to pull test branch")

        # Remember the number of commits on this branch
        commits_1 = git.get_commits()
        num_commits_1 = len(commits_1)
        for cc in commits_1:
            out.put_color("{0}: {1}".format(cc['date'], cc['message'].strip()), 'cyan')

        # Assertions on commit order
        self.assertTrue("BASE - 1" in commits_1[0]['message'], "Commits out of order (1)")
        self.assertTrue("Initial commit" in commits_1[1]['message'], "Commits out of order (2a)")

        # Create a new branch
        new_branch = "test/mods"
        self.assertTrue(git.current_branch() == test_branch, "Should be on test branch")
        self.assertTrue(os.path.isfile(os.path.join(init_path, 'deleteme.txt')), "Expected file disappeared (1)")
        self.assertFalse(git.branch_exists(new_branch), "New branch already exists")
        self.assertTrue(git.create_branch(new_branch), "Unable to create mods branch")
        self.assertTrue(git.current_branch() == new_branch, "Should be on mods branch")
        self.assertTrue(os.path.isfile(os.path.join(init_path, 'deleteme.txt')), "Expected file disappeared (2)")

        # Modify a file
        with open(os.path.join(init_path, 'changeme.txt'), 'w') as temp_file:
            temp_file.write("Here's some modified content")

        # Delete a file
        os.unlink(os.path.join(init_path, 'deleteme.txt'))

        # Move (rename) a file
        shutil.move(os.path.join(init_path, 'moveme.txt'), os.path.join(init_path, 'movedme.txt'))

        # Add a new file
        with open(os.path.join(init_path, "new-file.dat"), 'w') as temp_file:
            temp_file.write("This is a new file")
        self.assertTrue(git.add("new-file.dat"), "Unable to add new-file.dat")

        # Get status of repo
        status = git.status_dict()
        self.assertTrue(len(status['notstaged']['items']) == 3, "Should be three unstaged items")
        self.assertTrue(len(status['untracked']['items']) == 1, "Should be one untracked item")  # Moved item
        self.assertTrue(git.current_branch() == new_branch, "Should be on mods branch (2)")

        # Commit changes
        self.assertTrue(git.add(), "Unable to add mods")
        self.assertTrue(git.current_branch() == new_branch, "Should be on mods branch (3)")
        self.assertTrue(git.commit("MODS - A"), "Unable to commit mods")
        self.assertTrue(git.current_branch() == new_branch, "Should be on mods branch (4)")

        # Remember the number of commits on this branch
        commits_2 = git.get_commits()
        num_commits_2 = len(commits_2)
        for cc in commits_2:
            out.put_color("{0}: {1}".format(cc['date'], cc['message'].strip()), 'yellow')

        # Assertions on commit order
        self.assertTrue("MODS - A" in commits_2[0]['message'], "Commits out of order (2b)")
        self.assertTrue("BASE - 1" in commits_2[1]['message'], "Commits out of order (3)")
        self.assertTrue("Initial commit" in commits_2[2]['message'], "Commits out of order (4)")

        # Test best common ancestor
        common_ancestor = git.get_common_ancestor_details(new_branch, test_branch)
        out.put_color(common_ancestor, 'green')
        self.assertTrue("BASE - 1" in common_ancestor['message'], "Did not detect common ancestor")

        # Tag the current state
        self.assertTrue(git.tag("0.1.1"), "Unable to tag version 0.1.1")

        if test_remote:
            # Push current commits to mods branch
            self.assertTrue(git.push(), "Pre-rebase push failed")
            self.assertFalse(git.push_needed(), "Pre-rebase push still needed???")

            # Remember the commits on this remote branch
            remote_commits_1 = git.get_commits('origin/' + new_branch)
            for cc in remote_commits_1:
                out.put_color("{0}: {1}".format(cc['date'], cc['message'].strip()), 'magenta')

        # Return to previous state
        self.assertTrue(git.reset(reset_point="0.1"), "Unable to return to version 0.1")

        if test_remote:
            # Pull should be needed
            self.assertTrue(git.pull_needed(), "Post-reset should need pull")
            # Try to push this previous state, and expect failure
            # ToDo: Add checking to push() for the following error:
            #   ! [rejected]        mjg/test -> mjg/test (non-fast-forward)
            # self.assertFalse(git.push(), "Push from tag should have failed")
            # Force push this previous state
            self.assertTrue(git.push(force=True), "Force push failed")
            # Pull should not be needed
            self.assertFalse(git.pull_needed(), "Post-force-push should not need pull")

        # Restore 0.1.1
        self.assertTrue(git.merge(new_branch, '0.1.1'), "Merge of tagged commits failed")
        # Delete the tag
        self.assertTrue(git.delete_tag('0.1.1'), "Could not delete tag 0.1.1")

        # Compare the commits on this remote branch
        if test_remote:
            remote_commits_2 = git.get_commits('origin/' + new_branch)
            for cc in remote_commits_2:
                out.put_color("{0}: {1}".format(cc['date'], cc['message'].strip()), 'red')

            self.assertTrue(len(remote_commits_1) > len(remote_commits_2), "remote commits should have decreased")

        # Make some more changes on original branch so that rebase test can be done
        self.assertTrue(git.checkout_branch(test_branch), "Unable to return to test branch (rebase)")
        # Modify a file
        with open(os.path.join(init_path, 'changeme2.txt'), 'w') as temp_file:
            temp_file.write("Here's some newly-modified content")

        # Commit changes
        self.assertTrue(git.add(), "Unable to add mods (rebase)")
        self.assertTrue(git.commit("BASE - 2"), "Unable to commit mods (rebase)")

        # Remember the number of commits on this branch
        commits_3 = git.get_commits()
        num_commits_3 = len(commits_3)
        for cc in commits_3:
            out.put_color("{0}: {1}".format(cc['date'], cc['message'].strip()), 'blue')

        # Assertions on commit order
        self.assertTrue("BASE - 2" in commits_3[0]['message'], "Commits out of order (5)")
        self.assertTrue("BASE - 1" in commits_3[1]['message'], "Commits out of order (6)")
        self.assertTrue("Initial commit" in commits_3[2]['message'], "Commits out of order (7)")

        # Rebase test branch
        self.assertTrue(git.checkout_branch(new_branch), "Unable to return to new_branch (rebase)")
        self.assertTrue(git.rebase(new_branch, test_branch) == 'S', "Rebase did not return 'S'")

        # Remember the number of commits on this branch
        commits_4 = git.get_commits()
        num_commits_4 = len(commits_4)
        for cc in commits_4:
            out.put_color("{0}: {1}".format(cc['date'], cc['message'].strip()), 'magenta')

        # Assertions on commit order
        self.assertTrue("MODS - A" in commits_4[0]['message'], "Commits out of order (8)")
        self.assertTrue("BASE - 2" in commits_4[1]['message'], "Commits out of order (9)")
        self.assertTrue("BASE - 1" in commits_4[2]['message'], "Commits out of order (10)")
        self.assertTrue("Initial commit" in commits_4[3]['message'], "Commits out of order (11)")

        # Check merged branches
        merged_to_new = git.merged_branches(new_branch)
        merged_to_test = git.merged_branches(test_branch)
        self.assertTrue(test_branch in merged_to_new['local'], "New branch should contain test branch")
        self.assertTrue(new_branch not in merged_to_test['local'], "New branch should not be in test branch")

        # Merge mods into test_branch
        self.assertTrue(git.merge(test_branch, new_branch), "Unable to merge branches")
        self.assertTrue(git.current_branch() == new_branch, "Should be on mods branch")

        # Check merged branches (local)
        merged_to_test = git.merged_branches(test_branch)
        self.assertTrue(new_branch in merged_to_test['local'], "New branch should have been merged to test branch")
        self.assertTrue(new_branch not in merged_to_test['remote'], "New branch shouldn't have been pushed after merge")

        self.assertTrue(git.checkout_branch(test_branch), "Return to test branch")
        self.assertTrue(git.current_branch() == test_branch, "Should be back on test branch")

        # Delete mods branch
        self.assertTrue(git.delete_branch(new_branch), "Could not delete local mods branch")
        # self.assertTrue(git.delete_remote_branch(new_branch), "Could not delete remote mods branch")

        # Diff 0.1 against 0.2
        self.assertTrue(git.tag("0.2"), "Unable to tag version 0.2")
        self.assertTrue(git.most_recent_tag() == '0.2', "0.2 is most-recent tag")
        changes = git.diff_branches("0.1", "0.2")

        # Git displays moved file differently on old versions of Git
        # ToDo: Handle the two different ways moved files are displayed
        # if IS_APP_SERVER:
        #     self.assertTrue(len(changes['A']) == 3, "Three files should have been added")
        #     self.assertTrue(len(changes['M']) == 1, "One file should have been modified (moved counts as modified)")
        #     self.assertTrue(len(changes['D']) == 2, "Two files should have been deleted")
        # else:
        self.assertTrue(len(changes['A']) == 2, "Two files should have been added")
        self.assertTrue(len(changes['M']) == 2, "Two files should have been modified (moved counts as modified)")
        self.assertTrue(len(changes['D']) == 1, "One file should have been deleted")

        # Push the results
        if test_remote:
            self.assertTrue(git.push_needed(), "Push is needed")
            self.assertTrue(git.push(test_branch), "Unable to push test branch")
            self.assertTrue(git.push(new_branch), "Unable to push new branch")
            self.assertFalse(git.push_needed(), "Push is not needed")

        merged_to_test = git.merged_branches(test_branch)

        if test_remote:
            self.assertTrue(
                "origin/{0}".format(new_branch) in merged_to_test['remote'],
                "Test branch should have been pushed after merge"
            )

        # Move (rename) a file
        shutil.move(os.path.join(init_path, 'movedme.txt'), os.path.join(init_path, 'movedmeagain.txt'))

        # Repo is now dirty
        self.assertFalse(git.is_clean(), "Repo should be dirty")

        # Reset the repo
        self.assertTrue(git.reset(), "Unable to reset repo")
        self.assertTrue(git.is_unmodified(), "Repo should be unmodified after a reset")
        self.assertFalse(git.is_clean(), "Untracked files are unclean")

        # Reset repo and remove untracked files
        self.assertTrue(git.reset(None, False), "Unable to reset repo and remove untracked files")
        self.assertTrue(git.is_clean(), "Untracked files should have been removed")

        # Delete the 0.1 tag
        self.assertTrue(git.delete_tag("0.1"), "Delete tag 0.1")
        self.assertTrue(git.delete_tag("0.2"), "Delete tag 0.2")
        # Check if 0.1 tag exists
        self.assertFalse(git.tag_exists("0.1"), "Tag 0.1 should have been deleted")

        # Delete the test branches
        self.assertTrue(git.delete_branch(test_branch), "Could not delete local test branch (2)")
        if test_remote:
            # This branch was deleted, and then pulled back from remote
            self.assertTrue(git.delete_branch(new_branch), "Could not delete local test branch (3)")
        self.assertTrue(len(git.list_branches()) == 1, "Only master branch should be left (local)")

        # Delete the test branches
        if test_remote:
            self.assertTrue(git.delete_remote_branch(test_branch), "Could not delete remote test branch (2)")
            self.assertTrue(git.delete_remote_branch(new_branch), "Could not delete remote test branch (3)")
            self.assertTrue(len(git.list_remote_branches()) == 1, "Only master branch should be left (remote)")

        # Make sure last branch cannot be deleted (suppress the error)
        out.suppressConsoleOutput = True
        self.assertFalse(git.delete_branch("master"), "Can not delete last existing branch")
        out.suppressConsoleOutput = False

        # Test function to run any git command
        exe = git.run_git_command('git --help')
        self.assertTrue(exe.return_code == 0, "Git --help command returned non-0 status")
        self.assertTrue('usage' in exe.get_output(), "Git --help command not including 'usage'")

        # Remove the test directory and repo
        os.chdir(self.unit_test_sandbox)
        if os.path.isdir(init_path):
            shutil.rmtree(init_path)


if __name__ == '__main__':
    unittest.main()
