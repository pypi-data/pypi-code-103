
import os
import uuid
import shlex
import tempfile
import subprocess

kadmin_cmd = os.environ.get("KADMIN_CMD", "kadmin.local")
kinit_cmd = os.environ.get("KINIT_CMD", "kinit")
encodings = ["utf-8", "gb18030"]

def set_kinit_command(path):
    global kinit_cmd
    kinit_cmd = shlex.quote(path)

def set_kadmin_command(path):
    global kadmin_cmd
    kadmin_cmd = shlex.quote(path)

def decode_output(output):
    for encoding in encodings:
        try:
            return output.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError("BYTES decode to STR failed with {0} encodings...".format(encodings))

def run(cmd):
    proc = subprocess.Popen(
        cmd,
        universal_newlines = True,
        shell = True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr

def list_principals():
    cmd = "{} -q list_principals".format(kadmin_cmd)
    returncode, stdout, stderr = run(cmd)
    return stdout.splitlines()[1:]

def add_principal(principal, password=None):
    cmd = "{} add_principal".format(kadmin_cmd)
    if password:
        cmd += " -pw {}".format(shlex.quote(password))
    else:
        cmd += " -randkey"
    cmd += " {}".format(shlex.quote(principal))
    returncode, stdout, stderr = run(cmd)
    return returncode, stdout, stderr

def delete_principal(principal):
    cmd = "{} delete_principal {}".format(kadmin_cmd, shlex.quote(principal))
    returncode, stdout, stderr = run(cmd)
    return returncode, stdout, stderr

def change_password(principal, password=None):
    cmd = "{} change_password".format(kadmin_cmd)
    if password:
        cmd += " -pw {}".format(shlex.quote(password))
    else:
        cmd += " -randkey"
    cmd += " {}".format(shlex.quote(principal))
    returncode, stdout, stderr = run(cmd)
    return returncode, stdout, stderr

def get_principal(principal):
    cmd = "{} get_principal {}".format(kadmin_cmd, shlex.quote(principal))
    returncode, stdout, stderr = run(cmd)
    if returncode == 0:
        info = {}
        for line in stdout.splitlines():
            key, value = line.split(":", maxsplit=1)
            info[key] = value
        return info
    else:
        raise RuntimeError(stderr)

def rename_principal(old_principal, new_principal):
    cmd = "{} rename_principal -force {} {}".format(kadmin_cmd, shlex.quote(old_principal), shlex.quote(new_principal))
    returncode, stdout, stderr = run(cmd)
    return returncode, stdout, stderr

def ktadd(keytab_filename, principals):
    cmd = "{} ktadd -k {} ".format(kadmin_cmd, shlex.quote(keytab_filename))
    cmd += " ".join([shlex.quote(x) for x in principals])
    returncode, stdout, stderr = run(cmd)
    return returncode, stdout, stderr

def check_password(principal, password):
    temp_cache_filename = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    try:
        cmd = "echo {} | {} {} -c {}".format(
            shlex.quote(password),
            shlex.quote(kinit_cmd),
            shlex.quote(principal),
            shlex.quote(temp_cache_filename),
        )
        returncode, stdout, stderr = run(cmd)
        if returncode == 0:
            return True
        else:
            raise RuntimeError(stderr)
    finally:
        if os.path.exists(temp_cache_filename):
            os.unlink(temp_cache_filename)
