
from generallibrary import CodeLine, comma_and_and, EnvVar

from itertools import chain


class _PackagerWorkflow:
    """ Light handling of workflow logic. """
    @staticmethod
    def _var(string):
        return f"${{{{ {string} }}}}"

    @staticmethod
    def _commit_msg_if(**conditions):
        checks = [f"contains(github.event.head_commit.message, '[CI {key}]') == {str(value).lower()}" for key, value in conditions.items()]
        return f"if: {' && '.join(checks)}"

    _commit_msg = "github.event.head_commit.message"
    _action_checkout = "actions/checkout@v2"
    _action_setup_python = "actions/setup-python@v2"
    _action_setup_ssh = "webfactory/ssh-agent@v0.5.3"
    _matrix_os = "matrix.os"
    _matrix_python_version = "matrix.python-version"

    def get_triggers(self):
        """ :param generalpackager.Packager self: """
        on = CodeLine("on:")
        push = on.add_node("push:")
        branches = push.add_node("branches:")
        branches.add_node("- master")
        return on

    def _get_step(self, name, *codelines):
        step = CodeLine(f"- name: {name}")
        for codeline in codelines:
            if codeline:
                step.add_node(codeline)
        return step

    def step_setup_ssh(self):
        """ :param generalpackager.Packager self: """
        with_ = CodeLine("with:")
        with_.add_node("ssh-private-key: ${{ secrets.GIT_SSH }}")
        return self._get_step(f"Set up Git SSH", f"uses: {self._action_setup_ssh}", with_)

    def step_setup_python(self, version):
        """ :param generalpackager.Packager self:
            :param version: """
        with_ = CodeLine("with:")
        with_.add_node(f"python-version: {version}")
        return self._get_step(f"Set up python version {version}", f"uses: {self._action_setup_python}", with_)

    def step_install_necessities(self):
        """ :param generalpackager.Packager self: """
        run = CodeLine("run: |")
        run.add_node("python -m pip install --upgrade pip")
        run.add_node(f"pip install setuptools wheel twine")
        return self._get_step(f"Install necessities pip, setuptools, wheel, twine", run)

    def step_install_package_pip(self, *packagers):
        """ Supply Packagers to create pip install steps for.

            :param generalpackager.Packager self: """
        names = [p.name for p in packagers]
        run = CodeLine(f"run: pip install {' '.join(names)}")
        return self._get_step(f"Install pip packages {comma_and_and(*names, period=False)}", run)

    def step_install_package_git(self, *packagers):
        """ Supply Packagers to create git install steps for.

            :param generalpackager.Packager self: """
        run = CodeLine(f"run: |")
        for packager in packagers:
            run.add_node(f"pip install git+ssh://git@github.com/{packager.github.owner}/{packager.name}.git")

        for packager in chain(packagers, self.summary_packagers):  # Also clone summary_packagers for syncing
            run.add_node(f"git clone ssh://git@github.com/{packager.github.owner}/{packager.name}.git")

        return self._get_step(f"Install and clone {len(packagers)} git repos", run)

    def get_env(self):
        """ :param generalpackager.Packager self: """
        env = CodeLine("env:")
        for packager in self.get_all():
            for env_var in packager.localmodule.get_env_vars():
                if env_var.actions_name and env_var.name not in str(env):
                    env.add_node(f"{env_var.name}: {env_var.actions_name}")
        if not env.get_children():
            return None
        return env

    def steps_setup(self, python_version):
        """ :param generalpackager.Packager self:
            :param python_version: """
        steps = CodeLine("steps:")
        steps.add_node(self.step_setup_ssh())
        steps.add_node(self.step_setup_python(version=python_version))
        steps.add_node(self.step_install_necessities())
        steps.add_node(self.step_install_package_git(*self.get_ordered_packagers()))
        return steps

    def get_unittest_job(self):
        """ :param generalpackager.Packager self: """
        job = CodeLine("unittest:")
        job.add_node(self._commit_msg_if(SKIP=False, AUTO=False))
        job.add_node(f"runs-on: {self._var(self._matrix_os)}")
        strategy = job.add_node("strategy:")
        matrix = strategy.add_node("matrix:")
        matrix.add_node(f"python-version: {list(self.python)}".replace("'", ""))
        matrix.add_node(f"os: {[f'{os}-latest' for os in self.os]}".replace("'", ""))

        steps = job.add_node(self.steps_setup(python_version=self._var(self._matrix_python_version)))
        steps.add_node(self.step_run_packager_method("workflow_unittest"))
        return job

    def get_sync_job(self):
        """ :param generalpackager.Packager self: """
        job = CodeLine("sync:")
        job.add_node("needs: unittest")
        job.add_node(f"runs-on: ubuntu-latest")
        steps = job.add_node(self.steps_setup(python_version=self.python[0]))
        steps.add_node(self.step_run_packager_method("workflow_sync"))
        return job

    def step_run_packager_method(self, method):
        """ :param generalpackager.Packager self:
            :param method: """
        run = CodeLine(f'run: |')
        run.add_node(f'python -c "from generalpackager import Packager; Packager(\'generalpackager\').{method}()"')
        return self._get_step(f"Run Packager method '{method}'", run, self.get_env())

    def run_ordered_methods(self, *funcs):
        """ :param generalpackager.Packager self: """
        order = self.get_ordered_packagers()
        for func in funcs:
            for packager in order:
                func(packager)

    def workflow_unittest(self):
        """ :param generalpackager.Packager self: """
        self.run_ordered_methods(
            lambda packager: packager.generate_localfiles(aesthetic=False),
            lambda packager: packager.localrepo.pip_install(),
            lambda packager: packager.localrepo.unittest(),
        )

    def workflow_sync(self):
        """ Runs in workflow once Packagers have created each LocalRepo from latest master commit.

            :param generalpackager.Packager self: """
        trigger_repo = str(EnvVar('GITHUB_REPOSITORY')).split('/')[1]
        msg1 = f"[CI AUTO] Sync triggered by {trigger_repo}"
        msg2 = f"[CI AUTO] Publish triggered by {trigger_repo}"

        self.run_ordered_methods(
            lambda packager: packager.if_publish_bump(),
            lambda packager: packager.generate_localfiles(aesthetic=True),
            lambda packager: packager.localrepo.pip_install(),
            lambda packager: packager.localrepo.unittest(),  # For good measure
            lambda packager, msg=msg1: packager.commit_and_push(message=msg, tag=False),
            lambda packager, msg=msg2: packager.if_publish_publish(message=msg),
            lambda packager: packager.sync_github_metadata(),
        )

        for packager in self.summary_packagers:
            packager.upload_package_summary(msg=msg1)

    def upload_package_summary(self, msg):
        """ :param generalpackager.Packager self: """
        self.file_secret_readme.generate()
        self.commit_and_push(message=msg)

    def if_publish_bump(self):
        """ Bump if updated and any other Packager is bumped.

            :param generalpackager.Packager self: """
        if self.general_bumped_set() and not self.is_bumped() and self.compare_local_to_pypi(aesthetic=False):
            self.localrepo.bump_version()

    def if_publish_publish(self, message):
        """ :param generalpackager.Packager self:
            :param message: """
        if self.is_bumped():
            self.file_readme.generate()
            self.commit_and_push(message=message, tag=True)
            if not self.localrepo.private:
                self.localrepo.upload()







