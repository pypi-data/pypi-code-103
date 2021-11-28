from os import makedirs, path, listdir, getcwd, chdir, system
from werkzeug.utils import secure_filename
import platform
import shutil
import subprocess


def create_file(sfilepath: str, dfilepath: str, props: dict):
    """Lee archivo original, reemplaza las variables y crea archivo de salida"""
    with open(sfilepath, "r", encoding="utf-8") as fl:
        data = fl.read()
        for prop, value in props.items():
            data = data.replace(prop, value)
    with open(dfilepath, "w", encoding="utf-8") as fl:
        fl.write(data)


def create_virtual_env(name: str, rootProject: str, rootApi: str):
    """
    Crea entorno virtual e instala las dependencias
    """
    chdir(rootProject)  # mueve a carpeta del proyecto
    upp = input('pip upgrade (Y/N) 👉: ').strip().lower() == 'y'
    if platform.system() == 'Windows':
        exe_cmd = "python -m venv {0}-venv & {1}/{0}-venv/Scripts/activate".format(name, rootProject)
        if upp is True:
            subprocess.run("{0} & pip install --upgrade pip & pip install -r {1}/requirements.txt".format(exe_cmd, rootApi), shell=True)
        else:
            subprocess.run("{0} & pip install -r {1}/requirements.txt".format(exe_cmd, rootApi), shell=True)
    else:
        exe_cmd = "python3 -m venv {0}-venv; source ./{0}-venv/bin/activate;".format(name)
        if upp is True:
            system(exe_cmd + "pip install --upgrade pip; pip install -r {1}/requirements.txt".format(exe_cmd, rootApi))
        else:
            system(exe_cmd + "pip install -r {1}/requirements.txt".format(exe_cmd, rootApi))


def delete_app(napp: str):
    """
    Elimina el directorio
    """
    if napp:
        napp = secure_filename(napp).lower().replace('-api', '') + '-project'
        if input('💩 Are you sure you want to delete the %s (Y/N): ' % napp).lower() == 'y':
            shutil.rmtree(napp)
    else:
        print("you need to specify the api name 🤬")


def create_app(napp: str):
    """
    Crea app
    """
    if napp:
        CDIR = path.dirname(path.realpath(__file__))
        acode = input('app code 👉: ').strip()
        port = input('app port 👉: ').strip() or '5000'
        napp = secure_filename(napp).lower().replace('-api', '')
        rootProject = path.join(getcwd(), napp + '-project')  # carpeta de proyecto
        rootPath = path.join(rootProject, napp + '-api')  # carpeta del api
        # crea carpetas
        for dname in ('', 'resources', '__temp__'):
            print("🚩 creating > " + (dname or rootPath))
            makedirs(path.join(rootPath, dname))
        DRESOURCES = path.join(CDIR, 'resources')
        for name in listdir(DRESOURCES):
            if name != '__pycache__':
                print("🚩 creating > " + name)
                npath = path.join(DRESOURCES, name)
                if path.isdir(npath):  # si es directorio lo copia todo
                    shutil.copytree(npath, path.join(rootPath, name), symlinks=False, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                else:  # si es un archivo
                    if name == 'const.py':
                        create_file(npath, path.join(rootPath, name), {'<<APPLICATION_CODE>>': acode, '<<PORT>>': port})
                    elif name == 'app.py':
                        create_file(npath, path.join(rootPath, name), {'<<API_NAME>>': napp})
                    elif name == 'runServer.py':
                        create_file(npath, path.join(rootPath, name), {'<<API_NAME>>': napp})
                    elif name.endswith('.pyc') is False:
                        shutil.copyfile(npath, path.join(rootPath, name))
        create_virtual_env(napp, rootProject, rootPath)  # crea entorno e instala dependencias
        print("\n\nhappy coding 😎🤟\n\n")
    else:
        print("you need to specify the api name 🤬")
