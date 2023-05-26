from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class AiResult:
    isValid: bool
    gaitType: str = None
    graphs: Dict[str, List[Union[int, float]]] = None

    def toDict(self) -> Dict:
        return {
            'isValid': self.isValid,
            'gaitType': self.gaitType,
            'graphs': self.graphs
        }
