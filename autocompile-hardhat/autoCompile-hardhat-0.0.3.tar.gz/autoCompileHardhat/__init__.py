# coding:utf-8
import shutil
import subprocess
import fileinput
import re
import os
import argparse
rootPath = os.getcwd()
def getSolcVersion(filePath):
    # 获取sol文件的版本号
    with open(filePath, 'r+', encoding='utf-8')as fr:
        lines = fr.read()
        # 首先判断是否有固定版本的
        fixedVersions = re.findall(r'pragma solidity (={0,1}0\.\d{1,2}\.\d{1,2});', lines)
        # 如果只有一个固定版本，直接返回固定版本
        if len(fixedVersions) == 1:
            currentHighestVersion = fixedVersions[0].replace('=', '')
            # print('{} 推荐编译器版本：{}'.format(filePath.split('\\')[-1], currentHighestVersion))
            return currentHighestVersion
        # 判断文件中是否存在两个不同的固定版本
        elif len(fixedVersions) > 1:
            for item in fixedVersions:
                if fixedVersions[0] != item:
                    print("{}无法编译通过".format(filePath))
                    return 'Error'
                currentHighestVersion = fixedVersions[0].replace('=', '')
                # print('{} 推荐编译器版本：{}'.format(filePath.split('\\')[-1], currentHighestVersion))
                return currentHighestVersion
        versions = re.findall(r'\d\.(\d{1,2})\.\d{1,2}', lines)
        if len(versions) == 1:
            return getMaxVersion(versions[0])
        else:
            return getMaxVersion(str(int(sorted(versions)[-1]) - 1))


def getMaxVersion(num):
    solcVersion = {'8': 9, '7': 6, '6': 12, '5': 17, '4': 26}
    return f'0.{num}.{solcVersion[num]}'


def getLibrayVersion(filePath):
    isImport = False
    isImportUpgrade = False
    with open(filePath, 'r+', encoding='utf-8')as fr:
        lines = fr.read()
        if lines.find('@openzeppelin/contracts') != -1:
            isImport = True
        if lines.find('@openzeppelin/contracts-upgradeable') != -1:
            isImportUpgrade = True
    return isImport, isImportUpgrade


def chageConfig(versions):
    temp = ''
    for version in versions:
        if temp!='':
            temp = temp +','+ version
        else:
            temp = version

    newversion = '{' + f"compilers:[{temp}]" + '},'
    # 更换solc版本
    for line in fileinput.input(rootPath + "/hardhat.config.js", inplace=True):
        line = re.sub(r'solidity: .*', f'solidity: {newversion}', line)
        print(line, end='')

    print("hardhat.config.js 中编译器版本已更新为：{}\n".format(newversion), end='')


def installLibray(isOldOpen, isOldUpgrade, upgradeable, normal):
    if isOldOpen:
        if not normal:
            subprocess.run('cnpm install @openzeppelin/contracts@3.4.0', shell=True, cwd=rootPath)
    else:
        if not normal:
            subprocess.run('cnpm install @openzeppelin/contracts', shell=True, cwd=rootPath)
    if isOldUpgrade:
        if not upgradeable:
            subprocess.run('cnpm install @openzeppelin/contracts-upgradeable@3.4.0', shell=True, cwd=rootPath)
    else:
        if not upgradeable:
            subprocess.run('cnpm install @openzeppelin/contracts-upgradeable', shell=True, cwd=rootPath)
    print("安装完成...")


def checkIsInstall(isOldOpen, isOldUpgrade):
    if isOldOpen:
        normal = os.path.exists(rootPath + '\\node_modules\\@openzeppelin\\contracts\\math')
    else:
        normal = os.path.exists(rootPath + '\\node_modules\\@openzeppelin\\contracts\\security')

    if isOldUpgrade:
        upgradeable = os.path.exists(rootPath + '\\node_modules\\@openzeppelin\\contracts-upgradeable\\math')
    else:
        upgradeable = os.path.exists(rootPath + '\\node_modules\\@openzeppelin\\contracts-upgradeable\\security')

    if normal and upgradeable:
        return True, upgradeable, normal
    print('有未安装的库，准备安装...')
    return False, upgradeable, normal

def moveJsonToSingleDir(Path):
    for root, dirs, files in os.walk(Path+'\\artifacts\\contracts'):
        for file in files:
            srcPath = root+'\\'+file
            dstPath = Path+'\\compileFiles\\'+file
            if not os.path.exists(Path+'\\compileFiles\\'):
                os.makedirs(Path+'\\compileFiles\\')
            shutil.copyfile(srcPath,dstPath)
    print("文件移动完成...")

def main():
    parser = _argparse()
    isOptimization = False
    optimizationTime = 200
    if parser.optimization.lower() =='true':
        isOptimization = True
        try:
            optimizationTime = int(parser.time)
        except:
            pass
    fileInfo = {}
    isOldOpen = False
    isOldUpgrade = False
    libVersion = {}
    isImportOpen = False
    isImportUpgrade = False
    for root, dirs, files in os.walk(rootPath + '\contracts'):
        for file in files:
            if file.split('.')[-1] == 'sol':
                filePath = os.path.join(root, file)
                tempIsImportOpen, tempIsImportUpgrade = getLibrayVersion(filePath)
                if not isImportUpgrade:
                    isImportOpen = tempIsImportOpen
                if not isImportUpgrade:
                    isImportUpgrade = tempIsImportUpgrade
                if filePath.find('interfaces') != -1 or filePath.find('library') != -1 or filePath.find(
                        'libraries') != -1:
                    continue
                version = getSolcVersion(filePath)
                if tempIsImportOpen:
                    if '@openzeppelin/contracts' in libVersion.keys():
                        libVersion['@openzeppelin/contracts'].append(version)
                    else:
                        libVersion['@openzeppelin/contracts'] = [version]
                if tempIsImportUpgrade:
                    if '@openzeppelin/contracts-upgradeable' in libVersion.keys():
                        libVersion['@openzeppelin/contracts-upgradeable'].append(version)
                    else:
                        libVersion['@openzeppelin/contracts-upgradeable'] = [version]
                if version != 'Error':
                    if version in fileInfo.keys():
                        fileInfo[version].append(filePath)
                    else:
                        temp = []
                        temp.append(filePath)
                        fileInfo[version] = temp

    for key in libVersion.keys():
        if key == '@openzeppelin/contracts-upgradeable':
            if sorted(libVersion['@openzeppelin/contracts-upgradeable'])[-1].split('.')[1] < '8':
                isOldUpgrade = True
        if key == '@openzeppelin/contracts':
            if sorted(libVersion['@openzeppelin/contracts'])[-1].split('.')[1] < '8':
                isOldOpen = True
    if isImportOpen:
        isInstall, upgradeable, normal = checkIsInstall(isOldOpen, isOldUpgrade)
        if not isInstall:
            if not isImportUpgrade:
                upgradeable = True
            if not isImportOpen:
                normal = True
            installLibray(isOldOpen, isOldUpgrade, upgradeable, normal)
    compilers = []
    setting = ""
    initVersion = ""
    if isOptimization:
        setting = ",settings: { optimizer: { enabled: true, runs: "+"{}".format(optimizationTime)+ "}}"
        initVersion = "{version:\"0.8.4\",settings: { optimizer: { enabled: true, runs: "+"{}".format(optimizationTime)+ "}}}"
    else:
        initVersion = "{version:\"0.8.4\"}"
    compilers.append(initVersion)
    for key in fileInfo.keys():
        temp = "{version:"+"\"{}\"{}".format(key,setting)+"}"
        compilers.append(temp)
    # print(compilers)
    chageConfig(compilers)
    subprocess.run('npx hardhat compile', shell=True, cwd=rootPath)

    print('编译完成...')

def _argparse():
        parser = argparse.ArgumentParser(description="This is description")
        parser.add_argument('--opt',default='False',dest='optimization',help='Whether to enable optimization')
        parser.add_argument('-t',default='200',dest='time',help='optimization time')
        return parser.parse_args()

if __name__ == '__main__':
	main()


