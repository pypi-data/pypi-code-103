import subprocess as sp
from . import General as Gen

rar_exe_path = f'{Gen.file_path(__file__)}/bin/Rar.exe'


# dd

def list_content(rar_path: str):
    rar = sp.Popen([rar_exe_path, '-ep', 'lb', rar_path],
                   stdin=sp.PIPE,
                   stdout=sp.PIPE,
                   stderr=sp.PIPE)
    result = rar.communicate()[0].decode()
    return result.splitlines()


def add_to(rar_path: str, in_file: str, data: bytes):
    rar = sp.Popen([rar_exe_path, '-rr3', '-m0', f'-si{in_file}', 'a', rar_path],
                   stdin=sp.PIPE,
                   stdout=sp.PIPE,
                   stderr=sp.PIPE)
    result = rar.communicate(input=data)[0].decode()
    return result
