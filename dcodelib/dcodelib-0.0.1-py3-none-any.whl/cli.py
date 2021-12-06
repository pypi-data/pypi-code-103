import typer
from typing import Optional
from .serializers import *
from .utils import logger, get_path

mainCli = typer.Typer()
baseCli = typer.Typer(name = 'base')

b64Cli = typer.Typer(name = 'b64', short_help='Base64')
bgzCli = typer.Typer(name = 'bgz', short_help='Base64 + Gzip')

#baseCli.add_typer(b64Cli)
#baseCli.add_typer(bgzCli)

jsonCli = typer.Typer(name = 'json')
yamlCli = typer.Typer(name = 'yaml')

mainCli.add_typer(b64Cli)
mainCli.add_typer(bgzCli)
mainCli.add_typer(jsonCli)
mainCli.add_typer(yamlCli)

@mainCli.command('uuid')
def mk_uuid():
    uuid = Base.get_uuid()
    logger('\n' + uuid)


@b64Cli.command('encode')
def b64_encode(
    text: str = typer.Argument(None),
    path: Optional[str] = typer.Argument(None)
    ):
    rez = Base.b64_encode(text)
    if path: 
        path = get_path(path)
        path.write_text(rez, encoding='UTF-8')
        logger(f'Wrote Result to {path.as_posix()}')
    logger('\n' + rez)


@b64Cli.command('decode')
def b64_decode(
    text: str = typer.Argument(None), 
    path: Optional[str] = typer.Argument(None)
    ):
    rez = Base.b64_decode(text)
    if path: 
        path = get_path(path)
        path.write_text(rez, encoding='UTF-8')
        logger(f'Wrote Result to {path.as_posix()}')
    logger('\n' + rez)

@bgzCli.command('encode')
def bgz_encode(
    text: str = typer.Argument(None),
    path: Optional[str] = typer.Argument(None)
    ):
    rez = Base.b64_gzip_encode(text)
    if path: 
        path = get_path(path)
        path.write_text(rez, encoding='UTF-8')
        logger(f'Wrote Result to {path.as_posix()}')
    logger('\n' + rez)


@bgzCli.command('decode')
def bgz_decode(
    text: str = typer.Argument(None), 
    path: Optional[str] = typer.Argument(None)
    ):
    rez = Base.b64_gzip_decode(text)
    if path: 
        path = get_path(path)
        path.write_text(rez, encoding='UTF-8')
        logger(f'Wrote Result to {path.as_posix()}')
    logger('\n' + rez)


