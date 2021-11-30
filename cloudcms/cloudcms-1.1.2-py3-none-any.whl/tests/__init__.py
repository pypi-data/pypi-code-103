import unittest
from .test_platform import TestPlatform
from .test_repository import TestRepository
from .test_branch import TestBranch
from .test_node import TestNode
from .test_association import TestAssociation
from .test_attachment import TestAttachment
from .test_file_folder import TestFileFolder
from .test_project import TestProject
from .test_release import TestRelease

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPlatform)
    suite.addTest(TestRepository)
    suite.addTest(TestBranch)
    suite.addTest(TestNode)
    suite.addTest(TestAssociation)
    suite.addTest(TestAttachment)
    suite.addTest(TestFileFolder)
    suite.addTest(TestProject)
    suite.addTest(TestRelease)

    return suite

if __name__ == "__main__":
    suite = create_suite()
    runner = unittest.TextTestRunner()

    runner.run(suite)