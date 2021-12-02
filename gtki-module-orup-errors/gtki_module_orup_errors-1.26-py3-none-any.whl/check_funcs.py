""" Содержит все функции проверок для алертов из модуля all_errors"""
from orup_errors import general_functions


def check_car_number(car_number, *args, **kwargs):
    if len(car_number) < 8 or len(car_number) > 10 \
            and not general_functions.is_car_num_valid(car_number):
        return True


def check_car_has_rfid(have_rfid, choose_mode, *args, **kwargs):
    if have_rfid and choose_mode == 'manual':
        return True


def check_scale_fail(weight_data: int, aliquot=10, *args, **kwargs):
    """ Проверить весы на работоспособность. Обычно WeightDataSplitter возвращает коды ошибок, не кратные 10."""
    if weight_data % aliquot != 0:
        return True

def check_brutto_on_exit(course: str, have_brutto: bool, car_protocol: str, tko_protocol='rfid', *args, **kwargs):
    if course == "OUT" and not have_brutto and car_protocol == tko_protocol:
        return True


def check_brutto_having_brutto(course: str, have_brutto: bool, car_protocol: str, tko_protocol='rfid', *args, **kwargs):
    if have_brutto and course == 'IN' and car_protocol == tko_protocol:
        return True


def check_carrier_incorrectness(carrier_name: str, carriers_list:list, *args, **kwargs):
    return check_type_incorrectness(carrier_name, carriers_list)


def check_tc_incorrectness(chosen_trash_cat, cats_list, *args, **kwargs):
    return check_type_incorrectness(chosen_trash_cat, cats_list)


def check_tt_incorrectness(type_name: str, types_list: list, *args, **kwargs):
    return check_type_incorrectness(type_name, types_list)


def check_carrier_debtor(carrier_name:str, debtors_list: list, *args, **kwargs):
    return check_type_correctness(carrier_name, debtors_list)


def check_type_correctness(given: any, list_name: list, *args, **kwargs):
    """ Проверить факт нахождение элемента given в list_name """
    if given in list_name:
        return True


def check_type_incorrectness(given: any, list_name: list, *args, **kwargs):
    """ Проверить факт НЕ нахождение элемента given в list_name """
    if given not in list_name:
        return True


def check_ar_busy(ar_status: bool, busy_status=False, *args, **kwargs):
    if ar_status == busy_status:
        return True


def other_instead_tko(chosen_trash_cat: str, tko_name='ТКО-4', must_be_tko=False, *args, **kwargs):
    """ Указали какую то категорию груза, а рейс c ТКО (tko_name) был запланирован """
    if chosen_trash_cat != tko_name and must_be_tko:
        return True


def tko_instead_other(chosen_trash_cat: str, tko_name='ТКО-4', must_be_tko=False, *args, **kwargs):
    """ Указали ТКО (tko_name), а рейс не был запланирован """
    if chosen_trash_cat == tko_name and not must_be_tko:
        return True
