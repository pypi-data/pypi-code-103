import re

from cloudrail.knowledge.utils import file_utils


def get_file_used_modules(file_path: str) -> set:
    text = file_utils.read_all_text(file_path)
    return get_text_used_modules(text)


def get_dir_used_modules(dir_path: str) -> set:
    files = file_utils.get_all_files(dir_path)
    results = set()
    for file in files:
        if file.endswith('.py'):
            results.update(get_file_used_modules(file))
    return results


def get_text_used_modules(text: str) -> set:
    results = set()
    lines = text.split('\n')
    for line in lines:
        from_import = re.search(r'from\s+([^.]*)\.?.*\s+import\s', line)
        if from_import:
            results.add(from_import.group(1))
            continue
        pure_import = re.search(r'import\s+([^.]*)\.?.*', line)
        if pure_import:
            results.add(pure_import.group(1))
            continue
        return results
