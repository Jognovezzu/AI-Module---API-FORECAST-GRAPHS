from pydantic import BaseModel


class ComplementaryExamData(BaseModel):
    leftInsoleId: str
    rightInsoleId: str
    examStartTime: str