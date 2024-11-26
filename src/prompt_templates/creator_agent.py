ZERO_SHOT = """
        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "The tables that are relevant to the question.",
            "feedback_trace": "Feedback from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the relevant tables to identify where the necessary data is stored.
        3. Consider any feedback to avoid repeating mistakes.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables provided to answer the question. Do not use any other table names. Using any table not listed in the relevant tables is not allowed.

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}"
        }}
        """

ONE_SHOT = """
        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "The tables that are relevant to the question.",
            "feedback_trace": "Feedback from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the relevant tables to identify where the necessary data is stored.
        3. Consider any feedback to avoid repeating mistakes.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables provided to answer the question. Do not use any other table names. Using any table not listed in the relevant tables is not allowed.

        -------------------------------------------------------------------------------

        Example Input with empty Feedback:
        {{
            "original_question": "What is the total revenue generated in 2023?",
            "relevant_tables": ["sales"],
            "feedback_trace": []
        }}

        Example Output with empty Feedback:
        SELECT SUM(revenue) FROM sales WHERE year = 2023;

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}"
        }}
        """

TWO_SHOT = """
        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "The tables that are relevant to the question.",
            "feedback_trace": "Feedback from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the relevant tables to identify where the necessary data is stored.
        3. Consider any feedback to avoid repeating mistakes.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables provided to answer the question. Do not use any other table names. Using any table not listed in the relevant tables is not allowed.

        -------------------------------------------------------------------------------

        Example Input with empty Feedback:
        {{
            "original_question": "What is the total revenue generated in 2023?",
            "relevant_tables": ["sales"],
            "feedback_trace": []
        }}

        Example Output with empty Feedback:
        SELECT SUM(revenue) FROM sales WHERE year = 2023;

        -------------------------------------------------------------------------------

        Example Input with Feedback:
        {{
            "original_question": "What is the average household income in King County for 2021?",
            "relevant_tables": ["income_data"],
            "feedback_trace": {{'query_result': 'error', 'is_correct': False, 'feedback': 'Error executing query: near "Output": syntax error', 'updated_query': None}}
        }}

        Example Output with Feedback:
        SELECT AVG(`Household Income`) FROM income_data WHERE `County` = 'King' AND `Year` = 2021;

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}"
        }}
        """
