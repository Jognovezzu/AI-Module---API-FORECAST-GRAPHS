import re


INSOLE_ID_PATTERN = '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})[ED]'  # MAC Address + E|D
PIEZORESISTIVE_DATA_PATTERN = '((([0-2]{1}[.][0-9]{2})|([3]{1}[.][0-3]{2})) ){9}'
ACCELEROMETER_DATA_PATTERN = '([-]?[0-1][.][0-9]{2} ){2}([-]?[0-3][.][0-9]{2})'

INPUT_DATA_PATTERN = f'^{INSOLE_ID_PATTERN} {PIEZORESISTIVE_DATA_PATTERN}{ACCELEROMETER_DATA_PATTERN}$'

inputDataPattern = re.compile(INPUT_DATA_PATTERN)


def isValid(data: bytes) -> bool:
    try:
        dataStr = data.decode()
        return inputDataPattern.match(dataStr) is not None
    
    except UnicodeDecodeError:
        return False
