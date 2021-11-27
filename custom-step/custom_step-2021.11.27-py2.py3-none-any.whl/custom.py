# -*- coding: utf-8 -*-

"""Non-graphical part of the Custom step in a SEAMM flowchart"""

import logging
import os

import custom_step
import seamm
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter('Custom')


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class Custom(seamm.Node):

    def __init__(
        self,
        flowchart=None,
        title='Custom Python',
        extension=None,
        logger=logger
    ):
        """A step for custom python in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug('Creating Custom {}'.format(self))

        super().__init__(
            flowchart=flowchart,
            title=title,
            extension=extension,
            logger=logger
        )

        self.parameters = custom_step.CustomParameters()

    @property
    def version(self):
        """The semantic version of this module.
        """
        return custom_step.__version__

    @property
    def git_revision(self):
        """The git version of this module.
        """
        return custom_step.__git_revision__

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
        P: dict
            An optional dictionary of the current values of the control
            parameters.

        Returns
        -------
        str
            A description of the current step.
        """
        if not P:
            P = self.parameters.values_to_dict()

        script = P['script'].splitlines()

        if len(script) > 10:
            text = '\n'.join(script[0:9])
            text += '\n...'
        else:
            text = '\n'.join(script)

        return (
            self.header + '\n' + __(text, indent=4 * ' ', wrap=False).__str__()
        )

    def run(self):
        """Run a Custom step.
        """
        next_node = super().run(printer)

        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Print what we are doing -- getting formatted values for printing
        printer.normal(self.header)

        # Override simple print statements
        script = (
            "import builtins\n"
            "import seamm_util.printing as printing\n"
            "job = printing.getPrinter()\n"
            "original_print = print\n"
            "\n"
            "def new_print(*objects, sep=' ', **kwargs):\n"
            "    if len(kwargs) > 0:\n"
            "        builtins.print(*objects, sep=sep, **kwargs)\n"
            "    else:\n"
            "        job.job(sep.join(objects))\n"
            "print = new_print\n"
        )
        script += P['script']

        # And do it!
        os.makedirs(self.directory, exist_ok=True)
        try:
            with cd(self.directory):
                exec(script, seamm.flowchart_variables._data)
        except Exception as e:
            printer.normal(f"\n    ***{e.__class__.__name__}*** {str(e)}")
            raise
        else:
            printer.normal('    --- end of script ---')
            printer.normal('')

        return next_node
