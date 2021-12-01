"""
Kubenetes CLI
"""
import argparse
import re
import os
import subprocess
import sys


class ColorTag:
    RESET = '\x1b[0m'

    RED = '\x1b[5;31;40m'
    BLUE = '\x1b[5;34;40m'
    CYAN = '\x1b[5;36;40m'
    GRAY = '\x1b[5;37;40m'
    GREEN = '\x1b[5;32;40m'
    YELLOW = '\x1b[5;33;40m'

    ON_RED = '\x1b[5;30;41m'
    ON_BLUE = '\x1b[5;30;44m'
    ON_CYAN = '\x1b[5;30;46m'
    ON_GRAY = '\x1b[5;30;47m'
    ON_GREEN = '\x1b[5;30;42m'
    ON_YELLOW = '\x1b[5;30;43m'

    RED_ON_YELLOW = '\x1b[5;31;43m'
    BLUE_ON_YELLOW = '\x1b[3;34;43m'
    GRAY_ON_CYAN = '\x1b[3;37;46m'
    GRAY_ON_RED = '\x1b[3;37;41m'
    YELLOW_ON_RED = '\x1b[5;33;41m'
    YELLOW_ON_BLUE = '\x1b[5;33;44m'


class Kubes:

    try:
        _TERMINAL_SIZE_WIDTH = os.get_terminal_size().columns
    except:
        _TERMINAL_SIZE_WIDTH = 90

    _FG_COLORS = [
        ColorTag.CYAN,
        ColorTag.GRAY,
        ColorTag.GREEN,
        ColorTag.YELLOW,
        ColorTag.RED,
        ColorTag.BLUE,
    ]

    _BG_COLORS = [
        ColorTag.ON_CYAN,
        ColorTag.ON_GRAY,
        ColorTag.ON_GREEN,
        ColorTag.ON_YELLOW,
        ColorTag.ON_RED,
        ColorTag.ON_BLUE,
    ]

    _PATTERN_FORM = r'[^ \t\n]+ *'
    _PATTERN_POD_LABEL = '[\-\w\d]?[\-\w\d]?$'
    _PATTERN_REMOTE_PATH =  r'^([\-\d\w]*):(.*)$'

    _REGEX_FORM = re.compile(_PATTERN_FORM)
    _REGEX_REMOTE_PATH = re.compile(_PATTERN_REMOTE_PATH)

    _VALID_STATUS = [
        'running',
        'active',
    ]

    @classmethod
    def _help(cls):
        print(cls.__doc__)
        sys.exit()

    @classmethod
    def _get_parser(cls):
        parser = argparse.ArgumentParser()
        action = parser.add_subparsers(description='List Subjects', dest='action')
        # ---------------- 檢視Pods ---------------- #
        ls = action.add_parser(
            'ls',
            help='List Subject [default value: pods]',
        )
        ls.add_argument(
            'subject',
            default='pods',
            type=str,
            nargs='?',
        )
        # ---------------- 檢視Namespace ---------------- #
        context = action.add_parser(
            'cx',
            help='List namespaces or switch the context to one of them',
        )
        context.add_argument(
            'namespace',
            type=str,
            nargs='?',
        )
        # ---------------- 檢視日誌 ---------------- #
        log = action.add_parser(
            'log',
            help='Show logs',
        )
        log.add_argument(
            'pod',
            type=str,
        )
        log.add_argument(
            'tail',
            help='Track the Logs back with specific number [default value: 100]',
            type=int,
            default=100,
            nargs='?',
        )
        log.add_argument(
            '--follow',
            action='store_true',
            help='Streaming pods logs',
        )
        # ---------------- 推拉檔案 ---------------- #
        copy = action.add_parser(
            'cp',
            help='Download file or directory',
        )
        copy.add_argument(
            'src',
            type=str,
        )
        copy.add_argument(
            'dest',
            type=str,
            nargs='?',
        )
        # ---------------- 交互模式 ---------------- #
        run = action.add_parser(
            'run',
            help='Execute pod with command default: bash',
        )
        run.add_argument(
            'pod',
            type=str,
        )
        run.add_argument(
            'command',
            help='Command[default: bash]',
            type=str,
            default='bash',
            nargs='?',
        )
        return parser

    @classmethod
    def _stdout(cls, output, tag=None, end='\n'):
        header = str()
        if tag:
            badge = f' [{tag.upper()}] '
            header = f'{ColorTag.ON_CYAN}{badge:-^{cls._TERMINAL_SIZE_WIDTH}}{ColorTag.RESET}\n'
        sys.stdout.write(
            f'{header}{output}{end}'
        )

    @classmethod
    def _stderr(cls, output, tag=None, end='\n'):
        header = str()
        if tag:
            badge = f' [{tag.upper()}] '
            header = f'{ColorTag.ON_RED}{badge:-^{cls._TERMINAL_SIZE_WIDTH}}{ColorTag.RESET}\n'
        sys.stderr.write(
            f'{header}'
            f'{ColorTag.RED}{output}{ColorTag.RESET}{end}'
        )
        exit('Program has been terminated')

    @classmethod
    def _exec(cls, cmd):
        try:
            output = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                shell=True,
                # timeout=10,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            cls._stderr(output=e.output, tag='error')
        else:
            return output

    @classmethod
    def _get_fg_color(cls, index):
        return cls._FG_COLORS[index % len(cls._FG_COLORS)]

    @classmethod
    def _get_bg_color(cls, index):
        return cls._BG_COLORS[index % len(cls._BG_COLORS)]

    @classmethod
    def _is_valid_status(cls, text):
        for status in cls._VALID_STATUS:
            if text.lower().startswith(status):
                return True
        return False

    @classmethod
    def _format_line(cls, index, text, status_index, is_title=None):
        if (status_index is not None) and (index == status_index) and (not cls._is_valid_status(text=text)):
            return f'{ColorTag.RED}{text}{ColorTag.RESET}'
        color = cls._get_bg_color(index=index) if is_title else cls._get_fg_color(index=index)
        return f'{color}{text}{ColorTag.RESET}'

    @classmethod
    def _format_form(cls, form, has_header=False):
        """ has_header just format the 1st line(loop) """
        if len(form) == 2 and not form[1]:
            cls._stderr(output=form[0])
        status_index = None
        for index, line in enumerate(form, start=1):
            texts = cls._REGEX_FORM.findall(line)
            if not texts:
                continue
            result = str()
            for index, text in enumerate(texts):
                result += cls._format_line(index=index, text=text, status_index=status_index, is_title=has_header)
                if has_header and 'STATUS' in text:
                    status_index = index
            cls._stdout(output=result)
            has_header = False

    @classmethod
    def _list(cls, args):
        cmd = f'kubectl get {args.subject}'
        stdout = cls._exec(cmd=cmd)
        form = stdout.split('\n')
        cls._format_form(form=form, has_header=True)

    @classmethod
    def _context(cls, args):
        if not args.namespace:
            cmd = f'kubectl get namespace'
            stdout = cls._exec(cmd=cmd)
            form = stdout.split('\n')
            cls._format_form(form=form, has_header=True)
        else:
            cmd = f'kubectl config set-context --current --namespace={args.namespace}'
            result = cls._exec(cmd=cmd)
            cls._stdout(output=result)

    @classmethod
    def _get_pods(cls):
        cmd = 'kubectl get pods --no-headers --output=custom-columns="NAME:.metadata.name"'
        stdout = cls._exec(cmd=cmd)
        if not stdout:
            cls._stderr(output=f'No pods in the current namespace')
        return stdout.strip().split('\n')

    @classmethod
    def _get_pod(cls, pod_name):
        pods = cls._get_pods()
        if pod_name in pods:
            return pod_name
        pod_info = '\n'.join(f' - {pod}' for pod in pods)
        cls._stderr(output=f'Cannot Find < POD {pod_name} >:\n{pod_info}', tag='error')

    @classmethod
    def _is_upload(cls, src):
        """ if source is remote means download """
        if cls._REGEX_REMOTE_PATH.findall(src):
            return False
        return True

    @classmethod
    def _copy(cls, args):
        if not args.src:
            exit(f'Missing Key: --src')
        if cls._is_upload(src=args.src) and not args.dest:
            """ if it is upload dest is mandatory """
            exit(f'Missing Key: --dest "pod:/path/to/location"')
        source = args.src.replace(':/', ':')
        if args.dest:
            destination = os.path.join(args.dest, os.path.basename(source))
        else:
            destination = os.path.join('.', os.path.basename(source))
        cmd = f'kubectl cp {source} {destination}'
        result = cls._exec(cmd=cmd)
        cls._stdout(output=result)

    @classmethod
    def _run(cls, args):
        if not args.pod:
            exit(f'Missing Key: --pod')
        command = args.command or 'bash'
        pod = cls._get_pod(pod_name=args.pod)
        cmd = f'kubectl exec -it {pod} -- {command}'
        os.system(cmd)

    @classmethod
    def _log(cls, args):
        if not args.pod:
            exit(f'Missing Key: --pod')
        pod = cls._get_pod(pod_name=args.pod)
        if args.follow:
            """ 串流直至退出 """
            os.system(f'kubectl logs {pod} --follow')
            exit()
        tail = args.tail or 100
        cmd = f'kubectl logs --tail={tail} {pod}'
        stdout = cls._exec(cmd=cmd)
        logs = stdout.split('\n')
        for log in logs:
            if 'GET /probe' in log or 'kube-probe/1.18' in log:
                continue
            cls._stdout(output=log)

    @classmethod
    def cli(cls):
        parser = cls._get_parser()
        if len(sys.argv) == 1:
            parser.print_help()
        args = parser.parse_args()
        if args.action == 'ls':
            cls._list(args=args)
            parser.exit()
        if args.action == 'cx':
            cls._context(args=args)
            parser.exit()
        if args.action == 'cp':
            cls._copy(args=args)
            parser.exit()
        if args.action == 'run':
            cls._run(args=args)
            parser.exit()
        if args.action == 'log':
            cls._log(args=args)
            parser.exit()


if __name__ == '__main__':
    Kubes.cli()
