

def make_assertion_text(dict_with_errors):
    """ Сформировать и выдать легко-читаемое сообщение об ошибке """
    # TODO: (Кузнецов М) Тут нужен рефакторинг и описание
    fail_icon = '*'  # \N{Cross Mark}
    # fail_icon = '\N{Cross Mark}'
    error_texts_list = []

    def to_pretty(ddict, level=0):
        if isinstance(ddict, str):
            error_texts_list.append(f" \n{'    ' * level}{ddict}")

        elif isinstance(ddict, dict):
            for k, v in ddict.items():
                # otstup = '\t' * level
                otstup = '    ' * level

                if isinstance(v, str):
                    error_texts_list.append(f" \n{otstup}{fail_icon} {k}: {v}")
                elif isinstance(v, dict):
                    error_texts_list.append(f" \n{otstup}{fail_icon} {k}:")
                    to_pretty(v, level=level+1)
                elif isinstance(v, list):
                    assert len(v) < 3
                    if len(v) == 1:
                        to_pretty({k:v[0]}, level=level)
                    else:
                        error_texts_list.append(f" \n{otstup}{fail_icon} {k}: {v[0]}")
                        to_pretty(v[1], level=level+1)
                else:
                    raise TypeError("Не удалось распарсить результат работы cerberus")

        else:
            raise TypeError("Не удалось распарсить список ошибок")

    to_pretty(dict_with_errors)
    return error_texts_list