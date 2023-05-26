from typing import List, Any

from pydantic import BaseModel


class InsolePackage(BaseModel):
    leftInsoleId: str
    rightInsoleId: str
    leftData: List[Any]
    rightData: List[Any]
