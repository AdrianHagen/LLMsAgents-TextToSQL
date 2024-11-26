from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages


class FeedbackResponse(TypedDict):
    query_result: str
    is_correct: bool
    feedback: str
    updated_query: str


class FixerResponse(TypedDict):
    error_message: str
    specific_error: str
    advise: str


class State(TypedDict):
    messages: Annotated[list, add_messages]
    relevant_database: str
    relevant_tables: dict
    descriptions: str
    original_question: str
    generated_sql_queries: list
    feedbacks: List[FeedbackResponse]
    errors: list
    final_query: str
