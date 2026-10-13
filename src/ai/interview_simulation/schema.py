from operator import add
from pydantic import BaseModel, Field
from typing import Annotated, Literal


class State(BaseModel):
    messages: Annotated[list, add]
    iteration: int = Field(default=0)
    gaps: list[str] = Field(default_factory=list)
    summary: str = Field(default=None)

class EvaluatorOutput(BaseModel):
    gaps: list[str] = Field(description="1-4 identified gaps and areas of improvement")
    summary: str = Field(description="brief summary on how the candidate performed")
