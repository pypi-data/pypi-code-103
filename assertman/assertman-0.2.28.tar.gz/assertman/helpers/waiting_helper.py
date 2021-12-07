from __future__ import absolute_import
from waiting import wait, TimeoutExpired
from hamcrest import *
import logging



def _wait_base(mode, function, matcher, timeout=10, sleep_seconds=1, waiting_for=None, on_poll=None):
    """ Циклическое выполнение переданной функции пока она:
    (a) не вернет результат удовлетворяющий переданному матчеру
    (b) ИЛИ пока не истечет таймаут ожидания.
    Подробнее тут: https://pypi.org/project/waiting/

    :param mode: strictly - прерывать работу если не дождались того чего хотели ИЛИ
                 soft - не прерывать работу, а просто возвращать False
    :param function: функция, которая будет циклически выполняться и результат которой будет сравниваться с матчером
    :param matcher: матчер
    :param timeout: таймаут ожидания по истечении которого будет брошено исключение TimeoutExpired
    :param sleep_seconds:  интервал выполнения функции (например: каждую 1 секунду)
    :param waiting_for: сообщение допоняющее сообщение брошенное TimeoutExpired'ом
    :param on_poll: функция выполняющаяся после каждого прохода цикла
    :return: значение последнего вызова function

    Рекомендации по применению:
    * Важно: функцию нужно передавать с лямбдой, что бы сюда передалась именно функция а не ее результат
        Пример lambda: qa_api.bank_card.get()
    """
    on_poll = on_poll if on_poll is not None \
        else lambda: logging.info(f"Ждем пока результат функции не будет удовлетворять переданному {matcher}")

    waiting_for = waiting_for if waiting_for is not None \
        else "function returns result that satisfying the assertion in matcher"

    # для сохранения результата последнего вызова function()
    value_to_return = None

    # т.к. в lambda нельзя использовать nonlocal и присвоение, то делаем функцию, которая возвращает True/False
    # для wait и сохраняет результат вызова function в value_to_return
    def predicate():
        nonlocal value_to_return
        value_to_return = function()
        return matcher.matches(value_to_return)

    try:
        wait(predicate=predicate,
             timeout_seconds=timeout,
             sleep_seconds=sleep_seconds,
             waiting_for=waiting_for,
             on_poll=on_poll)

    # Если вышло по таймауту, значит мы не дождались того чего хотели и в зависимости от mode
    # либо прерываем работу, либо возрващаем False
    except TimeoutExpired as timeout_error:
        waiting_failed_text = "[WAITING] Failed: Время ожидания истекло" \
                              "\n\t{}".format(timeout_error)
        try:
            assert_that(function(), matcher)
        except AssertionError as assertion_error:
            waiting_failed_text = waiting_failed_text + "\n\t{}".format(assertion_error)

        # если режим = soft, то не прерываем работу, просто выводим в лог сообщение и возвращаем False
        if mode is "soft":
            logging.info(waiting_failed_text)
            return value_to_return
        # если режим != soft, то прерываем работу и выкидываем c AssertionError
        else:
            raise AssertionError(waiting_failed_text)

    # Если не вышло по таймауту, значит мы дождались того чего хотели и возвращаем True
    logging.info(
        "[WAITING] Success: Результат функции удовлетворяет переданному матчеру. Ожидание успешно закончено")
    return value_to_return


def wait_soft_until(function, matcher, timeout=10, sleep_seconds=1, waiting_for=None, on_poll=None):
    """ Soft-ожидание, пока результат выполнения функции не будет удовлетворять матчеру.
    Если дождались - возвращаем последнее значение возвращённое function
    Если вышел таймаут возвращаем последнее значение возвращённое function
    детальнее см. описание функции "_wait_base"
    """
    return _wait_base(mode="soft", function=function, matcher=matcher,
                timeout=timeout, sleep_seconds=sleep_seconds, waiting_for=waiting_for, on_poll=on_poll)


def wait_strictly_until(function, matcher, timeout=10, sleep_seconds=1, waiting_for=None, on_poll=None):
    """ Strict-ожидание, пока результат выполнения функции не будет удовлетворять матчеру.
    Если дождались - возвращаем последнее значение возвращённое function
    Если вышел таймаут кидаем исключение и прерываем работу
    детальнее см. описание функции "_wait_base"
    """
    return _wait_base(mode="strictly", function=function, matcher=matcher,
                timeout=timeout, sleep_seconds=sleep_seconds, waiting_for=waiting_for, on_poll=on_poll)