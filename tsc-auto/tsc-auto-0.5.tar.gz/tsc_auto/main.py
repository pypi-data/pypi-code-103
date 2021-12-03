import os
import sys


def main():
    para = sys.argv[1:]
    # print(para)
    os.system('chmod 777 auto.sh && ./auto.sh ' + ' '.join(para))


if __name__ == '__main__':
    main()
