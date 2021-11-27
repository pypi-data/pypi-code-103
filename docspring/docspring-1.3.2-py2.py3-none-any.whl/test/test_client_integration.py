# coding: utf-8
# Note - this file is just used to generate a scaffold for the tests
# We overwrite it with test_pdf_api.py

"""
    API V1

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    OpenAPI spec version: v1
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import mock
import time

import docspring
# from docspring.api.pdf_api import PDFApi  # noqa: E501
from docspring.rest import ApiException
from pprint import pprint

class TestClient(unittest.TestCase):
    """Client unit tests"""

    def setUp(self):
        # Configure HTTP basic authorization: api_token_basic
        configuration = docspring.Configuration()
        configuration.api_token_id = 'api_token123'
        configuration.api_token_secret = 'testsecret123'
        configuration.host = 'api.docspring.local:31337/api/v1'

        # create an instance of the API class
        self.client = docspring.Client(docspring.ApiClient(configuration))

    def tearDown(self):
        pass

    def test_generate_pdf(self):
        """Test case for generate_pdf

        Generates PDFs
        """
        with mock.patch.object(docspring.Client, 'wait') as wait_patched:
          template_id = 'tpl_000000000000000001'  # str |

          response = self.client.generate_pdf(
              template_id, {
                  'data': {
                      'title': 'Test PDF',
                      'description': 'This PDF is great!'
                  },
                  'field_overrides': {
                    'title': {
                      'required': False
                    }
                  }
              })
          wait_patched.assert_called()
          self.assertEquals(response.status, 'success')
          submission = response.submission
          self.assertRegexpMatches(submission.id, '^sub_')
          self.assertEquals(submission.expired, False)
          self.assertEquals(submission.state, 'processed')


    def test_generate_pdf_with_error(self):
        """Test case for generate_pdf with error

        Generates PDFs
        """
        with mock.patch.object(docspring.Client, 'wait') as wait_patched:
            with self.assertRaises(ApiException) as context:
                template_id = 'tpl_000000000000000001'  # str |
                self.client.generate_pdf(
                    template_id, {
                        'data': {
                            'title': 'Test PDF',
                        }
                    })
            wait_patched.assert_not_called()
            self.assertEquals(context.exception.data['status'], 'error')
            self.assertEquals(context.exception.data['errors'], [
                "Your submission data did not contain a required property of 'description'"
            ])

    def test_batch_generate_pdfs(self):
        """Test case for batch_generate_pdfs

        Batch Generates PDFs
        """
        with mock.patch.object(docspring.Client, 'wait') as wait_patched:
            template_id = 'tpl_000000000000000001'  # str |

            response = self.client.batch_generate_pdfs({
                'template_id': template_id,
                'metadata': { 'user_id': 123 },
                'test': True,
                'submissions': [
                    {
                        'data': {
                            'title': 'Test PDF',
                            'description': 'This PDF is great!',
                        }
                    },
                    {
                        'data': {
                            'title': 'Test PDF 2',
                            'description': 'This PDF is also great!',
                        }
                    }
                ]}, wait=True)
            wait_patched.assert_called()

            self.assertEquals(response.status, 'success')
            batch = response.submission_batch
            self.assertRegexpMatches(batch.id, '^sbb_')
            self.assertEquals(batch.state, 'processed')
            self.assertEquals(batch.metadata['user_id'], 123)
            self.assertEquals(batch.total_count, 2)
            self.assertEquals(batch.pending_count, 0)
            self.assertEquals(batch.error_count, 0)
            self.assertEquals(batch.completion_percentage, 100)

            submissions = response.submissions
            self.assertEquals(len(submissions), 2)
            first_response = submissions[0]
            self.assertEquals(first_response.status, 'success')
            submission = first_response.submission
            self.assertRegexpMatches(submission.id, '^sub_')
            self.assertEquals(submission.expired, False)
            self.assertEquals(submission.state, 'processed')


    def test_combine_submissions(self):
        """Test case for combine_submissions

        Merge generated PDFs together  # noqa: E501
        """
        with mock.patch.object(time, "sleep") as wait_patched:
            response = self.client.combine_submissions({
                'submission_ids': ['sub_000000000000000001', 'sub_000000000000000002']
            }, wait=True)
            wait_patched.assert_called()
            self.assertEquals(response.status, 'success')
            combined_submission = response.combined_submission
            self.assertRegexpMatches(combined_submission.id, '^com_')
            self.assertEquals(combined_submission.expired, False)
            self.assertEquals(len(combined_submission.submission_ids), 2)
            self.assertEquals(combined_submission.state, 'processed')

    def test_batch_generate_and_combine_pdfs(self):
        """Test case for batch_generate_and_combine_pdfs

        Batch generate and merge PDFs together  # noqa: E501
        """
        with mock.patch.object(time, "sleep") as wait_patched:
            template_id = 'tpl_000000000000000001'  # str |
            response = self.client.batch_generate_and_combine_pdfs({
                'template_id': template_id,
                'metadata': {'user_id': 123},
                'test': True,
                'submissions': [
                    {
                        'data': {
                            'title': 'Test PDF',
                            'description': 'This PDF is great!',
                        }
                    },
                    {
                        'data': {
                            'title': 'Test PDF 2',
                            'description': 'This PDF is also great!',
                        }
                    }
                ]}, wait=True)

            wait_patched.assert_called()
            combined_submission = response.combined_submission
            self.assertRegexpMatches(combined_submission.id, '^com_')
            self.assertEquals(combined_submission.expired, False)
            self.assertEquals(len(combined_submission.submission_ids), 2)
            self.assertEquals(combined_submission.state, 'processed')


if __name__ == '__main__':
    unittest.main()
