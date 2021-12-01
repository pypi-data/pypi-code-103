import click


class File(object):
    def __init__(self, filename=None):
        if not filename:
            raise ValueError("filename not be None")

        self.filename = filename
        self.content = open(self.filename, 'rb').read()
        self.decoded_content = self.content.decode()

    def line(self, charpos):
        return len(self.decoded_content[0:charpos].split('\n'))

    def find(self, pattern):
        import re
        return list(re.finditer(pattern.encode(), self.content))

    def save(self):
        with open(self.filename, 'wb') as f:
            f.write(self.content)

    def replace(self, find, replace, dryrun):
        if dryrun:
            matches = self.find(find)
            for match in matches:
                click.echo("%s: (%s,%s)" % (self.filename, match.start(), match.end()))
        else:
            import re
            self.content = re.sub(find.encode(), replace.replace('\\n', '\n').encode(), self.content)
            self.save()

    def content_by_line(self, line_start, line_end=None):
        if line_end and line_end != line_start:
            out = '\n'.join(self.decoded_content.split('\n')[line_start-1:line_end-1])
        else:
            out = self.decoded_content.split('\n')[line_start-1]

        if len(out) > 80:
            return "%s ..." % out[:80]
        else:
            return out
