from pdx import Console
from pdx import Session
from pdx import CodeBlock

import unittest
import os
import inspect

# Always run in debug mode
Session.debug_mode = True

out = Console.get()


class TestCodeBlock(unittest.TestCase):
    """
    Test CodeBlock Features
    """
    # Root directory of pdx-lib package
    pdx_code = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    # Unit test working directory
    unit_test_sandbox = os.path.join(Session.pdx_home, 'unit-test')

    def test_removing_sql_comments(self):
        """Test removing comments from a block of SQL text"""
        text = """
                    /** Here is some sloppy SQL **/
                    -- Written by Mike

            SELECT 'x' FROM dual;

            --SELECT 'y' FROM dual dual;
                    SELECT --rather than delete
                    'x', 'it''s -- True!', 'z', 5, --null,
                    100


                    FROM dual

                    WHERE test - 5 = -1; --This never happens!
                    /** END TEST TEXT **/
                    """
        expected = """
                    
                    

            SELECT 'x' FROM dual;

            
                    SELECT 
                    'x', 'it''s -- True!', 'z', 5, 
                    100


                    FROM dual

                    WHERE test - 5 = -1; 
                    
                    """

        code = CodeBlock.CodeBlock(text, 'sql')
        result = code.get_without_comments()

        out.put_color("'{0}'".format(expected), 'green')
        out.put_color("'{0}'".format(result), 'red')
        self.assertTrue(result == expected, "SQL comment removal failed")

    def test_removing_all_comments(self):
        """Test removing comments from a block of Groovy/Java text"""
        text = """/*testing...
*/this is /** just **/
a '//sample' /**
that can be used **/
for /* unit */ testing//.
        """
        expected = """this is 
a '//sample' 
for  testing
        """

        code = CodeBlock.CodeBlock(text, 'groovy')
        result = code.get_without_comments()

        out.put_color("'{0}'".format(expected), 'green')
        out.put_color("'{0}'".format(result), 'red')
        self.assertTrue(result == expected, "Groovy comment removal failed")


if __name__ == '__main__':
    unittest.main()
