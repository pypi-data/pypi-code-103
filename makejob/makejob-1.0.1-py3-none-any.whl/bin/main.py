"""
    Generate jobfile for SJM
"""
from pathlib import Path
import click

from makejob import __epilog__
from makejob.core.util import check_queues
from makejob.core.job import make_job



@click.command(
    no_args_is_help=True,
    help=click.style(__doc__, fg='cyan', bold=True),
    epilog=click.style(__epilog__, fg='yellow'),
)
@click.argument('configfile', required=True, type=click.File())
@click.option('-o', '--outfile', help='the output filename', default='out.job', show_default=True)
@click.option('-l', '--logdir', help='the log directory', default='logs', show_default=True)
@click.option('-q', '--queue', help='specify a queue', multiple=True)
@click.option('-no', '--no-check', help='do not check queues', is_flag=True)
def cli(**kwargs):
    click.secho(f'input arguments: {kwargs}', fg='green')

    configfile = kwargs['configfile']
    logdir = Path(kwargs['logdir']).resolve()
    outfile = Path(kwargs['outfile'])

    if not logdir.exists():
        logdir.mkdir(parents=True)
    if not outfile.parent.exists():
        outfile.parent.mkdir(parents=True)

    # deal with queues
    queues = set(kwargs['queue'])
    if not kwargs['no_check']:
        avail_queues = check_queues()
        print('available queues:', avail_queues)
        queues = avail_queues.intersection(queues)
        if not queues:
            queues = avail_queues
    click.secho(f'use queues: {queues}', fg='green')

    base_scheds = '-V -cwd'
    if queues:
        base_scheds += ' -q ' + ' -q '.join(queues)

    job_list, order_list = make_job(configfile.name, base_scheds)
    click.secho(f'total jobs: {len(job_list)}', fg='green')

    with open(kwargs['outfile'], 'w') as out:
        for job in job_list:
            out.write(job + '\n\n')
        for order in order_list:
            out.write(order + '\n')
        out.write(f'\nlog_dir {logdir}\n')

    click.secho(f'save file: {kwargs["outfile"]}', fg='green')


def main():
    cli()


if __name__ == "__main__":
    main()
