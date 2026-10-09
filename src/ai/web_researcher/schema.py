from operator import add
from pydantic import BaseModel, Field
from typing import Annotated, Literal


class ResearchState(BaseModel):
    question: str = ""
    messages: Annotated[list, add]
    search_results: list = Field(default=None)
    sub_queries: list = Field(default=None)
    findings_formatted: list = Field(default=None)
    iteration: int = 0
    sufficient: bool = False
    gaps: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    follow_up_queries: list[str] = Field(default_factory=list)
    answer: str = Field(default=None)
    answer_source: str = Field(default=None)

class PlannerOutput(BaseModel):
    sub_queries: list[str] = Field(description="1-4 standalone search queries")
    reasoning: str = Field(description="brief note on why these queries were chosen")

class SearchFilterOutput(BaseModel):
    selected_urls: list[str] = Field(description="URLs worth fetching, ranked by relevance")
    discarded_reason: dict[str, str] = Field(description="url -> one-line reason for discarding, for discarded results only")

# Sythesize     
class Finding(BaseModel):
    claim: str
    source_url: str
    confidence: Literal["high", "medium", "low"] = Field(
        description="high = explicitly stated fact, medium = reasonably implied by content, low = tangential/weak support"
    )

class SynthesizeOutput(BaseModel):
    findings: list[Finding]
    content_relevant: bool = Field(description="false if this source had nothing useful for the query")

class AnswerOutput(BaseModel):
    source_url: str = Field(description="url of source used to generate answer")
    answer: str = Field(description="final answer generated from the source")


class ReflectOutput(BaseModel):
    sufficient: bool
    gaps: list[str] = Field(description="specific missing pieces, empty if sufficient=True")
    contradictions: list[str] = Field(description="description of any conflicting findings that need resolution, if any")
    follow_up_queries: list[str] = Field(description="targeted search queries to close the gaps, empty if sufficient=True")
