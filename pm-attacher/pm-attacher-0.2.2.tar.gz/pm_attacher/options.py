import typer

CLI_OPTIONS = {
    'file_type_code'  : typer.Option(..., help='Код типа файла'),
    'file_type_name'  : typer.Option(..., help='Наименование типа файла'),
    'file_info_name'  : typer.Option('Протокол осмотра', help='Наименование файла'),
    'create_user_id'  : typer.Option(1, help='Идентификатор пользователя, прикрепившего файл'),
    'create_user_name': typer.Option('Администратор', help='ФИО пользователя, прикрепившего файл'),
    'prefix'          : typer.Option('', help='Префикс имени файла'),
    'suffix'          : typer.Option('', help='Суффикс имени файла'),
    'recursive'       : typer.Option(False, help='Рекурсивный поиск'),
    'dry_run'         : typer.Option(False, help='Тестовый запуск'),
    'mis_db_server'   : typer.Option(..., envvar='MIS_DB_SERVER', help='Адрес сервера МИС'),
    'mis_db_port'     : typer.Option(1433, envvar='MIS_DB_PORT', help='Порт сервера МИС'),
    'mis_db_name'     : typer.Option(..., envvar='MIS_DB_NAME', help='Имя базы данных'),
    'mis_db_username' : typer.Option('sa', envvar='MIS_DB_USERNAME', help='Имя пользователя для подключения к БД МИС'),
    'mis_db_password' : typer.Option(..., envvar='MIS_DB_PASSWORD',
                                     help='Пароль пользователя для подключения к БД МИС'),
    'mis_file_path'   : typer.Option(..., envvar='MIS_FILE_PATH', help='Путь до хранилища прикреплённых файлов МИС'),
    'log_path'        : typer.Option(None, envvar='PMA_LOG_PATH', help='Путь для хранения журнала приложения'),
}
