from assertman.cerberus_wrapper import mapping
from assertman.cerberus_wrapper import validators
from assertman.cerberus_wrapper import pretty_error
from rich.console import Console
import io
from rich.traceback import install

install()

def assert_that(document, matcher):
    __tracebackhide__ = True

    # Проверяем, что валидируемый документ - это словарь
    if not isinstance(document, (dict, list)):
        raise TypeError('Валидируемый документ должен быть словарем (json) или list')

    # Базовая схема
    _base_schema = {}

    # Конвертируем hamcrest-матчеры в формат cerberus-схемы
    _matchers_schema = mapping.extract(matcher)

    if _matchers_schema.get('schema') is None:
        _matchers_schema = {'schema': _matchers_schema, 'type': 'dict'}

    # TODO: (Кузнецов М.) Написать тесты на то что схема дополняется, а не заменяется
    for k, v in _matchers_schema['schema'].items():
        if k not in _base_schema:
            _base_schema.update({k: v})
        else:
            _base_schema[k].update(v)

    # Выполняем валидацию ответа по схеме
    # (не менять тут схему)
    validator = validators.SkyrimValidator(
        _base_schema,
        allow_unknown=True,
        require_all=True
    )

    result = validator.validate(document)

    # Если при проведени валидации по схеме найдены ошибки, выкидываем AssertionError со сформировнным текстом ошибок
    if result is False:
        # Если в результате проверок нашлись ошибки, то выкидываем AssertionError c перечнем ошибок
        error_text = pretty_error.make_assertion_text(validator.errors)
        raise AssertionError("".join(error_text))
    return True



def assert_that2(document, matcher):
    __tracebackhide__ = True

    # Проверяем, что валидируемый документ - это словарь
    if not isinstance(document, dict):
        raise TypeError('Валидируемый документ должен быть словарем (json)')

    # Базовая схема
    _base_schema = {}

    # Конвертируем hamcrest-матчеры в формат cerberus-схемы
    _matchers_schema = mapping.extract(matcher)

    # TODO: (Кузнецов М.) Написать тесты на то что схема дополняется, а не заменяется
    for k, v in _matchers_schema['schema'].items():
        if k not in _base_schema:
            _base_schema.update({k: v})
        else:
            _base_schema[k].update(v)

    # Выполняем валидацию ответа по схеме
    # (нее менять тут схему)
    validator = validators.SkyrimValidator(
        _base_schema,
        allow_unknown=True,
        require_all=True
    )

    result = validator.validate(document)

    # Если при проведени валидации по схеме найдены ошибки, выкидываем AssertionError со сформировнным текстом ошибок
    if result is False:
        install()
        # Если в результате проверок нашлись ошибки, то выкидываем AssertionError c перечнем ошибок
        error_text = pretty_error.make_assertion_text(validator.errors)


        console = Console(color_system="windows", file=io.StringIO(), width=120)

        console.print("".join(error_text))
        output = console.file.getvalue()


        raise AssertionError(output)

    return True