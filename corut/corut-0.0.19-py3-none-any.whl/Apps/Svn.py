#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It is designed to connect as SVN Remote Client and read all data.
In this way, Commitment details will be received and managed as requested.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import collections
import dateutil.parser
import html
import xml.etree.ElementTree
from difflib import unified_diff
from time import time, sleep
from .. import __author__, __email__
from ..Apps.FileRw import file_rw
from ..Decorators import try_except, calculate_time_processing
from ..OS import delete_files_or_folders, get_path_temp, join_directory, get_basename
from ..Shell import run_cmd_2


class _Remote:
    def __init__(self, url, username=None, password=None, trust_cert=None):
        self.url = url
        self.__username = username
        self.__password = password
        self.__trust_cert = trust_cert

    def __repr__(self):
        return '<SVN(REMOTE) %s>' % self.url

    @staticmethod
    def __element_text(element):
        if element and len(element.text):
            return element.text
        return None

    @staticmethod
    def _split_file_hunk(file_hunk):
        lines = file_hunk.split('\n')
        filepath = lines[0][len('Index: '):]
        assert lines[2].startswith('--- '), f"Could not find 'left' header prefix: [{lines[2]}]"
        assert lines[3].startswith('+++ '), f"Could not find 'right' header prefix: [{lines[3]}]"
        file_hunk_left_phrase = lines[2][len('--- '):].split('\t')
        file_hunk_right_phrase = lines[3][len('+++ '):].split('\t')
        lines = lines[4:]
        hunks = []
        while True:
            if not lines:
                break
            hunk_lines_phrase = lines[0]
            lines = lines[1:]
            hunk_lines = []
            for line in lines:
                if line.startswith('@@ '):
                    break
                hunk_lines.append(line)
            lines = lines[len(hunk_lines):]
            hunks.append({'lines_phrase': hunk_lines_phrase, 'body': '\n'.join(hunk_lines), })
        hunks_info = {
            'left_phrase': file_hunk_left_phrase,
            'right_phrase': file_hunk_right_phrase,
            'hunks': hunks,
        }
        return filepath, hunks_info

    def run_command(self, subcommand, args, **kwargs):
        cmd = ['svn', '--non-interactive']
        if self.__trust_cert:
            cmd += ['--trust-server-cert']
        if self.__username and self.__password:
            cmd += ['--username', self.__username]
            cmd += ['--password', self.__password]
            cmd += ['--no-auth-cache']
        cmd += [subcommand] + args
        return run_cmd_2(cmd, **kwargs)

    def info(self, rel_path=None, revision=None):
        cmd = []
        if revision:
            cmd += ['-r', str(revision)]
        full_url_or_path = self.url
        if rel_path:
            full_url_or_path += '/' + rel_path
        cmd += ['--xml', full_url_or_path]
        result = self.run_command('info', cmd, do_combine=True)
        root = xml.etree.ElementTree.fromstring(result)
        entry_attr = root.find('entry').attrib
        commit_attr = root.find('entry/commit').attrib
        relative_url = root.find('entry/relative-url')
        author = root.find('entry/commit/author')
        wcroot_abspath = root.find('entry/wc-info/wcroot-abspath')
        wcinfo_schedule = root.find('entry/wc-info/schedule')
        wcinfo_depth = root.find('entry/wc-info/depth')
        info = {
            'url': root.find('entry/url').text,
            'relative_url': self.__element_text(relative_url),
            'entry#kind': entry_attr['kind'],
            'entry#path': entry_attr['path'],
            'entry#revision': int(entry_attr['revision']),
            'repository/root': root.find('entry/repository/root').text,
            'repository/uuid': root.find('entry/repository/uuid').text,
            'wc-info/wcroot-abspath': self.__element_text(wcroot_abspath),
            'wc-info/schedule': self.__element_text(wcinfo_schedule),
            'wc-info/depth': self.__element_text(wcinfo_depth),
            'commit/author': self.__element_text(author),
            'commit/date': dateutil.parser.parse(root.find('entry/commit/date').text),
            'commit#revision': int(commit_attr['revision']),
        }
        info['entry_kind'] = info['entry#kind']
        info['entry_path'] = info['entry#path']
        info['entry_revision'] = info['entry#revision']
        info['repository_root'] = info['repository/root']
        info['repository_uuid'] = info['repository/uuid']
        info['wcinfo_wcroot_abspath'] = info['wc-info/wcroot-abspath']
        info['wcinfo_schedule'] = info['wc-info/schedule']
        info['wcinfo_depth'] = info['wc-info/depth']
        info['commit_author'] = info['commit/author']
        info['commit_date'] = info['commit/date']
        info['commit_revision'] = info['commit#revision']
        return info

    def log_default(
            self, timestamp_from_dt=None, timestamp_to_dt=None, limit=None, rel_filepath=None,
            stop_on_copy=False, revision_from=None, revision_to=None,
            changelist=False, use_merge_history=False
    ):
        full_url_or_path = self.url
        if rel_filepath:
            full_url_or_path += '/' + rel_filepath
        timestamp_from_phrase = f'{{timestamp_from_dt.isoformat()}}' if timestamp_from_dt else ''
        timestamp_to_phrase = f'{{timestamp_to_dt.isoformat()}}' if timestamp_to_dt else ''
        args = []
        if timestamp_from_phrase or timestamp_to_phrase:
            if not timestamp_from_phrase:
                raise ValueError(
                    "The default log retriever can not take "
                    "a TO timestamp without a FROM timestamp."
                )

            if not timestamp_to_phrase:
                timestamp_to_phrase = 'HEAD'
            args += ['-r', timestamp_from_phrase + ':' + timestamp_to_phrase]
        if revision_from or revision_to:
            if timestamp_from_phrase or timestamp_to_phrase:
                raise ValueError("The default log retriever can not take both "
                                 "timestamp and revision number ranges.")
            if not revision_from:
                revision_from = '1'
            if not revision_to:
                revision_to = 'HEAD'
            args += ['-r', str(revision_from) + ':' + str(revision_to)]
        if limit:
            args += ['-l', str(limit)]
        if stop_on_copy:
            args += ['--stop-on-copy']
        if use_merge_history:
            args += ['--use-merge-history']
        if changelist:
            args += ['--verbose']
        result = self.run_command('log', args + ['--xml', full_url_or_path], do_combine=True)
        root = xml.etree.ElementTree.fromstring(result)
        named_fields = ['date', 'msg', 'revision', 'author', 'changelist']
        c = collections.namedtuple('LogEntry', named_fields)
        for e in root.iter('logentry'):
            entry_info = {x.tag: x.text for x in e}
            date = None
            date_text = entry_info.get('date')
            if date_text:
                date = dateutil.parser.parse(date_text)
            log_entry = {
                'msg': entry_info.get('msg'),
                'author': entry_info.get('author'),
                'revision': int(e.get('revision')),
                'date': date,
                'changelist': None
            }
            if changelist:
                cl = []
                for ch in e.findall('paths/path'):
                    cl.append((ch.attrib['action'], ch.text))
                log_entry.update({'changelist': cl})
            yield c(**log_entry)

    def export(self, to_path, revision=None, force=False):
        cmd = []
        if revision:
            cmd += ['-r', str(revision)]
        cmd += [self.url, to_path]
        cmd.append('--force') if force else None
        self.run_command('export', cmd)

    def list(self, extended=False, rel_path=None):
        full_url_or_path = self.url
        if rel_path:
            full_url_or_path += '/' + rel_path
        if extended is False:
            for line in self.run_command('ls', [full_url_or_path]):
                line = line.strip()
                if line:
                    yield line
        else:
            raw = self.run_command('ls', ['--xml', full_url_or_path], do_combine=True)
            root = xml.etree.ElementTree.fromstring(raw)
            list_ = root.findall('list/entry')
            for entry in list_:
                entry_attr = entry.attrib
                kind = entry_attr['kind']
                name = entry.find('name').text
                size = entry.find('size')
                if size:
                    size = int(size.text)
                commit_node = entry.find('commit')
                author = commit_node.find('author').text
                date = dateutil.parser.parse(commit_node.find('date').text)
                commit_attr = commit_node.attrib
                revision = int(commit_attr['revision'])
                entry = {
                    'kind': kind,
                    'is_directory': kind == 'dir',
                    'name': name,
                    'size': size,
                    'author': author,
                    'date': date,
                    'timestamp': date,
                    'commit_revision': revision,
                }
                yield entry

    def diff(self, old, new, rel_path=None):
        full_url_or_path = self.url
        if rel_path:
            full_url_or_path += '/' + rel_path
        arguments = [
            '--old', f'{full_url_or_path}@{old}',
            '--new', f'{full_url_or_path}@{new}',
        ]
        diff_result = self.run_command('diff', arguments, do_combine=True)
        diff_result = diff_result.strip()
        hunks = {}

        def _process_hunk(_file_hunk_raw):
            filepath, hunks_info = self._split_file_hunk(_file_hunk_raw)
            hunks[filepath] = hunks_info

        while True:
            if not diff_result:
                break
            assert diff_result.startswith('Index: '), \
                f"Diff output doesn't start with 'Index:':\n{diff_result}"
            try:
                next_index = diff_result.index('Index: ', 1)
            except ValueError:
                _process_hunk(diff_result)
                break
            file_hunk_raw, diff_result = diff_result[:next_index], diff_result[next_index:]
            _process_hunk(file_hunk_raw)
        return hunks

    def checkout(self, path, revision=None):
        cmd = []
        if revision:
            cmd += ['-r', str(revision)]
        cmd += [self.url, path]
        self.run_command('checkout', cmd)


class StrToHtml:
    CSS = """
    body {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 21px;
    }
    add {
        background-color: #24c73f;
    }
    delete {
        background-color: #fc3705;
    }
    info {
        background-color: yellow;
    }
    info2 {
        color: #fc3705;
    }
    """

    @try_except
    def converter(self, file_name, data):
        page = f'<!-- Created by {__author__} / {__email__}-->\n'
        page += '<html>\n'
        page += '<head>\n'
        page += """<meta http-equiv="Content-Type" content="text/html; charset="UTF-8"">\n"""
        page += f'<title>{file_name} Diff File</title>\n'
        page += f"""<style type="text/css">\n{self.CSS}\n</style>\n"""
        page += '<body lang=TR>\n'
        data = html.escape(data).replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;').split('\n')
        for i, line in enumerate(data):
            if i in (1, 2, 3):
                page += f'\t<br><info>{line}</info>\n'
            elif str(line).startswith('@@ '):
                page += f'\t<br><info2>{line}</info2>\n'
            elif str(line).startswith('+'):
                page += f'\t<br><add>{line}</add>\n'
            elif str(line).startswith('-'):
                page += f'\t<br><delete>{line}</delete>\n'
            else:
                page += f'\t<br>{line}\n'
        page += '</body>\n'
        page += '</head>\n'
        page += '</html>\n'
        return page


class RemoteClient:
    def __init__(self, target_url, username=None, password=None):
        self.__username = username
        self.__password = password
        self.__SVN = _Remote(target_url, username=self.__username, password=self.__password)
        self.__revision_from = None
        self.__revision_to = None
        self.__ignore_dirs = None
        self.__ignore_files = None
        self.__create_diff_file = None
        self.__maximum_time_for_reconnection = None
        self.__repo_root = ''
        self.__repo_link_for_active_commit_files = None
        self.__active_revision = 0
        self.__active_revision = None

    def __enter__(self):
        return self

    @try_except
    def __get_diff_for_selected_file(self, file):
        diff = None
        if self.__create_diff_file:
            t = time()
            while (t + self.__maximum_time_for_reconnection) > time():
                client = _Remote(
                    self.__repo_root + file, username=self.__username, password=self.__password
                )
                diff = client.diff(self.__active_revision - 1, self.__active_revision)
                if diff != {}:
                    break
                sleep(10)
                print(self.__active_revision - 1, self.__active_revision)
                print(self.__repo_root + file)
            value = list(diff.values())
            if value.__len__() > 0:
                value = value[0]
                diff = f"Index: {list(diff.keys())[0]}\n"
                diff += '='*99 + '\n'
                diff += f"--- {' '.join(i for i in value.get('left_phrase'))}\n"
                diff += f"+++ {' '.join(i for i in value.get('right_phrase'))}\n"
                # for sub_diff in value.get('hunks'):
                #     diff += sub_diff.get('lines_phrase') + '\n' + sub_diff.get('body') + '\n'
                diff += self.get_diff_from_before_and_after_file(file)
        return diff

    @try_except
    def __get_commit_change_list(self, data):
        files = []
        if isinstance(self.__ignore_files, str):
            self.__ignore_files = [self.__ignore_files]
        if isinstance(self.__ignore_dirs, str):
            self.__ignore_dirs = [self.__ignore_dirs]
        for (status, file) in data:
            _file = file[1:].split('/')
            if isinstance(self.__ignore_dirs, list) and any(i in _file for i in self.__ignore_dirs):
                print(f'Unwanted folder found ---> {_file}')
                continue
            if self.__ignore_files:
                for diff_file in self.__ignore_files:
                    if diff_file in file:
                        files.append([status, file, self.__get_diff_for_selected_file(file)])
            else:
                files.append([status, file, []])
        self.__repo_link_for_active_commit_files = ''
        for (status, file, diff) in files:
            self.__repo_link_for_active_commit_files += f'{self.__repo_root + file}\n'
        return files

    @try_except
    def export_file(self, to_path, revision=None, force=False):
        self.__SVN.export(to_path=to_path, revision=revision, force=force)

    @calculate_time_processing
    @try_except
    def get_commits(
            self,
            revision_from=0, revision_to=0,
            ignore_dirs=None, ignore_files=None,
            create_diff_file=False,
            maximum_time_for_reconnection=60
    ):
        self.__revision_from = revision_from
        self.__revision_to = revision_to
        self.__ignore_dirs = ignore_dirs
        self.__ignore_files = ignore_files
        self.__create_diff_file = create_diff_file
        self.__maximum_time_for_reconnection = maximum_time_for_reconnection
        self.__repo_root = ''
        self.__repo_link_for_active_commit_files = None
        self.__active_revision = 0
        if self.__revision_from:
            assert isinstance(self.__revision_from, int), 'Value must be integer'
        if self.__revision_to:
            assert isinstance(self.__revision_to, int), 'Value must be integer'

        print(f'Get Commits --> Active Revision:{self.__revision_from} ---> Repo:{self.__SVN.url}')
        commits = {}
        self.__repo_root = self.__SVN.info()['repository/root']
        for commit in self.__SVN.log_default(revision_from=self.__revision_from, changelist=True):
            if self.__revision_from < commit.revision <= self.__revision_to:
                self.__active_revision = commit.revision
                commits.update(
                    {
                        commit.revision: {
                            'REVISION': commit.revision,
                            'AUTHOR': commit.author,
                            'DATE': commit.date,
                            'MESSAGE': commit.msg,
                            'CHANGED_FILES': self.__get_commit_change_list(commit.changelist)
                        }
                    }
                )
                print(f'Added revision:{commit.revision} in commits')
        return commits

    @try_except
    def get_diff_from_before_and_after_file(self, file):
        diff_text = ''
        if self.__create_diff_file:
            t = time()
            while (t + self.__maximum_time_for_reconnection) > time():
                path_file_1 = join_directory(get_path_temp(), f"file1.{get_basename(file)}")
                path_file_2 = join_directory(get_path_temp(), f"file2.{get_basename(file)}")
                client = _Remote(
                    self.__repo_root + file, username=self.__username, password=self.__password
                )
                client.export(path_file_1, self.__active_revision - 1)
                client.export(path_file_2, self.__active_revision)
                before = file_rw(path_file_1, mode='r', list_format=True)
                after = file_rw(path_file_2, mode='r', list_format=True)
                diff_text = '\n'.join(i for i in unified_diff(before, after))[9:]
                delete_files_or_folders([path_file_1, path_file_2]),
                if diff_text != '':
                    break
        return diff_text

    @try_except
    def get_last_revision(self):
        revision = self.__SVN.info().get('commit_revision')
        print(f'Last Revision:{revision} ---> Repo:{self.__SVN.url}')
        return revision

    @try_except
    def info(self):
        self.__SVN.info()

    @try_except
    def path_dir(self, path):
        values = _Remote(path, username=self.__username, password=self.__password).list()
        return [str(i).rstrip('/') for i in values]

    def set_target_url(self, url):
        self.__SVN.url = url
