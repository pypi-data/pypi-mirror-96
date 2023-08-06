""" Функции для терминала CAS"""
from weightsplitter import settings as s


def get_parsed_input_data(data):
    data = str(data)
    try:
        data_els = data.split(',')
        for el in data_els:
            if 'kg' in el:
                kg_els = el.split(' ')
                for element in kg_els:
                    if element.isdigit():
                        return element
    except:
        return s.fail_parse_code


def check_scale_disconnected(data):
    # Провреят, отправлен ли бит, означающий отключение Терминала
    data = str(data)
    if 'x00' in data:
        return True