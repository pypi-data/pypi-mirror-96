from weightsplitter import support_functions as sf
from weightsplitter.errors import UnknownTerminal


print(sf.get_all_terminal_dirs())

func = sf.get_terminal_func('CAS')
print(func.get_parsed_input_data('213'))

def define_terminal_test():
    response = sf.extract_terminal_func('cas')
    print('Define_terminal_test:', response)

def define_terminal_test_no_terminal():
    try:
        response = sf.extract_terminal_func('cas12')
        print('Define_terminal_test_no_terminal:', response)
    except UnknownTerminal:
        print('Success. Have an exception!')

define_terminal_test()
define_terminal_test_no_terminal()