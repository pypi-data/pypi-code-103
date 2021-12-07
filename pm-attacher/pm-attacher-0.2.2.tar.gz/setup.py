# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pm_attacher']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0', 'pymssql>=2.2.2,<3.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['pm-attacher = pm_attacher.main:app']}

setup_kwargs = {
    'name': 'pm-attacher',
    'version': '0.2.2',
    'description': "Attach files to a patient's medical record (TrustMed)",
    'long_description': '![python-version](https://img.shields.io/badge/python-3.7+-blue.svg)\n[![publish](https://github.com/mnogomed/pm-attacher/actions/workflows/publish.yml/badge.svg)](https://github.com/mnogomed/pm-attacher/actions/workflows/publish.yml)\n![PyPI](https://img.shields.io/pypi/v/pm-attacher)\n\n# Прикрепление файлов к МКАБ\n\nУтилита предназначена для поиска и прикрепления файлов к медицинским картам амбулаторных больных (МКАБ), основываясь на имени файла, в котором должен быть номер МКАБ.\n\n## Установка\n\n```shell\npip install pm-attacher\n```\n\n## Настройка\n\nУправление параметрами утилиты производится либо через переменные окружения, либо через ключи запуска, причём приоритет имеют последние. Обязательные параметры обозначены значком :exclamation:\n\n| Ключ запуска         | Переменная<br>окружения |               | Значение по<br>умолчанию | Описание                                          |\n|----------------------|-------------------------|:-------------:|--------------------------|---------------------------------------------------|\n| `--file-type-code`   |                         | :exclamation: |                          | Код типа файла                                    | \n| `--file-type-name`   |                         | :exclamation: |                          | Наименование типа файла                           | \n| `--file-info-name`   |                         |               | `Протокол осмотра`       | Наименование файла                                | \n| `--create-user-id`   |                         |               | `1`                      | Идентификатор пользователя,<br>прикрепившего файл | \n| `--create-user-name` |                         |               | `Администратор`          | ФИО пользователя,<br>прикрепившего файл           | \n| `--prefix`           |                         |               |                          | Префикс имени файла                               |         \n| `--suffix`           |                         |               |                          | Суффикс имени файла                               |         \n| `--recursive`        |                         |               |                          | Рекурсивный поиск                                 |      \n| `--dry-run`          |                         |               |                          | Тестовый запуск,<br>изменения не сохраняются      |        \n| `--mis-db-server`    | `MIS_DB_SERVER`         | :exclamation: |                          | Адрес сервера МИС                                 |  \n| `--mis-db-port`      | `MIS_DB_PORT`           |               | `1433`                   | Порт сервера МИС                                  |    \n| `--mis-db-name`      | `MIS_DB_NAME`           | :exclamation: |                          | Наименование базы данных                          |    \n| `--mis-db-username`  | `MIS_DB_USERNAME`       |               | `sa`                     | Имя пользователя для<br>подключения к БД МИС      |\n| `--mis-db-password`  | `MIS_DB_PASSWORD`       | :exclamation: |                          | Пароль пользователя для<br>подключения к БД МИС   |\n| `--mis-file-path`    | `MIS_FILE_PATH`         | :exclamation: |                          | Путь до хранилища<br>прикреплённых файлов МИС     |  \n| `--log-path`         | `PMA_LOG_PATH`          |               |                          | Путь для хранения<br>журнала приложения           |         \n\nКлючи `--create-user-id` и `--create-user-name` должны соответствовать полям `UserID` и `FIO` таблицы `x_User`.\n\nКлючи `--file-type-code` и `--file-type-name` должны соответствовать полям `Code` и `Name` таблицы `atf_FileType`. Если совпадение по коду не будет найдено, то программа создаст тип прикрепляемого файла с указанными параметрами. **Внимание!** Поиск типа производится по полю `Code` и используется\nпервое найденное вхождение.\n\nКлючи `--recursive` и `--dry-run` являются флагами и им **не передаются** значения.\n\nПри использовании ключа `--log-path` в указанной директории будет формироваться журнал `debug.log` с ротацией каждые 1 Мб и очисткой данных через 3 месяца.\n\nПолучить справку по описанным выше параметрам из командной строки можно запустив утилиту с ключом `--help`:\n\n```shell\npm-attacher --help\n```\n\n## Запуск\n\nПри запуске необходимо определить обязательные параметры (таблица выше) и указать путь, по которому будет производиться обработка файлов:\n\n```shell\npm-attacher [OPTIONS] WATCH_DIR\n```\n\nДля получения информации о названии и версии утилиты необходимо выполнить команду с ключом `--version`:\n\n```shell\npm-attacher --version\n```\n',
    'author': 'Vladislav Chmelyuk',
    'author_email': 'neimp@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
