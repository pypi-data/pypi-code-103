# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def run(args=None):
    import argparse
    from pidb import create_app

    parser = argparse.ArgumentParser(description="Run the webserver. Never use this for production!!!")
    parser.add_argument('--debug', action='store_true', default=False, help="Run the server in debug mode.")
    parser.add_argument('--host', default=None, help="Define the host, leave empty for localhost. (e.g. 0.0.0.0)")
    parser.add_argument('--port', default=None, type=int, help="Define the port, leave empty for 5000")
    args = parser.parse_args(args=args)

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


def db_init(args=None):
    from pidb import create_app
    from pidb.models import db

    # Create the database
    print("Initializing database ...")
    app = create_app()
    with app.app_context():
        db.create_all()


def db_clean(force_yes=False):
    import sys
    from pidb import create_app
    from pidb.models import db

    if '-f' in sys.argv or '--force' in sys.argv:
        force_yes = True

    if force_yes:
        doit = True
    else:
        doit = input("Are you sure you want to empty the database? [yes/no]: ") == 'yes'

    if doit:
        app = create_app()
        with app.app_context():
            db.drop_all()
            db.create_all()

        print("Database is emptied!")
    else:
        print("Cancelled database clean action.")


def add_task(args=None):
    import json
    import argparse
    import requests

    from . import control
    from . import exceptions
    from pidb import create_app
    from pidb import models

    parser = argparse.ArgumentParser(description="Add a task from a task json.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('task', help="A task json file.")
    parser.add_argument('-db', '--database-insert', action="store_true", help="Store directly in the database, not via the api.")
    parser.add_argument('-p', '--project', required=True, help="Assign the task to a project.")
    parser.add_argument('-u', '--users', nargs='+', help="A list of users to assign the task to.")
    parser.add_argument('-g', '--groups', nargs='+', help="A list of groups to assign the task to.")
    parser.add_argument('-t', '--tags', nargs='+', help="A list of tags to add to the task.")
    parser.add_argument('-d', '--distribute-group', help="Assign the task to be distributed in a group.")
    parser.add_argument('-gen', '--generator-url', default=None, help="The URL to indicate from where this task is requested/originated.")
    parser.add_argument('-an', '--application-name', default=None, help="The name of the application that should consume this task.")
    parser.add_argument('-av', '--application-version', default=None, help="The minimally required version of the consuming application.")
    parser.add_argument('-cu', '--callback-url', default=None, help="Callback URL.")
    parser.add_argument('-cc', '--callback-content', default=None, help="Callback content.")
    parser.add_argument('--url', default="http://localhost:5000", help="Base URL where the pidb is running.")
    parser.add_argument('--old', action='store_true', help="Use old api located at /data instead of /api/v1")
    args = parser.parse_args(args=args)

    if args.old:
        tasks_endpoint = '{}/data/tasks'.format(args.url)
    else:
        tasks_endpoint = '{}/api/v1/tasks'.format(args.url)

    task_info = {'project': args.project}

    task_info['users'] = args.users
    task_info['groups'] = args.groups
    task_info['tags'] = args.tags
    task_info['distribute_in_group'] = args.distribute_group
    task_info['generator_url'] = args.generator_url
    task_info['application_name'] = args.application_name
    task_info['application_version'] = args.application_version
    task_info['callback_url'] = args.callback_url
    task_info['callback_content'] = args.callback_content

    with open(args.task) as task_json:
        task_info['content'] = task_json.read()
        task_info['template'] = json.loads(task_info['content'])[0]['template']
    
    print("task_info: {}".format(task_info))

    if args.database_insert:
        print("Storing directly in the database, not via the api.")
        with create_app().app_context():
            try:
                task_info['commit_to_db'] = True
                control.insert_task(**task_info)
            except exceptions.TaskManagerError:
                models.db.session.rollback()
                raise
        print("Task was added to the pidb.")

    else:
        try:
            print("tasks_endpoint: {}".format(tasks_endpoint))
            response = requests.post(tasks_endpoint, json=task_info)
            if response.status_code not in [200, 201]:
                raise ValueError("Response had invalid status [{}]: {}".format(response.status_code, response.text))
            else:
                print("Task was added to the pidb.")
        except requests.exceptions.ConnectionError as e:
            print("The pidb is not running (correctly). Make sure it running and reachable. We tried to look at: {}".format(tasks_endpoint))


def add_user(args=None):
    import json
    import argparse

    from pidb import create_app
    from pidb import models
    from pidb import user_datastore
    from flask_security import hash_password

    parser = argparse.ArgumentParser(description="Add a user to the pidb.")
    parser.add_argument('-u', '--username', required=True, help="The username.")
    parser.add_argument('-p', '--password', required=True, help="The password.")
    parser.add_argument('-n', '--full-name', required=True, help="The full name of the user")
    parser.add_argument('-e', '--email', required=True, help="The e-mail.")
    parser.add_argument('-i', '--inactive', default=False, action='store_true', help="If the user starts active or not", required=False)
    parser.add_argument('-f', '--force', action='store_true', default=False, help="Do not ask questions, just do it")
    args = parser.parse_args(args=args)

    app = create_app()
    with app.app_context():
        db = models.db

        user = {"username": args.username,
                "password": hash_password(args.password),
                "name": args.full_name,
                "email": args.email,
                "active": not args.inactive}
        db_user = user_datastore.create_user(**user)

        doit = False
        if not args.force:
            doit = input("Are you sure you want to commit user [{}], to database '{}' [yes/no]: ".format(user['username'], app.config['SQLALCHEMY_DATABASE_URI'])) == 'yes'
        if doit or args.force:
            db.session.commit()
            print("\n * Committed to the database.")
        else:
            db.session.rollback()
            print("\n * Cancelled.")


def config_from_file(args=None):
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Configure the pidb from a config json file.")
    parser.add_argument('config', metavar="JSON", help="A json file containing the config for the pidb.",  default=(None if sys.stdin.isatty() else sys.stdin))
    args = parser.parse_args(args=args)

    from . import create_app
    from .util.helpers import load_config_file
    app = create_app()
    load_config_file(app, args.config)


def create_random_test_tasks(args=None):
    import pathlib
    from . import create_app
    from .tests.loaders import create_random_test_tasks

    base_tasks = pathlib.Path(__file__).parent / 'tests' / 'tasks'
    create_random_test_tasks(create_app(), base_tasks)
    
    print("Random tasks generated!")


def create_random_test_taskgroup(args=None):
    import argparse

    from . import create_app
    from .tests.loaders import create_random_test_taskgroup

    parser = argparse.ArgumentParser(description="Create a taskgroup from a random selection of tasks.")
    parser.add_argument('-n', '--num-tasks', default=3, required=False, help="Number of tasks")
    args = parser.parse_args(args)

    create_random_test_taskgroup(create_app(), num_tasks=int(args.num_tasks))


def flask_manager(args=None):
    from flask_script import Manager
    from flask_migrate import Migrate, MigrateCommand

    from pidb import create_app
    from pidb.models import db

    app = create_app(use_sentry=False)
    with app.app_context():
        migrate = Migrate()
        migrate.init_app(app=app, db=db, directory='migrations')
        manager = Manager(app)
        manager.add_command('db', MigrateCommand)

        manager.run()


def run_gunicorn(args=None):
    from pidb import create_app

    try:
        from gunicorn.app.base import BaseApplication
    except ImportError:
        print("In order to run the server with gunicorn install it with: pip install gunicorn")
        return False

    class WSGIServer(BaseApplication):
        def __init__(self, app):
            self.application = app
            super(WSGIServer, self).__init__("%(prog)s [OPTIONS]")
            #super(WSGIServer, self).__init__()

        def load_config(self):
            parser = self.cfg.parser()
            args = parser.parse_args()

            for k, v in list(args.__dict__.items()):
                if v is None:
                    continue
                if k == "args":
                    continue
                self.cfg.set(k.lower(), v)

        def load(self):
            return self.application

    WSGIServer(create_app()).run()


def add_template(args=None):
    import json
    import argparse
    import requests
    import os
    import netrc
    import urllib.parse


    parser = argparse.ArgumentParser(description="Add a template from a template json.")
    parser.add_argument('server', metavar='HOSTNAME', type=str, help='The server to update on')
    parser.add_argument('template', type=argparse.FileType('rb'), help="A template json file.")
    parser.add_argument('--old', action='store_true', help="Use old api located at /data instead of /api/v1")
    args = parser.parse_args(args=args)
    template_json = json.load(args.template)

    request_data = {
        "content": json.dumps(template_json),
        "label": template_json['template_name']
    }

    if args.old:
        url = '{}/data/task_templates'.format(args.server)
    else:
        url = '{}/api/v1/task_templates'.format(args.server)

    # NETRC!
    try:
        parsed_server = urllib.parse.urlparse(args.server)
        netrc_file = os.path.join('~', '_netrc' if os.name == 'nt' else '.netrc')
        netrc_file = os.path.expanduser(netrc_file)
        user, _, password = netrc.netrc(netrc_file).authenticators(parsed_server.netloc)
        response = requests.post(url, json=request_data, auth=(user, password))
    except (TypeError, IOError):
        response = requests.post(url, json=request_data)


def update_template(args=None):
    import argparse
    import json
    import requests

    parser = argparse.ArgumentParser(description='Update template on the server')
    parser.add_argument('server', metavar='HOSTNAME', type=str, help='The server to update on')
    parser.add_argument('path', metavar='TEMPLATE.JSON', help="The path of the file to use")
    parser.add_argument('--name', metavar='NAME', required=False, help='The name of the template on the server')
    parser.add_argument('--user', metavar='USER', help="username for the server login, if given a password will be prompted")
    parser.add_argument('--old', action='store_true', help="Use old api located at /data instead of /api/v1")
    args = parser.parse_args()

    with open(args.path, 'r') as fin:
        json_data = json.load(fin)

    request_data = {
        "content": json.dumps(json_data)
    }

    if not args.name:
        name = json_data['template_name']
    else:
        name = args.name

    if args.old:
        url = '{}/data/task_templates/{}'.format(args.server, name)
    else:
        url = '{}/api/v1/task_templates/{}'.format(args.server, name)
    print('Uploading template to {}'.format(url))
    print('Using data:\n{}'.format(request_data))

    if args.user:
        import getpass

        password = getpass.getpass('Please provide the password for user "{}":  '.format(args.user))
        response = requests.put(url, json=request_data, auth=(args.user, password))
    else:
        import os
        import netrc
        import urllib.parse

        # NETRC!
        try:
            parsed_server = urllib.parse.urlparse(args.server)
            netrc_file = os.path.join('~', '_netrc' if os.name == 'nt' else '.netrc')
            netrc_file = os.path.expanduser(netrc_file)
            user, _, password = netrc.netrc(netrc_file).authenticators(parsed_server.netloc)
            response = requests.put(url, json=request_data, auth=(user, password))
        except (TypeError, IOError):
            response = requests.put(url, json=request_data)

    print('Response:\n[status {}]\n{}'.format(response.status_code, response.text))

def bootstrap_db(args=None):
    import argparse
    import random
    from pidb.models import Subject, Experiment, Finding, Label, db
    from pidb import create_app
    
    parser = argparse.ArgumentParser(description="Bootstrap the db with generated values for testing purposes")
    parser.add_argument('--wipe', action='store_true', default=False, help="Wipe the tables before populating")
    parser.add_argument('-e', '--experiments', type=int, default=1000, help="Number of experiments, default is 1000")
    parser.add_argument('-s', '--subjects', type=int, default=1000, help="Number of subjects, default is 1000")
    parser.add_argument('-f', '--findings', type=int, default=1000, help="Number of findings, default is 1000")
    
    args = parser.parse_args(args=args)
    
    app = create_app()
    
    with app.app_context():
        if args.wipe:
            Experiment.query.delete()
            Subject.query.delete()
            Finding.query.delete()
            Label.query.delete()
            db.session.commit()

        task_templates = ["qa_1", "qa_2", "segmentation"]
        labels = [Label(label_text="Done"), Label(label_text="In progress"), Label(label_text="Rejected")]

        for label in labels:
            db.session.add(label)

        subjects = []
        for i in range(args.subjects):
            subject = Subject(study_id=f'generated_study_{i}', generator_url='generated')
            db.session.add(subject)
            subjects.append(subject)
        
        experiments = []
        for i in range(args.experiments):
            experiment = Experiment(label=f"generated_experiment_{i}", subject=random.choice(subjects))
            db.session.add(experiment)
            experiments.append(experiment)

        findings = []
        for i in range(args.findings):
            finding = Finding(experiment=random.choice(experiments), 
                                label=random.choice(labels), 
                                task_template=random.choice(task_templates),
                                generator_url="generated_finding"
                                )
            db.session.add(finding)
            findings.append(finding)

        db.session.commit()