from os import makedirs, path, listdir, getcwd, chdir, system
from werkzeug.utils import secure_filename
from re import findall
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
        # modulos opcionales
        if input('Do you want add personnel module 👉: ').strip().lower() == "y":
            add_optional("personnel", rootPath)
        if input('Do you want add brand module 👉: ').strip().lower() == "y":
            add_optional("brand", rootPath)
        create_virtual_env(napp, rootProject, rootPath)  # crea entorno e instala dependencias
        print("\n\nhappy coding 😎🤟\n\n")
    else:
        print("you need to specify the api name 🤬")


def __validate_module(rootProject: str):
    """
    Validaciones de existencia de modulo
    """
    CDIR = path.dirname(path.realpath(__file__))
    rootProject = rootProject or getcwd()
    rServerPath = path.join(rootProject, 'runServer.py')
    if path.exists(path.join(rootProject, 'modules')) is False or path.exists(rServerPath) is False:
        raise Exception(path.basename(rootProject) + " is not a valid project")
    return CDIR, rootProject, rServerPath


def __add_module_to_run(module: str, rServerPath: str, mCPath: str):
    """
    Agrega el modulo a runServer.py

    parameters:
        module(str): Nombre del modulo
        rServerPath(str): Direccion de ruta del archivo runServer.py
        mCPath(str): Direccion de la ruta del archivo controller.py
    """
    vmodule = None  # variable del modulo
    with open(mCPath, 'r') as fl:
        pattern = r'(\w+)\s{1,}(\=\s{1,}Blueprint\([\'\"].+[\'\"],\s{1,}__name__\))'
        for ln in fl.readlines():
            res = findall(pattern, ln)
            if len(res) > 0:
                vmodule = res[0][0]
                break
    if vmodule:
        lnmodule = "from modules.{0}.{0}_controller import {1}".format(module, vmodule)
        lnregistre = "app.register_blueprint(%s)" % vmodule
        # lectura del archivo runServer.py
        with open(rServerPath, 'r+') as fl:
            data = fl.read()  # lee todo el texto
            lines = data.splitlines()
            inmodule = lnmodule in data  # si existe la verificacion del modulo
            inregistre = lnregistre in data
            if inmodule is False or inregistre is False:
                index = -1
                flag = ""
                for ln in list(lines):
                    index += 1
                    if flag == 'module' and inmodule is False:
                        if ln.strip() == "":
                            flag = ""
                            lines.insert(index, lnmodule)
                            index += 1
                    elif flag == 'register' and inregistre is False:
                        if ln.strip() == "":
                            lines.insert(index, lnregistre)
                            break
                    elif flag == '':
                        if "from modules." in ln:
                            flag = 'module'
                        elif "app.register_blueprint(" in ln:
                            flag = 'register'
                fl.seek(0)
                lines.append("")  # agrega linea vacia
                fl.writelines("\n".join(lines))
    else:
        raise Exception("The module variable not found")


def add_optional(module: str, rootProject: str):
    """
    Agrega modulo existente
    """
    if module:
        CDIR, rootProject, rServerPath = __validate_module(rootProject)
        mPath = path.join(CDIR, 'optional', module)
        if path.exists(mPath) is False:
            raise Exception("Module %s is not available" % module)
        # copia el modulo
        print("🚩 adding module > " + module)
        shutil.copytree(mPath, path.join(rootProject, 'modules', module), symlinks=False, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        mCPath = path.join(mPath, module + "_controller.py")
        __add_module_to_run(module, rServerPath, mCPath)


def create_module(module: str):
    """
    Crea modulo
    """
    if module:
        module = module.strip().lower()
        CDIR, rootProject, rServerPath = __validate_module(None)
        mPath = path.join(rootProject, 'modules', module)
        mCPath = path.join(mPath, "%s_controller.py" % module)
        # crea directorio
        print("🚩 creating module > " + module)
        makedirs(mPath)
        # crea archivo controlador
        mDefaultPath = path.join(CDIR, "default")
        with open(path.join(mDefaultPath, "default_controller.py"), 'r') as ofl:
            data = ofl.read()
            data = data.replace('default', module)
            with open(mCPath, 'w') as fl:
                fl.write(data)
        docs = path.join(mPath, "docs")
        makedirs(docs)  # crea directorio de docs
        with open(path.join(mDefaultPath, "docs", "search.yml"), 'r') as ofl:
            data = ofl.read()
            data = data.replace('default', module)
            data = data.replace('Default', module[0].upper() + module[1:].lower())
            with open(path.join(docs, 'search.yml'), 'w') as fl:
                fl.write(data)
        __add_module_to_run(module, rServerPath, mCPath)
