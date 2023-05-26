import copy
from typing import Dict, List, Union


class InsolePackage():
    LEFT_INSOLE_MARKER = "E"
    RIGHT_INSOLE_MARKER = "D"

    def __init__(self) -> None:
        self._createPackage()

    def _createPackage(self) -> None:
        self._package = {
            'leftInsoleId': None,
            'rightInsoleId': None,
            'leftData': [],
            'rightData': []
            }

    def add(self, values: List[str]) -> None:
        # insole id(MAC Address + [ED]), piezoelectric{9}, accelerometer{3}, datetime
        insoleId = values[0].decode()
        piezoData = [float(value) for value in values[1:10]]
        accData = [float(value) for value in values[10: 13]]
        datetime_ = values[13]

        if insoleId[-1] == self.LEFT_INSOLE_MARKER:
            self._package['leftInsoleId'] = insoleId
            self._package['leftData'].append([*piezoData, *accData, datetime_])
        elif insoleId[-1] == self.RIGHT_INSOLE_MARKER:
            self._package['rightInsoleId'] = insoleId
            self._package['rightData'].append([*piezoData, *accData, datetime_])

    def clear(self) -> None:
        self._createPackage()

    def getCurrentData(self) -> Dict[str, List[Union[str, float]]]:
        package = copy.deepcopy(self._package)
        self.clear()
        return package
