import io

from contextlib import redirect_stdout

from unittest import TestCase

from canvas_workflow_kit.management.commands.protocols_dependencies import Command


class TestCommand(TestCase):
    maxDiff = None

    def test_handle(self):
        out = io.StringIO()

        with redirect_stdout(out):
            Command().handle()

        captured = out.getvalue()

        # flake8: noqa
        expected = [
            '----------------------------------------------------------------------------------------------------',
            '| Data                 | Protocol                       | Description                              |',
            '----------------------------------------------------------------------------------------------------',
            '| billing_line_item    | ClinicalQualityMeasure138v6    | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p1  | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p2  | Preventive Care and Screening: Tobacc... |',
            '|                      | Hcc005v1                       | Annual Wellness Visit                    |',
            '----------------------------------------------------------------------------------------------------',
            '| condition            | Ccp002v1                       | COVID-19 High Risk Outreach              |',
            '|                      | Ccp003v1                       | Diagnosis Of Hypertension                |',
            '|                      | Ccp004v1                       | Diagnosis Of Diabetes                    |',
            '|                      | Ccp005v1                       | Diagnosis Of Asthma                      |',
            '|                      | ClinicalQualityMeasure122v6    | Diabetes: Hemoglobin HbA1c Poor Contr... |',
            '|                      | ClinicalQualityMeasure123v6    | Diabetes: Foot Exam                      |',
            '|                      | ClinicalQualityMeasure125v6    | Breast Cancer Screening                  |',
            '|                      | ClinicalQualityMeasure130v6    | Colorectal Cancer Screening              |',
            '|                      | ClinicalQualityMeasure131v6    | Diabetes: Eye Exam                       |',
            '|                      | ClinicalQualityMeasure134v6    | Diabetes: Medical Attention for Nephr... |',
            '|                      | Hcc001v1                       | Problem List Hygiene                     |',
            '|                      | Hcc002v2                       | CKD suspect                              |',
            '|                      | Hcc003v1                       | Diabetes Mellitus With Secondary Comp... |',
            '|                      | Hcc004v1                       | Dysrhythmia Suspects                     |',
            '----------------------------------------------------------------------------------------------------',
            '| imaging_report       | ClinicalQualityMeasure125v6    | Breast Cancer Screening                  |',
            '|                      | ClinicalQualityMeasure130v6    | Colorectal Cancer Screening              |',
            '----------------------------------------------------------------------------------------------------',
            '| instruction          | ClinicalQualityMeasure134v6    | Diabetes: Medical Attention for Nephr... |',
            '|                      | ClinicalQualityMeasure138v6    | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p2  | Preventive Care and Screening: Tobacc... |',
            '----------------------------------------------------------------------------------------------------',
            '| interview            | Ccp001v1                       | COVID-19 Risk Assessment Follow Up       |',
            '|                      | Ccp002v1                       | COVID-19 High Risk Outreach              |',
            '|                      | ClinicalQualityMeasure123v6    | Diabetes: Foot Exam                      |',
            '|                      | ClinicalQualityMeasure138v6    | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p1  | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p2  | Preventive Care and Screening: Tobacc... |',
            '----------------------------------------------------------------------------------------------------',
            '| lab_report           | ClinicalQualityMeasure122v6    | Diabetes: Hemoglobin HbA1c Poor Contr... |',
            '|                      | ClinicalQualityMeasure130v6    | Colorectal Cancer Screening              |',
            '|                      | ClinicalQualityMeasure134v6    | Diabetes: Medical Attention for Nephr... |',
            '|                      | Hcc002v2                       | CKD suspect                              |',
            '----------------------------------------------------------------------------------------------------',
            '| medication           | ClinicalQualityMeasure134v6    | Diabetes: Medical Attention for Nephr... |',
            '|                      | ClinicalQualityMeasure138v6    | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p2  | Preventive Care and Screening: Tobacc... |',
            '|                      | Hcc004v1                       | Dysrhythmia Suspects                     |',
            '----------------------------------------------------------------------------------------------------',
            '| patient              | Ccp002v1                       | COVID-19 High Risk Outreach              |',
            '|                      | ClinicalQualityMeasure122v6    | Diabetes: Hemoglobin HbA1c Poor Contr... |',
            '|                      | ClinicalQualityMeasure123v6    | Diabetes: Foot Exam                      |',
            '|                      | ClinicalQualityMeasure125v6    | Breast Cancer Screening                  |',
            '|                      | ClinicalQualityMeasure130v6    | Colorectal Cancer Screening              |',
            '|                      | ClinicalQualityMeasure131v6    | Diabetes: Eye Exam                       |',
            '|                      | ClinicalQualityMeasure134v6    | Diabetes: Medical Attention for Nephr... |',
            '|                      | ClinicalQualityMeasure138v6    | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p1  | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p2  | Preventive Care and Screening: Tobacc... |',
            '|                      | Hcc002v2                       | CKD suspect                              |',
            '|                      | Hcc005v1                       | Annual Wellness Visit                    |',
            '----------------------------------------------------------------------------------------------------',
            '| protocol_override    | ClinicalQualityMeasure122v6    | Diabetes: Hemoglobin HbA1c Poor Contr... |',
            '|                      | ClinicalQualityMeasure123v6    | Diabetes: Foot Exam                      |',
            '|                      | ClinicalQualityMeasure125v6    | Breast Cancer Screening                  |',
            '|                      | ClinicalQualityMeasure130v6    | Colorectal Cancer Screening              |',
            '|                      | ClinicalQualityMeasure131v6    | Diabetes: Eye Exam                       |',
            '|                      | ClinicalQualityMeasure134v6    | Diabetes: Medical Attention for Nephr... |',
            '|                      | ClinicalQualityMeasure138v6    | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p1  | Preventive Care and Screening: Tobacc... |',
            '|                      | ClinicalQualityMeasure138v6p2  | Preventive Care and Screening: Tobacc... |',
            '|                      | Hcc001v1                       | Problem List Hygiene                     |',
            '|                      | Hcc002v2                       | CKD suspect                              |',
            '|                      | Hcc003v1                       | Diabetes Mellitus With Secondary Comp... |',
            '|                      | Hcc004v1                       | Dysrhythmia Suspects                     |',
            '|                      | Hcc005v1                       | Annual Wellness Visit                    |',
            '----------------------------------------------------------------------------------------------------',
            '| referral_report      | ClinicalQualityMeasure130v6    | Colorectal Cancer Screening              |',
            '|                      | ClinicalQualityMeasure131v6    | Diabetes: Eye Exam                       |',
            '|                      | ClinicalQualityMeasure134v6    | Diabetes: Medical Attention for Nephr... |',
            '----------------------------------------------------------------------------------------------------',
        ]
        self.assertEqual('\n'.join(expected), captured.strip())

    def test_print_line(self):
        tested = Command()

        out = io.StringIO()
        with redirect_stdout(out):
            tested.print_line()
        captured = out.getvalue()

        # flake8: noqa
        expected = [
            '----------------------------------------------------------------------------------------------------',
        ]
        self.assertEqual('\n'.join(expected), captured.strip())

    def test_print_table_titles(self):
        tested = Command()

        out = io.StringIO()
        with redirect_stdout(out):
            tested.print_table_titles()
        captured = out.getvalue().strip()

        # flake8: noqa
        expected = [
            '----------------------------------------------------------------------------------------------------',
            '| Data                 | Protocol                       | Description                              |',
            '----------------------------------------------------------------------------------------------------',
        ]
        self.assertEqual('\n'.join(expected), captured)

    def test_print_table_row(self):
        tested = Command()

        out = io.StringIO()
        with redirect_stdout(out):
            tested.print_table_row('type', 'key', 'description')
        captured = out.getvalue().strip()

        # flake8: noqa
        expected = [
            '| type                 | key                            | description                              |',
        ]
        self.assertEqual('\n'.join(expected), captured)
