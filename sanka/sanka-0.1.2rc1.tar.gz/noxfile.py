import nox


PROJECT_NAME = 'sanka'
VENV = f'{PROJECT_NAME}-venv'
TESTDIR = '.'

supported_python_versions = [
    '3.6',
    '3.7',
    '3.8',
    '3.9',
    '3.10',
]

@nox.session(name=VENV, python=supported_python_versions, reuse_venv=True)
def tests(session):
    session.install('.')
    session.install('-r', 'requirements.txt')
    session.run(
        'python', '-m',
        'coverage', 'run', '--branch',
        '--omit', '.nox/*,noxfile.py,setup.py,test*',
        '--source', '.',
        '-m', 'unittest', 'discover',
        '-s', TESTDIR
    )
    session.run('coverage', 'report', '-m')
    session.run('coverage', 'xml')


@nox.session(name=f'build-{PROJECT_NAME}', reuse_venv=True)
def build(session):
    session.install('.')
    session.run('python', 'setup.py', 'sdist')


# TODO (withtwoemms) -- leverage gitpython to show version on-demand

