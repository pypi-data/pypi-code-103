import click
import os


@click.command()
@click.argument('find_string')
@click.option('--file_pattern', '-f', default=".*",
              help='Define a file pattern')
@click.option('--only_filepath', '-p', is_flag=True,
              help='print only filepaths')
@click.option('--short-output', '-s', is_flag=True, default=False,
              help='summarize filename and output in same line')
@click.option('--full-line', '-l', is_flag=True, default=False,
              help='print full line')
def find(find_string, file_pattern, only_filepath, short_output, full_line):
    """
    Find a regular expression in all repos
    """
    from octohot.cli.config import repositories
    from octohot.cli.regex.file import File
    for repo in repositories:
        files = repo.files(file_pattern)
        for file in files:
            try:
                f = File(file)
                matches = f.find(find_string)
                if matches:
                    for match in matches:
                        if short_output:
                            if only_filepath:
                                click.echo(
                                    "%s\t(%s:%s)\t" % (
                                        file.replace(os.getcwd(), '.'),
                                        f.line(match.start()),
                                        f.line(match.end())
                                    )
                                )
                            else:
                                if full_line:
                                    click.echo(
                                        "%s\t(%s:%s)\t%s\t%s" % (
                                            file.replace(os.getcwd(), '.'),
                                            f.line(match.start()),
                                            f.line(match.end()),
                                            match.group().decode('utf-8'),
                                            f.content_by_line(f.line(match.start()), f.line(match.end()))
                                        )
                                    )
                                else:
                                    click.echo(
                                        "%s\t(%s:%s)\t%s" % (
                                            file.replace(os.getcwd(), '.'),
                                            f.line(match.start()),
                                            f.line(match.end()),
                                            match.group().decode('utf-8')
                                        )
                                    )
                        else:
                            click.echo(
                                "%s\t(%s:%s)" % (
                                    file.replace(os.getcwd(), '.'),
                                    f.line(match.start()),
                                    f.line(match.end())
                                )
                            )
                            if not only_filepath:
                                click.echo(match.group())
                                if full_line:
                                    click.echo(f.content_by_line(f.line(match.start()), f.line(match.end())))
            except UnicodeDecodeError as e:
                pass
