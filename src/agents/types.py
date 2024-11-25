from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages


class FeedbackResponse(TypedDict):
    query_result: str
    is_correct: bool
    feedback: str
    updated_query: str


class State(TypedDict):
    messages: Annotated[list, add_messages]
    relevant_database: str
    relevant_tables: list
    descriptions: str
    original_question: str
    feedbacks: List[FeedbackResponse]
    errors: list
