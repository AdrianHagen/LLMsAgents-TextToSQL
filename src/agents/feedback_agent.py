import json

from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

from state_types import FeedbackResponse, State
from tools.database import Database
import prompt_templates.feedback_agent as templates


class FeedbackAgent:

    def __init__(self, llm: BaseChatModel = None, template: str = None) -> None:

        if template is None:
            self.template = templates.TWO_SHOT
        else:
            self.template = template
        self.prompt = PromptTemplate.from_template(self.template)
        if llm is None:
            self.llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
        else:
            self.llm = llm

    def evaluate_query(self, state: State):
        original_question = state["original_question"]
        database = state["relevant_database"]
        generated_sql_query = state["generated_sql_queries"][-1]

        response = self._evaluate_query(
            original_question, database, generated_sql_query
        )

        if response is not None:
            state["feedbacks"].append(response)
        else:
            state["errors"].append("Feedback Failed")

    def _evaluate_query(
        self, original_question: str, database: str, generated_sql_query: str
    ) -> FeedbackResponse | None:
        try:
            db = Database(database)

            (results, _) = db.execute_query(generated_sql_query)
        except Exception as e:
            print(e)
            return {
                "query_result": "error",
                "is_correct": False,
                "feedback": f"Error executing query: {e}",
                "updated_query": None,
            }

        if len(results) > 20:
            results = str(results[:10]) + "..." + str(results[-10:])

        p = self.prompt.invoke(
            input={
                "original_question": original_question,
                "database": database,
                "generated_sql_query": generated_sql_query,
                "query_result": results,
            }
        )

        try:
            response = self.llm.invoke(p)
        except Exception as e:
            print(f"Feedback Agent: LLM invoke failed : {e}")
            return None

        try:
            return json.loads(response.content)
        except Exception as e:
            print(f"JSON Parser failed : {e}")
            return None
