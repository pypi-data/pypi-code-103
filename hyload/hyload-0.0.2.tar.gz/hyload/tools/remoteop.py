import paramiko
import sys,os


class RemoteOp:

    def __init__(self,HOST,PORT,USER, PASSWD):

        print(f'connect {HOST}:{PORT} ...',end='')

        self.ssh = paramiko.SSHClient()

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


        self.ssh.connect(HOST,PORT,USER, PASSWD)

        print('ok')



    def remoteCmd(self, cmd, printCmd=True,printOutput=True):
        if printCmd:
            print(f'>> {cmd}')
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        output = stdout.read().decode('utf8')
        errinfo = stderr.read().decode()
        if printOutput:
            print(output+errinfo)
        return output+errinfo

    def putFile(self, localPath, remotePath):
        print(f'upload {localPath} to {remotePath} ...',end='')
        
        sftp = self.ssh.open_sftp()
        
        sftp.put(localPath, remotePath)
        sftp.close()

        print('ok')

    
    def getFile(self, remotePath, localPath ):
        print(f'download from {remotePath} to {localPath} ...',end='')
        
        sftp = self.ssh.open_sftp()
        
        sftp.get(remotePath,localPath)
        sftp.close()

        print('ok')



def uploadFile(HOST,PORT,USER, PASSWD,localPath,remotePath):    
    ro = RemoteOp(HOST,PORT,USER, PASSWD)
    ro.putFile(localPath,
               remotePath)
    
    print('ok')


def uploadFileAndUnGz(HOST,PORT,USER, PASSWD,localPath,remotePath):    
    ro = RemoteOp(HOST,PORT,USER, PASSWD)
    ro.putFile(localPath,
               remotePath)

    if '/' in remotePath:
        remoteDir,remoteFile = os.path.split(remotePath);
        cmd = f'cd {remoteDir} && tar zxf {remoteFile}'
    else:
        cmd = f'tar zxf {remotePath}'
    
    print(f'{cmd}')
    ro.remoteCmd(cmd)
    print('ok')


def puttyLogin(HOST,PORT,USER, PASSWD,checkLoginReady=True):
    
    from hyload.tools.PuttyAgents import LinuxPuttyAgent
    
    class machine:
        ip   = HOST
        user = USER
        passwd = PASSWD
        port = PORT
        isAutoSwitchToRoot = False
    pa = LinuxPuttyAgent(machine,checkLoginReady=checkLoginReady)

    return pa


def  downloadFiles(HOST,PORT,USER, PASSWD,remoteDir,filesStr,localPath,toolsDir):
    os.makedirs(localPath,exist_ok=True)


    ro = RemoteOp(HOST,PORT,USER, PASSWD)

    # package files 

    ro.remoteCmd(f'cd {remoteDir};rm -rf tmp.tar.gz;tar zcvf tmp.tar.gz {filesStr}')


    ro.getFile(remoteDir+'/tmp.tar.gz',os.path.join(localPath,'tmp.tar.gz'))


    unziptool = os.path.join(toolsDir,'7z.exe')
    
    file1 = localPath + os.sep + 'tmp.tar.gz'
    cmd = f'cd /d {localPath} && {unziptool} x -y {file1}'
    print (cmd)
    ret = os.system(cmd)

    if ret != 0:
        print ("\n!!uncompress gz file failed with 7z.exe, errCode = %s" % ret)
        return

    file2 = localPath + os.sep + 'tmp.tar'
    cmd = f'cd /d {localPath} && {unziptool} x -y {file2}'
    print (cmd)
    ret = os.system(cmd)

    if ret != 0:
        print ("\n!!uncompress tar file failed with 7z.exe, errCode = %s" % ret)
        return
    else:
        print ('unpackage record file successfully.')

    import subprocess
    subprocess.Popen(rf'explorer "{localPath}"') 
    