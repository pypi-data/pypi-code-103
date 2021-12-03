import os
import sys
import subprocess


def main():
    para = sys.argv[1:]
    # print(para)
    auto = subprocess.getstatusoutput('py=$(which python) && echo ${py%bin*}lib/python*/site-packages/tsc_auto/auto.sh')
    if auto[0] == 0:
        auto = auto[1]
    else:
        raise NameError(str(auto))
    os.system(f'chmod 777 {auto} && {auto} ' + ' '.join(para))


if __name__ == '__main__':
    main()
