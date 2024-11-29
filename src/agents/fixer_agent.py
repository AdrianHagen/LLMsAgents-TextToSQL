import json

from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

from state_types import FixerResponse, State
import prompt_templates.fixer_agent as templates


class FixerAgent:

    def __init__(self, llm: BaseChatModel = None, template: str = None) -> None:

        if template is None:
            self.template = templates.ONE_SHOT
        else:
            self.template = template
        self.prompt = PromptTemplate.from_template(self.template)
        if llm is None:
            self.llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
        else:
            self.llm = llm

    def analyse_incorrect_query(self, state: State):
        original_question = state["original_question"]
        database = state["relevant_database"]
        error_message = state["errors"][-1]

        response = self._analyse_incorrect_query(
            original_question, database, error_message
        )

        if response is not None:
            state["feedbacks"].append(response)
        else:
            state["errors"].append("Feedback Failed")

    # TODO - Could include the original question
    def _analyse_incorrect_query(
        self, query: str, database: str, error_message: str
    ) -> FixerResponse | None:

        p = self.prompt.invoke(
            input={
                "query": query,
                "database": database,
                "error_message": error_message,
            }
        )

        response = self.llm.invoke(p).content
        response = response.replace("Output:", "").strip()

        try:
            return json.loads(response)
        except Exception as e:
            print(f"Fixer Agent: JSON Parser failed : {e}")
            return None
