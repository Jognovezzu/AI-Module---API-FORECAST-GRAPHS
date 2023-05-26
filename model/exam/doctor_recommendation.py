from pydantic import BaseModel


class Doctor_recommendation(BaseModel):
    recommendation: str