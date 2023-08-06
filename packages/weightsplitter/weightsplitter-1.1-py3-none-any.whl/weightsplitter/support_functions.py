""" Вспомогательные функии"""
from weightsplitter.errors import UnknownTerminal
from weightsplitter import settings
import os
import importlib


def extract_terminal_func(terminal_name):
    # Возвращает функции работы с терминалом, если не может найти указанный терминал - возникает исключение
    all_terminals = get_all_terminal_dirs()
    for terminal in all_terminals:
        if terminal_name.lower() == terminal.lower():
            func = get_terminal_func(terminal)
            return func
    # Если терминал не был найден, возбудить исключение
    raise UnknownTerminal

def get_all_terminal_dirs():
    return os.listdir(settings.terminals_dir)

def get_terminal_func(terminal_name):
    # Вовзращает модуль с функциями указанного терминала
    terminal_path = "weightsplitter.terminals.{}.functions".format(terminal_name)
    func = importlib.import_module(terminal_path)
    return func
