import json
import string
import random

from .. import models

import json

class CannotReachIfdbException(Exception):
    pass


class InvalidParameterException(Exception):
    pass


class FindingScraper:
    DEFAULT_FINDING_NAME = '__main__'
    # At the end so all methods are defined
    WIDGET_PARSERS = {}

    def __init__(self, db, experiment_id, generator_url, task_template):
        self.db = db
        self.experiment_id = experiment_id
        self.generator_url = generator_url
        self.task_template = task_template
        self.finding_stack = []

        # Set the widget parsers so they are bound methods
        self.WIDGET_PARSERS.update({
            "TabsWidget": self.parse_tabs,
            "ListingWidget": self.parse_listing,
            "BoxWidget": self.parse_box,
        })

    def scrape(self, qa_fields, data):
        self.push_finding(self.DEFAULT_FINDING_NAME)
        for field_name, field_spec in qa_fields.items():
            if field_name not in data:
                data[field_name] = []
            self.parse_qa_field(field_name, field_spec, data[field_name])
        self.pop_finding()

    @property
    def current_finding(self):
        return self.finding_stack[-1]

    def push_finding(self, label_text):
        label = models.Label(label_text=label_text)
        # add label first
        try:
            self.db.session.add(label)
            self.db.session.commit()
        except:
            raise InvalidParameterException('Could not put label: {}'.format(label_text))

        finding = models.Finding(experiment_id=self.experiment_id, label_id=label.label_id, generator_url=self.generator_url, task_template=self.task_template)
        # add experiment
        try:
            self.db.session.add(finding)
            self.db.session.commit()
        except:
            raise InvalidParameterException('Could not put findings for: {}'.format(label_text))

        # TODO: Remove this test mock code
        # import random
        # finding = {'finding_id': f'{label}_{random.randint(0, 999999):06d}'}

        # TODO: Remove this debug print statement
        print(f'Adding finding [{label_text}] to {self.experiment_id} with {self.generator_url} -> {finding.finding_id}')

        self.finding_stack.append(finding.finding_id)

    def pop_finding(self):
        self.finding_stack.pop()

    def add_property(self, label, value):
        # TODO: Remove this debug print statement
        print(f'Adding property [{label}] {value!r} to finding {self.current_finding}')
        prop = models.Property(label=label, value=value, finding_id=self.current_finding)
        self.db.session.add(prop)
        self.db.session.commit()


    def parse_control_default(self, name, qa_spec, data):
        self.add_property(name, json.dumps(data))

    def parse_tabs(self, name, qa_spec, data):
        for tab_name, tab_content in qa_spec['content'].items():
            for field_name, field_spec in tab_content.items():
                if field_name not in data:
                    data[field_name] = []
                self.parse_qa_field(field_name, field_spec, data[field_name])

    def parse_box(self, name, qa_spec, data):
        for field_name, field_spec in qa_spec['content'].items():
            if field_name not in data:
                data[field_name] = []
            self.parse_qa_field(field_name, field_spec, data[field_name])

    def parse_listing(self, name, qa_spec, data):
        label = qa_spec['label']
        for entry in data:
            # Create a new finding and parse all elements
            self.push_finding(label)

            for field_name, field_spec in qa_spec['content'].items():
                if field_name not in entry:
                    entry[field_name] = []
                self.parse_qa_field(field_name, field_spec, entry[field_name])

            self.pop_finding()

    def parse_qa_field(self, name, qa_spec, data):
        control_type = qa_spec['control']

        print(f'Parsing {name}: {control_type}')
        parse_func = self.WIDGET_PARSERS.get(control_type, self.parse_control_default)
        parse_func(name, qa_spec, data)


def ingest_json(app, findings_data, template_data, task_template, subject_study_id, subject_generator_url, experiment_label, experiment_date, finding_generator_url):
    """
    Ingest json to pidb

    :raises InvalidParameterException, NoSyncableDataException, CannotReachIfdbException

    :param experiment_date: ISO 8601 datestring
    :param subject_generator_url: url to subject generator
    :param subject_study_id: study id of subject (e.g. ergoid)
    :param json_file_path: path to the json file
    :param task_template: template used for findings
    :return: No return value
    """

    label_mappings = {}
    with app.app_context():
        db = models.db
        # put subject
        subject = models.Subject(study_id=subject_study_id, generator_url=subject_generator_url)
        try:
            db.session.add(subject)
            db.session.commit()
        except:
            raise InvalidParameterException('Could not put subject: {} {}'.format(subject_study_id, subject_generator_url))

        # put experiment
        experiment = models.Experiment(subject_id=subject.subject_id, label=experiment_label, date=experiment_date)
        try:
            db.session.add(experiment)
            db.session.commit()
        except:
            raise InvalidParameterException('Could not put experiment {} {}'.format(experiment_label, experiment_date))
        
    # pidb.delete_findings_for_experiment_by_template(experiment['experiment_id'], task_template)

        # second we do the actual ingestion
        qa_fields = template_data['qa_fields']
        scraper = FindingScraper(db, experiment.experiment_id, finding_generator_url, task_template)
        scraper.scrape(qa_fields, findings_data)