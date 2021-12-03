import re
import shutil
import uuid
from pathlib import Path

import pkg_resources
import typer
from loguru import logger

from .database import Database
from .options import CLI_OPTIONS
from .sql import *

try:
    __version = pkg_resources.get_distribution("pm-attacher").version
except pkg_resources.DistributionNotFound:
    __version = 'dev'

app = typer.Typer()


@app.command()
def version():
    try:
        _version = pkg_resources.get_distribution("pm-attacher").version
    except pkg_resources.DistributionNotFound:
        _version = 'dev'

    typer.echo(f'PM Attacher, version: {__version}')


@app.command()
def main(
        watch_dir: Path,
        file_type_code: str = CLI_OPTIONS['file_type_code'],
        file_type_name: str = CLI_OPTIONS['file_type_name'],
        file_info_name: str = CLI_OPTIONS['file_info_name'],
        create_user_id: int = CLI_OPTIONS['create_user_id'],
        create_user_name: str = CLI_OPTIONS['create_user_name'],
        prefix: str = CLI_OPTIONS['prefix'],
        suffix: str = CLI_OPTIONS['suffix'],
        recursive: bool = CLI_OPTIONS['recursive'],
        dry_run: bool = CLI_OPTIONS['dry_run'],
        mis_db_server: str = CLI_OPTIONS['mis_db_server'],
        mis_db_port: int = CLI_OPTIONS['mis_db_port'],
        mis_db_name: str = CLI_OPTIONS['mis_db_name'],
        mis_db_username: str = CLI_OPTIONS['mis_db_username'],
        mis_db_password: str = CLI_OPTIONS['mis_db_password'],
        mis_file_path: Path = CLI_OPTIONS['mis_file_path'],
        log_path: Path = CLI_OPTIONS['log_path']
):
    if log_path is not None:
        logger.add(
            log_path / 'debug.log', format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}',
            level='DEBUG', rotation='1 MB', retention='3 months', compression='tar.gz'
        )

    glob_pattern = f'{prefix}*{suffix}.*'
    if recursive:
        glob_pattern = '**/' + glob_pattern

    # Инициализируем подключение к БД
    db = Database(mis_db_server, mis_db_port, mis_db_name, mis_db_username, mis_db_password)

    if dry_run:
        logger.warning('программа запущена о режиме, не вносящем изменения!')

    for filename in Path(watch_dir).glob(glob_pattern):
        match = re.match(r'^%s(\d+)%s' % (prefix, suffix), filename.name)
        if not match:
            logger.debug(f'в имени файла {filename.absolute()} НЕ обнаружен идентификатор')
            continue

        mkab_num = match.group(1)
        logger.debug(f'в имени файла {filename.absolute()} обнаружен идентификатор: {mkab_num}')

        # Получение МКАБ по номеру карты
        try:
            mkab = db.select_all(GET_MKAB, (mkab_num,), as_dict=True)[0]
            logger.debug(f'МКАБ {mkab_num} найден')
        except IndexError:
            logger.error(f'МКАБ {mkab_num} не найден')
            continue

        # Копирование файла в директорию назначения (mis-files)
        new_filename = mis_file_path / f'{uuid.uuid4()}{filename.suffix}'
        if not dry_run:
            shutil.copy(filename, new_filename)
        logger.debug(f'файл {filename.absolute()} скопирован в {new_filename.absolute()}')

        # Находим в настройках МИС, где должны лежать файлы для всеобщего обозрения
        try:
            path = db.select_one(GET_ATTACHMENT_PATH)[0]
        except (TypeError, KeyError):
            logger.error('Не найден параметр "Путь к хранилищу прикреплённых файлов" в таблице x_UserSettings')
            raise RuntimeError

        # Находим необходимый тип прикреплённых файлов
        try:
            file_type_id = db.select_one(GET_FILETYPE_ID, (file_type_code,))[0]
        except (TypeError, KeyError):
            cursor = db.execute_query(CREATE_FILETYPE, (file_type_code, file_type_name))
            file_type_id = cursor.lastrowid

        # Находим идентификатор типа документа МКАБ
        desc_type_guid = db.select_one(GET_DOCUMENT_GUID)[0]

        # Получение записи с информацией о группе вложений
        try:
            # Ищем уже имеющуюся информацию о файле на текущий день
            file_info_id = db.select_one(GET_FILEINFO, (file_type_id, desc_type_guid, mkab['UGUID']))[0]
            logger.debug(f'Используем имеющуюся информацию о файле (FileInfoID={file_info_id})')
        except (TypeError, KeyError):
            # Если не нашли - добавляем информацию о файле
            cursor = db.execute_query(CREATE_FILEINFO, (file_type_id, desc_type_guid, mkab['UGUID']))
            file_info_id = cursor.lastrowid
            logger.debug(f'Используем вновь созданную информацию о файле (FileInfoID={file_info_id})')

        # Добавляем информацию о вложении
        db.execute_query(CREATE_ATTACHMENT, (
            create_user_id,
            create_user_name,
            file_info_id,
            '\\'.join((path, new_filename.name)),
            file_info_name
        ))

        # Удаляем файл и коммитим изменения
        if not dry_run:
            filename.unlink()
            logger.debug(f'файл {filename.absolute()} удалён')
            db.connection.commit()


if __name__ == "__main__":
    app()
