from pydantic import BaseModel


class ExamConclusion(BaseModel):
    status: bool