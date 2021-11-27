# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_pay2',
 'django_pay2.contrib.rest_framework',
 'django_pay2.migrations',
 'django_pay2.providers',
 'django_pay2.providers.coinpayments',
 'django_pay2.providers.free_kassa',
 'django_pay2.providers.payeer',
 'django_pay2.providers.perfect_money',
 'django_pay2.providers.qiwi',
 'django_pay2.providers.qiwi_kassa',
 'django_pay2.providers.sberbank',
 'django_pay2.providers.tinkoff',
 'django_pay2.providers.tinkoff.api']

package_data = \
{'': ['*'],
 'django_pay2': ['static/css/*',
                 'static/img/*',
                 'static/js/*',
                 'templates/django_pay2/*']}

install_requires = \
['Django>=3.2.7,<4.0.0',
 'django-ipware>=4.0.0,<5.0.0',
 'djangorestframework>=3.12.4,<4.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'django-pay2',
    'version': '2.0.1',
    'description': 'Интеграция платежных систем для Django',
    'long_description': "=============================\nDjangoPay2\n=============================\n\n.. image:: https://travis-ci.org/la1t/django_pay2.svg?branch=master\n    :target: https://travis-ci.org/la1t/django_pay2\n\nИнтеграция платежных систем для Django\n\nQuickstart\n----------\n\nУстановите DjangoPay2::\n\n    pip install django_pay2\n\nДобавьте приложение в `INSTALLED_APPS`:\n\n.. code-block:: python\n\n    INSTALLED_APPS = (\n        ...\n        'django_pay2',\n        ...\n    )\n\nДобавьте Django Pay's URLы в urlpatterns:\n\n.. code-block:: python\n\n\n    urlpatterns = [\n        ...\n        path('payments/', include('django_pay2.urls')),\n        ...\n    ]\n\nПлатежи\n-----------------\n\nЛюбой платеж создается методом create_<название-платежной-системы>_payment. Метод возвращает объект типа PaymentMethod. Существует два типа\nPaymentMethod — PaymentForm и RedirectMethod. Первый должен сериализовываться и отправляться на front. Второй можно либо также сериализовать\nи отправить на фронт, либо возвратить редирект.\n\nТак же метод создает объект типа Payment. Эта модель отвечает за сохранение информации о платеже, а так же об объекте-инициаторе платежа.\nПосле успешной оплаты он отправляет сигнал `payment_received` привязанному объекту.\n\nTODO\n--------\n\n- [*] Сериализаторы для PaymentForm и RedirectMethod\n- [ ] Интеграция с free_kassa\n- [ ] `handle_form_debug` проверяет, что ему пришла валидная форма\n- [*] Переписывание тестов на pytest\n- [ ] Инструкция по написанию собственных провайдеров\n- [ ] Инструкция по добавлению и настройке каждого провайдера\n- [ ] Более подробная инструкция по использованию\n- [*] Инструкция по увеличению версии\n\n\nРазработка\n----------\n\nУстановка development зависимостей\n\n::\n  pip install -r requirements_dev.txt\n\nЗапуск тестов\n\n::\n  tox\n\nВыпуск\n--------\n\n1. Установить новую версию в `pyproject.toml' и `__init__.py` файлах\n2. `poetry publish --build`\n",
    'author': 'Anatoly Gusev',
    'author_email': 'gusev.tolia@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/la1t/django_pay',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
