"""
Compiling tex files and processing bibliography (bib) files.
"""

import subprocess
import sys

import latex_suite.util


class Outcome:
    """
    The outcome of compiling or processing latex and related files.
    """

    UNKNOWN = -1
    SUCCESS = 0
    FAILURE = 1
    ABORTED = 2
    FILE_NOT_FOUND = 3


class ProcessRunnerWithOutput:
    """
    Class to run a cmd line program on a positional parameter (e.g. a file) and collect the output.
    """

    def __init__(self, command, parameter, verbose=False):
        self._command = command
        self._parameter = str(parameter)
        self._verbose = verbose
        self._process = subprocess.Popen(self._command + " " + self._parameter, shell=True,
                                         stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self._total_output = ""

    @property
    def output(self):
        """
        :return:
        The output written to stdout by the pdf compiler engine.
        """
        return self._total_output

    @property
    def command(self):
        """
        The command/process.
        :return: str
            The command/process.
        """
        return self._command

    @property
    def parameter(self):
        """
        The parameter of the command/process.
        :return:
            The parameter of the command/process.
        """
        return self._parameter

    def write_to_stdin(self, input_bytes):
        """
        Write bytes to sdtin.
        :param input_bytes: bytes
            The input to write.
        """
        self._process.stdin.write(input_bytes)
        self._process.stdin.flush()

    def write_newline(self):
        """
        Write newline to stdin.
        """
        self.write_to_stdin(b'\n')

    def __iter__(self):
        """
        :return:
        An iterator over the bytes of the stdout from the compiler.
        """
        self._stdout_iterator = iter(lambda: self._process.stdout.read(1), b'')
        return self

    def __next__(self):
        """
        Get the next char from stdout until the process the finished or stdin gets closed.
        The char is also added to the entire output (see :func:`~LatexBashCompile.output`).

        :return: str
            The next char.
        """
        if self._process.stdin.closed:
            raise StopIteration
        byte_char = next(self._stdout_iterator)
        char = byte_char.decode("utf-8")
        self._total_output += char
        if self._verbose:
            sys.stdout.write(char)
        return char


class BibBashProcessing(ProcessRunnerWithOutput):
    """
    Process citations of a latex document.
    """

    def __init__(self, engine, tex_file, verbose=False):
        super().__init__(engine, BibBashProcessing.get_bib_parameter(engine, tex_file), verbose)
        self._verbose = verbose

    @staticmethod
    def get_bib_parameter(engine, tex_file):
        """
        Return the parameter of the bib engine to process citations.

        :param engine: str
            The engine.
        :param tex_file: str
            The name of the text file.
        :return: str
            The parameter for the bib engine.
        """
        bib_filename = None
        if engine == "biber":
            bib_filename = latex_suite.util.filename_stem(tex_file)
        elif engine == "bibtex":
            bib_filename = latex_suite.util.filename_stem(tex_file) + ".aux"
        return bib_filename

    def run_processing(self):
        """
        Process the citations.
        :return: int
            The outcome indicator.
        """
        compile_outcome = Outcome.SUCCESS
        for _ in iter(self):
            pass
        if self._verbose:
            sys.stdout.write("\n")
        sys.stdout.flush()
        if "I couldn't open file name" in self._total_output:
            compile_outcome = Outcome.FILE_NOT_FOUND
        if "I found no \\bibstyle command" in self._total_output:
            compile_outcome = Outcome.FAILURE
        return compile_outcome


class LatexBashCompile(ProcessRunnerWithOutput):
    """
    Class to use bash tex compile tools to translate pdfs.
    """

    def __init__(self, engine, file, max_end_attempts, verbose=False):
        """
        Constructor

        :param engine:
            The pdf compiler engine.
        :param file:
            The tex file to translate.
        :param max_end_attempts:
            The maximal number of attempts to progress past a compile error.
        """

        super().__init__(engine, file, verbose)
        self._max_end_attempts = max_end_attempts
        self._verbose = verbose
        self._warning_progressions = 0
        self._error_progressions = 0

    @property
    def num_warnings(self):
        """
        :return: int
        The number of question mark warnings during the pdf compile process.
        """
        return self._warning_progressions

    @property
    def num_errors(self):
        """
        :return: int
        The number of asterisk errors during the pdf compile process.
        """
        return self._error_progressions

    def write_end_enter(self):
        """
        Passes \\end and newline to stdin for passing past a latex error that requires entering an
        \\end command.
        """
        self.write_to_stdin(b'\\end\n')

    def run_compile(self):
        """
        Compile the tex file with the specified engine.

        :return: LatexBashCompileResult
        The compile result with the outcome, output and number of errors and warnings.
        """
        compile_outcome = Outcome.SUCCESS
        end_attempts = 0
        start_of_new_line = True
        potential_file_not_found_idx = 0
        for char in iter(self):
            if start_of_new_line:
                if char == "?":
                    self.write_newline()
                    self._warning_progressions += 1
                elif char == "!":
                    potential_file_not_found_idx = 1
                elif char == "*":
                    if end_attempts >= self._max_end_attempts:
                        self._process.stdin.close()
                        compile_outcome = Outcome.ABORTED
                    else:
                        self.write_end_enter()
                        end_attempts += 1
                        self._error_progressions += 1
            elif potential_file_not_found_idx > 0:
                fnf_message = "! I can't find file"
                if char == fnf_message[potential_file_not_found_idx]:
                    potential_file_not_found_idx += 1
                else:
                    potential_file_not_found_idx = 0
                if potential_file_not_found_idx == len(fnf_message):
                    self._process.stdin.close()
                    compile_outcome = Outcome.FILE_NOT_FOUND
            start_of_new_line = False
            if char == "\n":
                start_of_new_line = True
        if self._verbose:
            sys.stdout.write("\n")
        sys.stdout.flush()
        if (compile_outcome != Outcome.ABORTED
                and "Fatal error occurred, no output PDF file produced!" in self._total_output):
            compile_outcome = Outcome.FAILURE
        return compile_outcome


class LatexBashCompileResult:
    """
    The results of a tex compilation.
    """

    def __init__(self, filename, outcome, output, num_warnings, num_errors):
        self.filename = filename
        self.outcome = outcome
        self.output = output
        self.num_warnings = num_warnings
        self.num_errors = num_errors
        self._bib_processing_result = None

    @property
    def bib_processing_result(self):
        """
        :return:
        BibBashProcessingResult
            The result of a bib processing.
        """
        return self._bib_processing_result

    @bib_processing_result.setter
    def bib_processing_result(self, result):
        """
        Set the result of a bib processing.
        :param result: BibBashProcessingResult
            The result.
        """
        self._bib_processing_result = result


class BibBashProcessingResult:
    """
    The results of a bib processing.
    """

    def __init__(self, filename, outcome, output):
        self.filename = filename
        self.outcome = outcome
        self.output = output


def make_pdf(file_to_translate, engine, bib_engine, max_end_attempts=1,
             verbose=False, do_bib=False, do_single_run=False):
    """
    Compile a tex file to a pdf.

    Performs one or several steps of the translation of a tex file to a pdf file.
    This can include single and several compilation runs as well as citation processing.
    The minimal run is one translation of the tex file (do_bib=False, do_single_run=True) and the maximal
    run is: tex translation, bib processing, tex translation, tex translation (do_bib=True, do_single_run=False).

    :param file_to_translate:
        The path of the tex file.
    :param engine: str
        The engine to use to translate the tex file.
    :param bib_engine: str
        The engine to use to process the citations.
    :param max_end_attempts: int
        The maximal number of attempts to try to pass past a latex translation error.
    :param verbose: bool
        If True print processing.
    :param do_bib: bool
        If True processes the citations with the citation engine.
    :param do_single_run:
        If True and do_bib is False one translation of the tex file.
        If True and do_bib is True: tex translation, citation processing, tex translation.
    :return: LatexBashCompileResult
        The compile result of the last compile with the outcome, output and number of errors and warnings.
        If the bibliography was processed the bib processing information is included.
    """
    compile_result = None
    bib_process_result = None
    if do_bib and not do_single_run or not do_bib and do_single_run or not do_bib and not do_single_run:
        compile_result = compile_file(engine, file_to_translate, max_end_attempts=max_end_attempts, verbose=verbose)
    if do_bib:
        bib_process_result = compile_bib(bib_engine, file_to_translate, verbose=verbose)
    if do_bib and not do_single_run:
        compile_result = compile_file(engine, file_to_translate, max_end_attempts=max_end_attempts, verbose=verbose)
    if not do_single_run:
        compile_result = compile_file(engine, file_to_translate, max_end_attempts=max_end_attempts, verbose=verbose)
    compile_result.bib_processing_result = bib_process_result
    return compile_result


def compile_bib(engine, bib_parameter, verbose=False):
    """
    Process citations.

    :param engine: str
        The engine to use to process the citations.
    :param bib_parameter: str
        The parameter for the bib engine to process the citations. This could be a file name or a file name without
        the file extension.
    :param verbose: bool
         If True print processing.
    :return: BibBashProcessingResult
        The result of the citation processing.
    """
    processor = BibBashProcessing(engine, bib_parameter, verbose)
    outcome = processor.run_processing()
    return BibBashProcessingResult(BibBashProcessing.get_bib_parameter(processor.command, processor.parameter),
                                   outcome, processor.output)


def compile_file(engine, file, max_end_attempts=1, verbose=False):
    """
    Compiles a tex file with the specified engine.

    :param engine:
        The pdf compiler engine.
    :param file:
        The tex file to translate.
    :param max_end_attempts:
        The maximal number of attempts to progress past a compile error.
    :param verbose: bool
        If true prints engines output.
    :return: LatexBashCompileResult
        The compile result with the outcome, output and number of errors and warnings.
    """
    compiler = LatexBashCompile(engine, file, max_end_attempts, verbose)
    outcome = compiler.run_compile()
    return LatexBashCompileResult(file, outcome, compiler.output, compiler.num_warnings, compiler.num_errors)


def get_warnings(engine, file):
    """
    Get all warnings of a tex translation.

    :param engine:
        The pdf compiler engine.
    :param file:
        The tex file to translate.
    :return: list
        All warnings that occurred during the compilation.
    """
    compile_file(engine, file)
    compile_result = compile_file(engine, file)
    warnings = []
    warning_indicators = ["multiply defined", "overfull", "undefined", "Warning: Reference", "Warning:"]
    for one_line in compile_result.output.split("\n"):
        if any(indicator in one_line for indicator in warning_indicators):
            warnings.append(one_line)
    return warnings
