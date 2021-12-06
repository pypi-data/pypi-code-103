import datetime
import tempfile

from io import StringIO

from canvas_workflow_kit import settings
from unittest import TestCase

from canvas_workflow_kit.management.commands.build_medication_class_path_value_set import (
    BuildMedicationClassPathValueSet
)


class TestBuildMedicationClassPathValueSet(TestCase):

    def test_generate_full_classes(self):
        tested = BuildMedicationClassPathValueSet('')
        classes = [{
            'name': 'Penicillin',
            'path_ids': [4]
        }, {
            'name': 'Penicillin Antibiotics',
            'path_ids': [
                4,
                1,
            ]
        }, {
            'name': 'Penicillin Antibiotic - Natural',
            'path_ids': [
                4,
                1,
                2,
            ]
        }, {
            'name': 'Aminopenicillin Antibiotic',
            'path_ids': [
                4,
                1,
                3,
            ]
        }]
        medications = [{
            'med_id': 150020,
            'path_ids': [4]
        }, {
            'med_id': 150100,
            'path_ids': [
                4,
                1,
                2,
            ]
        }, {
            'med_id': 150106,
            'path_ids': [
                4,
                1,
                2,
            ]
        }, {
            'med_id': 150113,
            'path_ids': [
                4,
                1,
                3,
            ]
        }]
        result = tested.generate_full_classes(classes, medications)
        expected = {
            4: {
                'name': 'Penicillin',
                'ids': [150020, 150100, 150106, 150113]
            },
            1: {
                'name': 'Penicillin Antibiotics',
                'ids': [150100, 150106, 150113]
            },
            2: {
                'name': 'Penicillin Antibiotic - Natural',
                'ids': [150100, 150106]
            },
            3: {
                'name': 'Aminopenicillin Antibiotic',
                'ids': [150113]
            },
        }
        self.assertEqual(len(expected), len(result))
        for key, value in expected.items():
            self.assertIn(key, result)
            self.assertEqual(value['name'], result[key]['name'])
            self.assertEqual(len(value['ids']), len(result[key]['ids']))
            for exp, res in zip(value['ids'], result[key]['ids']):
                self.assertEqual(exp, res)

    def test_add_line(self):
        tested = BuildMedicationClassPathValueSet('')

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.add_line(0, 'this is a line')
        result = in_memory.getvalue()
        expected = 'this is a line\n'
        self.assertEqual(expected, result)
        in_memory.close()

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.add_line(2, 'this is a line')
        result = in_memory.getvalue()
        expected = '        this is a line\n'
        self.assertEqual(expected, result)
        in_memory.close()

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.add_line(3, 'this is a line')
        result = in_memory.getvalue()
        expected = '            this is a line\n'
        self.assertEqual(expected, result)
        in_memory.close()

    def test_get_indentation(self):
        tested = BuildMedicationClassPathValueSet('')
        result = tested.get_indentation(0)
        expected = ''
        self.assertEqual(expected, result)
        result = tested.get_indentation(2)
        expected = '        '
        self.assertEqual(expected, result)
        result = tested.get_indentation(1)
        expected = '    '
        self.assertEqual(expected, result)

    def test_class_name_from(self):
        tested = BuildMedicationClassPathValueSet('')
        tests = [
            ('abcd123', 'Abcd123'),
            ('123abcd', 'C123abcd'),
            ('ab-cd*123', 'AbCd123'),
            ('abc d1 23', 'AbcD123'),
        ]
        for title, expected in tests:
            result = tested.class_name_from(title)
            self.assertEqual(expected, result)

    def test_clean(self):
        tested = BuildMedicationClassPathValueSet('')
        tests = [
            ('abcdef', 'abcdef'),
            ('abc"def', 'abc"def'),
            ("abc'def", "abc\\'def"),
        ]
        for title, expected in tests:
            result = tested.clean(title)
            self.assertEqual(expected, result)

    def test_write_class_path(self):
        full_class = {
            'name': 'Top class of the drug',
            'ids': [
                1,
                4,
                56,
                89,
                632,
            ]
        }

        tested = BuildMedicationClassPathValueSet('')

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.write_class_path(full_class, '2018-10-13')
        result = in_memory.getvalue()
        expected = open(
            f'{settings.BASE_DIR}/protocols/tests/management/commands/medication_value_set_class.txt',
            'r').read()
        self.assertEqual(expected, result)
        in_memory.close()

    def test_run(self):
        classes = [{
            'name': 'Penicillin',
            'path_ids': [4]
        }, {
            'name': 'Penicillin Antibiotics',
            'path_ids': [
                4,
                1,
            ]
        }, {
            'name': 'Penicillin Antibiotic - Natural',
            'path_ids': [
                4,
                1,
                2,
            ]
        }, {
            'name': 'Aminopenicillin Antibiotic',
            'path_ids': [
                4,
                1,
                3,
            ]
        }]
        medications = [{
            'med_id': 150020,
            'path_ids': [4]
        }, {
            'med_id': 150100,
            'path_ids': [
                4,
                1,
                2,
            ]
        }, {
            'med_id': 150106,
            'path_ids': [
                4,
                1,
                2,
            ]
        }, {
            'med_id': 150113,
            'path_ids': [
                4,
                1,
                3,
            ]
        }]

        file_to = tempfile.NamedTemporaryFile()
        tested = BuildMedicationClassPathValueSet(file_to.name)

        tested.run(classes, medications)
        result = open(file_to.name, 'r').read()
        today = format(datetime.date.today().strftime('%y-%m-%d'))
        expected = open(
            f'{settings.BASE_DIR}/protocols/tests/management/commands/medication_value_set_file.txt',
            'r').read().replace('18-10-13', today)
        self.assertEqual(expected, result)
