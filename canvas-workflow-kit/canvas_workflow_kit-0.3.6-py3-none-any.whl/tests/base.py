import glob
import json
import os

from os.path import basename
from unittest import TestCase

from pathlib import Path
from stringcase import camelcase

from canvas_workflow_kit.patient import Patient
from canvas_workflow_kit.protocol import ProtocolResult


class SDKBaseTest(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            from canvas_workflow_kit import settings
            self.mocks_path = f'{settings.BASE_DIR}/tests/mock_data'
        except:
            self.mocks_path = '.'

    def load_patient(self, patient_key) -> Patient:
        data = {
            'billingLineItems': [],
            'conditions': [],
            'imagingReports': [],
            'immunizations': [],
            'inpatient_stays': [],
            'instructions': [],
            'interviews': [],
            'labReports': [],
            'medications': [],
            'referralReports': [],
            'referrals': [],
            'vitalSigns': [],
            'patient': {},
            'protocolOverrides': [],
            'changeTypes': [],
            'protocols': [],
        }

        file_loaded = False
        patient_path = Path(f'{self.mocks_path}/{patient_key}/')

        assert patient_path.is_dir(), f'no patient directory exists from {patient_path}'

        for filepath in patient_path.glob('*.json'):
            file_loaded = True

            filename = str(basename(filepath))
            field = camelcase(filename.split('.')[0])

            with open(filepath, 'r') as fh:
                data[field] = json.load(fh)

        assert file_loaded, f'no JSON files were loaded from {patient_path}'

        data['patient']['key'] = patient_key

        return Patient(data)

    def load_patient_data(self, patient_key, field):
        """
        Load data from mock data JSON files dumped by the dump_patient command.
        """
        filename = f'{self.mocks_path}/{patient_key}/{field}.json'

        if not os.path.exists(filename):
            if field == 'patient':
                raise Exception(f'Missing mock patient data for {patient_key}!')

            return []

        with open(filename, 'r') as fh:
            return json.load(fh)

    def assertIsNotApplicable(self, result: ProtocolResult):
        self.assertEqual('not_applicable', result.status)
        self.assertEqual('', result.narrative)
        self.assertEqual([], result.recommendations)
        self.assertIsNone(result.due_in)
