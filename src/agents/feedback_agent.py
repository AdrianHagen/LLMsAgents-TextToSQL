import json

from langchain.prompts import PromptTemplate
#from langchain_anthropic import ChatAnthropic
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
import tiktoken

from state_types import FeedbackResponse, State
from tools.database import Database
import prompt_templates.feedback_agent as templates



def truncate_results_by_tokens_or_count(results, token_model="gpt-4", token_limit=5000, max_results=20):
    # Initialize tokenizer for the specified model
    tokenizer = tiktoken.encoding_for_model(token_model)
    
    # Ensure results do not exceed the maximum count of 20
    if len(results) > max_results:
        midpoint = max_results // 2
        results = results[:midpoint] + [["..."]] + results[-midpoint:]
    
    # Convert results to JSON string
    results_str = json.dumps(results)
    
    # Tokenize the full string
    tokens = tokenizer.encode(results_str)
    total_tokens = len(tokens)
    
    while total_tokens > token_limit:
        # Dynamically reduce the number of results while keeping the middle truncation
        count = len(results)
        if count <= 3:  # Prevent reducing too much (1 on each side + '...')
            # Truncate tokens directly to fit the token limit
            truncated_tokens = tokens[:token_limit]
            results_str = tokenizer.decode(truncated_tokens) + " ... "
            break
        
        # Reduce results further
        midpoint = count // 2
        results = results[:midpoint] + [["..."]] + results[-midpoint:]
        
        # Regenerate the string and re-tokenize
        results_str = json.dumps(results)
        tokens = tokenizer.encode(results_str)
        total_tokens = len(tokens)
    
    return json.dumps(results_str)

class FeedbackAgent:

    def __init__(self, llm: BaseChatModel = None, template: str = None) -> None:

        if template is None:
            self.template = templates.TWO_SHOT
        else:
            self.template = template
        self.prompt = PromptTemplate.from_template(self.template)
        if llm is None:
            proxy_client = get_proxy_client('gen-ai-hub')
            self.llm = ChatOpenAI(proxy_model_name="gpt-3.5-turbo", proxy_client=proxy_client)
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
        self, original_question: str, database: str, generated_sql_query: str, max_tokens: int = 5000, token_model: str = "gpt-4"
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
        
        results_str = truncate_results_by_tokens_or_count(results, token_limit=max_tokens, token_model=token_model)
        p = self.prompt.invoke(
            input={
                "original_question": original_question,
                "database": database,
                "generated_sql_query": generated_sql_query,
                "query_result": json.dumps(results_str),
            }
        )
        print(p)

        try:
            response = self.llm.invoke(p)
        except Exception as e:
            print(f"Feedback Agent: LLM invoke failed : {e}")
            return None

        try:
            content = response.content.replace("```json\n", "").replace("```", "")
            return json.loads(content)
        except Exception as e:
            print(content)
            print(f"JSON Parser failed : {e}")
            return None
