from coverage.control import Coverage
from git import Repo
import subprocess
from collections import defaultdict
import pathlib
from coverage.report import get_analysis_to_report


def missing_diff_lines():
    changes = Changes()
    changed_lines = changes.changed_lines_lut
    changed_files = changes.changed_files
    missing_lines = load_missing_lines(changed_files)
    return missing_lines.intersection(changed_lines)



class Changes:

    def __init__(self):
        self.repo = Repo('.')

    @property
    def changed_lines(self):
        output = subprocess.check_output(['git', 'diff']).decode()
        changed_files = self.parse(output)
        res = defaultdict(list)
        for filename, lines in changed_files:
            res[filename] += lines
        return dict(res)

    @property
    def changed_lines_lut(self):
        res = set()
        for filename, lines in self.changed_lines.items():
            for line in lines:
                res.add((filename, line))
        return res

    @property
    def changed_files(self):
        output = subprocess.check_output(['git', 'diff']).decode()
        changed_files = self.parse(output)
        res = set()
        for filename, _ in changed_files:
            res.add(filename)
        return res

    def parse(self, diff_output):
        blocks = diff_output.split('diff --git a/')
        files = [self._parse_block(b) for b in blocks]
        return [f for f in files if f]

    def _parse_block(self, block):
        lines = block.split('\n')
        parts = lines[0].split(' b/')
        if len(parts) != 2:
            return None
        path, _ = parts
        
        line_numbers = set()
        for line in lines:
            line_numbers.update(self._parse_range(line))

        return (
            path,
            sorted(line_numbers)
        )

    def _parse_range(self, line):
        parts = line.split('@@')

        if len(parts) != 3:
            return []
        
        _, ranges_str, _ = parts
        ranges = [self._parse_range_str(r) for r in ranges_str.split(' ') if r]
        res = set()
        for r in ranges:
            res.update(r)
        return sorted(res)

    def _parse_range_str(self, range_str):
        start, count = [abs(int(p)) for p in range_str.split(',')]
        return list(range(start, start+count)) 
        



def load_missing_lines(changed_files):
    current_dir = str(pathlib.Path().absolute()) + '/'

    coverage = Coverage(check_preimported=True, messages=True)
    coverage.load()

    res = set()

    analysis = get_analysis_to_report(coverage, [])
    for file_reporter, analysis in get_analysis_to_report(coverage, []):
        fullname = analysis.filename
        filename = fullname.replace(current_dir, '')
        if changed_files and filename not in changed_files:
            continue
        missing_lines = analysis.missing
        if not missing_lines:
            continue
        for line in missing_lines:
            res.add((filename, line))
    return res


