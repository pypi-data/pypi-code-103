import sys
import traceback
import os
import pathlib

from django.http import HttpResponseServerError


def make_pretty_tb(tb):
    output = "Traceback is:\n"
    for (file, linenumber, affected, line) in tb:
        got_path = pathlib.PurePath(file)
        if "site-packages" in got_path.parts:
            i = got_path.parts.index("site-packages")
            new_color = "\033[0;35m"
            new_path = os.path.join(*got_path.parts[i + 1 :])
        elif "apps" in got_path.parts:
            i = got_path.parts.index("apps")
            new_path = os.path.join(*got_path.parts[i:])
            new_color = f"\033[0;31m"
        else:
            new_color = ""
            new_path = f'"{got_path}"'

        output += f"{new_color}{new_path} - {linenumber} >\033[0m {affected} {new_color}>\033[0m {line}\n"
    return output


def make_pretty_exc(trace2):
    tb = traceback.extract_tb(sys.exc_info()[2])
    output = f"Error in the server: {trace2}.\n"
    output += make_pretty_tb(tb)
    output += f"\t> Exception: {trace2}\n"
    return output


class PrettyTBMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        print(make_pretty_exc(exception), file=sys.stderr)
        return HttpResponseServerError()
