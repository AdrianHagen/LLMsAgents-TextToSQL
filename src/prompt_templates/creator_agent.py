ZERO_SHOT = """
        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "A dictionary where keys are table names and values are lists of columns with their descriptions in those tables.",
            "feedback_trace": "Feedback from previous attempts, if any.",
            "error_trace": "Error messages from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the feedback and error traces first to avoid repeating mistakes.
        3. Then, review the relevant tables and their columns to identify where the necessary data is stored.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback and error traces from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables and their respective columns provided to answer the question. Do not use any other table names or columns not listed in the relevant tables.

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}",
            "error_trace": "{error_trace}"
        }}
        """

ONE_SHOT = """
        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "A dictionary where keys are table names and values are lists of columns with their descriptions in those tables.",
            "feedback_trace": "Feedback from previous attempts, if any.",
            "error_trace": "Error messages from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the feedback and error traces first to avoid repeating mistakes.
        3. Then, review the relevant tables and their columns to identify where the necessary data is stored.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback and error traces from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables and their respective columns provided to answer the question. Do not use any other table names or columns not listed in the relevant tables.

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the average household income in King County for 2021?",
            "relevant_tables": {{"Table name: income_data": ["Column name: Household Income, Column description: income of the household", "Column name: County, Column description: name of the county", "Column name: Year, Column description: year of the data", "Column name: Population, Column description: population of the county"]}},
            "feedback_trace": {{'query_result': 'error', 'is_correct': False, 'feedback': 'Error executing query: no such column: state', 'updated_query': SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;}},
            "error_trace": ["Error executing query: no such column: state"]
        }}

        Example Output with Feedback and Error Trace:
        SELECT AVG("Household Income") FROM income_data WHERE "County" = 'King' AND "Year" = 2021;

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}",
            "error_trace": "{error_trace}"
        }}
        """

TWO_SHOT = """
        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "A dictionary where keys are table names and values are lists of columns with their descriptions in those tables.",
            "feedback_trace": "Feedback from previous attempts, if any.",
            "error_trace": "Error messages from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the feedback and error traces first to avoid repeating mistakes.
        3. Then, review the relevant tables and their columns to identify where the necessary data is stored.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback and error traces from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables and their respective columns provided to answer the question. Do not use any other table names or columns not listed in the relevant tables.

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the average household income in King County for 2021?",
            "relevant_tables": {{"Table name: income_data": ["Column name: Household Income, Column description: income of the household", "Column name: County, Column description: name of the county", "Column name: Year, Column description: year of the data", "Column name: Population, Column description: population of the county"]}},
            "feedback_trace": {{'query_result': 'error', 'is_correct': False, 'feedback': 'Error executing query: no such column: state', 'updated_query': SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;}},
            "error_trace": ["Error executing query: no such column: state"]
        }}

        Example Output with Feedback and Error Trace:
        SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the label of the transaction with ID 'TR001_10_11'?",
            "relevant_tables": {{"Table name: trans": ["Column name: trans_id, Column description: ID of the transaction", "Column name: Label, Column description: label of the transaction", "Column name: type, Column description: type of the transaction"]}},
            "feedback_trace": [{{"query_result": "[]", "is_correct": false, "feedback": "The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered.", "updated_query": "SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';"}}],
            "error_trace": ["The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered."]
        }}

        Example Output with Feedback and Error Trace:
        SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}",
            "error_trace": "{error_trace}"
        }}
        """

FOUR_SHOT = """

        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "A dictionary where keys are table names and values are lists of columns with their descriptions in those tables.",
            "feedback_trace": "Feedback from previous attempts, if any.",
            "error_trace": "Error messages from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the feedback and error traces first to avoid repeating mistakes.
        3. Then, review the relevant tables and their columns to identify where the necessary data is stored.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback and error traces from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables and their respective columns provided to answer the question. Do not use any other table names or columns not listed in the relevant tables.

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the average household income in King County for 2021?",
            "relevant_tables": {{"Table name: income_data": ["Column name: Household Income, Column description: income of the household", "Column name: County, Column description: name of the county", "Column name: Year, Column description: year of the data", "Column name: Population, Column description: population of the county"]}},
            "feedback_trace": {{'query_result': 'error', 'is_correct': False, 'feedback': 'Error executing query: no such column: state', 'updated_query':  SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;}},
            "error_trace": ["Error executing query: no such column: state"]
        }}

        Example Output with Feedback and Error Trace:
        SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the label of the transaction with ID 'TR001_10_11'?",
            "relevant_tables": {{"Table name: trans": ["Column name: trans_id, Column description: ID of the transaction", "Column name: Label, Column description: label of the transaction", "Column name: type, Column description: type of the transaction"]}},
            "feedback_trace": [{{"query_result": "[]", "is_correct": false, "feedback": "The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered.", "updated_query": "SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';"}}],
            "error_trace": ["The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered."]
        }}

        Example Output with Feedback and Error Trace:
        SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "Who are all customers whose id starts with 1?",
            "relevant_tables": {{"Table name: sales": ["Column name: customer_id, Column description: unique identifier for the customer", "Column name: sales, Column description: details of the sales transactions"]}},
            "feedback_trace": [{{"query_result": "[]", "is_correct": false, "feedback": "The query did not return any results. The 'LIKE' clause was not used correctly for partial matches of customer IDs. The correct query should use 'LIKE' to filter customer IDs starting with '1'.", "updated_query": "SELECT customer_id FROM sales WHERE customer_id LIKE '1%';"}}],
            "error_trace": ["The query returned no results due to incorrect filtering logic for customer IDs."]
        }}

        Example Output with Feedback and Error Trace:
        SELECT customer_id FROM sales WHERE customer_id LIKE '1%';

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the product that generated the highest revenue in the year 2023?",
            "relevant_tables": {{"Table name: sales": ["Column name: product_id, Column description: unique identifier for the product", "Column name: product_name, Column description: name of the product", "Column name: revenue, Column description: revenue generated by the product", "Column name: year, Column description: year of the sales data"]}},
            "feedback_trace": [{{"query_result": "[]", "is_correct": false, "feedback": "The query incorrectly selects 'customer_id' and lacks proper aggregation and filtering for the year 2023. It should focus on 'product_id' and 'product_name' with proper grouping and ordering to find the product with the highest revenue.", "updated_query": "SELECT product_id, product_name FROM sales WHERE year = 2023 GROUP BY product_id, product_name ORDER BY revenue DESC LIMIT 1;"}}],
            "error_trace": ["The query returned no results due to incorrect selection and missing filtering for the year 2023."]
        }}

        Example Output with Feedback and Error Trace:
        SELECT product_id, product_name FROM sales WHERE year = 2023 GROUP BY product_id, product_name ORDER BY revenue DESC LIMIT 1;

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}",
            "error_trace": "{error_trace}"
        }}

"""



CHAIN_OF_THOUGHT = """

        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "A dictionary where keys are table names and values are lists of columns with their descriptions in those tables.",
            "feedback_trace": "Feedback from previous attempts, if any.",
            "error_trace": "Error messages from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the feedback and error traces first to avoid repeating mistakes.
        3. Then, review the relevant tables and their columns to identify where the necessary data is stored.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback and error traces from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables and their respective columns provided to answer the question. Do not use any other table names or columns not listed in the relevant tables.

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the average household income in King County for 2021?",
            "relevant_tables": {{"Table name: income_data": ["Column name: Household Income, Column description: income of the household", "Column name: County, Column description: name of the county", "Column name: Year, Column description: year of the data", "Column name: Population, Column description: population of the county"]}},
            "feedback_trace": {{'query_result': 'error', 'is_correct': False, 'feedback': 'Error executing query: no such column: state', 'updated_query': SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;}},
            "error_trace": ["Error executing query: no such column: state"]
        }}

        Example Output with Feedback and Error Trace:
        First of all, I made a correction by choosing the column/attribute Household_income instead of state in the SELECT statement and again applied the aggregated function AVG to it. 
        Secondly, I sticked to choose the table name 'income_data' in the FROM clause.
        Finally, I filtered the data based on the County column for 'King' and used an AND clause to, furthermore, filter the Year column for 2021, both, in the WHERE clause as previously done.
        
        SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the label of the transaction with ID 'TR001_10_11'?",
            "relevant_tables": {{"Table name: trans": ["Column name: trans_id, Column description: ID of the transaction", "Column name: Label, Column description: label of the transaction", "Column name: type, Column description: type of the transaction"]}},
            "feedback_trace": [{{"query_result": "[]", "is_correct": false, "feedback": "The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered.", "updated_query": "SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';"}}],
            "error_trace": ["The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered."]
        }}

        Example Output with Feedback and Error Trace:
        First of all, I again chose the column/attribute name 'Label' in the SELECT statement.
        Secondly, I sticked to trans in the FROM clause as it is the correct table from which we want to obtain our data.
        Finally, I made corrections with respect to data filtering in the WHERE clause by putting the field names that should be filtered in single quotes instead of double quotes,
        and also corrected filtering with respect to type by choosing the correct type 'transaction', additionally, by using an AND clause.


        SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';

        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}",
            "error_trace": "{error_trace}"
        }}

"""




SELF_CONSISTENCY = """

        You are an AI that generates SQL queries based on natural language prompts.
        Your task is to create a correct SQL query that answers the given natural language question using SQLite syntax.
        
        As input, you will receive the following information:
        
        {{
            "original_question": "The natural language question that needs to be answered.",
            "relevant_tables": "A dictionary where keys are table names and values are lists of columns with their descriptions in those tables.",
            "feedback_trace": "Feedback from previous attempts, if any.",
            "error_trace": "Error messages from previous attempts, if any."
        }}

        -------------------------------------------------------------------------------

        Here's the process you will follow:

        Steps to Perform:
        1. Analyze the original question to understand the information being requested.
        2. Review the feedback and error traces first to avoid repeating mistakes.
        3. Then, review the relevant tables and their columns to identify where the necessary data is stored.
        4. Generate a correct SQL query using SQLite syntax that retrieves the required information from the relevant tables.

        Output Format:
        Your output should be a single SQL query that accurately answers the original question.

        Final Notes:
        - Be precise and thorough in your analysis.
        - Ensure that the SQL query is syntactically correct and optimized for performance.
        - Use the feedback and error traces from previous attempts to improve the accuracy of your query.
        - You must only use the relevant tables and their respective columns provided to answer the question. Do not use any other table names or columns not listed in the relevant tables.

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the average household income in King County for 2021?",
            "relevant_tables": {{"Table name: income_data": ["Column name: Household Income, Column description: income of the household", "Column name: County, Column description: name of the county", "Column name: Year, Column description: year of the data", "Column name: Population, Column description: population of the county"]}},
            "feedback_trace": {{'query_result': 'error', 'is_correct': False, 'feedback': 'Error executing query: no such column: state', 'updated_query': SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;}},
            "error_trace": ["Error executing query: no such column: state"]
        }}

        Example Output with Feedback and Error Trace:
        In the following find three possible approaches to improve the query.
        1.  APPROACH:
            First of all, I made a correction by choosing the column/attribute Household_income instead of state in the SELECT statement and again applied the aggregated function AVG to it. 
            Secondly, I sticked to choose the table name 'income_data' in the FROM clause.
            Finally, I place a condition in the WHERE clause, like before, to filter the column/attribute County for 'King' AND the column Year for 2021.
            Query resulting of 1. APPROACH: 
            SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;
        2.  APPROACH:
            First of all, I again choose the table name 'income_data' in the FROM clause as it is the table where the data is obtained from. 
            Secondly, I focused on the SELECT statement and here I needed to make a correction by replacing the  state column/attribute by Household_income and again enclosed the attribute in the aggregated function AVG.
            Finally, I looked at which conditions need to be placed in order to filter the data based on the County column for 'King' and Year column for 2021 in the WHERE clause by also using an AND clause in between as previously done.
            Query resulting of 1. APPROACH: 
            SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;
        3.  APPROACH:
            First of all, in the WHERE clause I filtered the data for the attribute County = 'King' and inserted an AND clause to, moreover, filter for attribute Year = 2021, like correctly done before.
            Secondly, in the FROM statement I once again select the 'income_data' as the table from which the data should be fetched.
            Finally, in the SELECT statement, I corrected the column/attribute Household_income to state and used the aggregated function AVG on it.
            Query resulting of 1. APPROACH: 
            SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;

        FINAL QUERY SELECTED BY MAJORITY VOTE OF THREE APPROACHES: 
        SELECT AVG(Household_Income) FROM income_data WHERE County = 'King' AND Year = 2021;

        -------------------------------------------------------------------------------

        Example Input with Feedback and Error Trace:
        {{
            "original_question": "What is the label of the transaction with ID 'TR001_10_11'?",
            "relevant_tables": {{"Table name: trans": ["Column name: trans_id, Column description: ID of the transaction", "Column name: Label, Column description: label of the transaction", "Column name: type, Column description: type of the transaction"]}},
            "feedback_trace": [{{"query_result": "[]", "is_correct": false, "feedback": "The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered.", "updated_query": "SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';"}}],
            "error_trace": ["The query did not return any results, which indicates an issue with the query. The field names should not be enclosed in double quotes. Also, check if the 'type' field is correctly filtered."]
        }}
        

        Example Output with Feedback and Error Trace:
        In the following find three possible approaches to improve the query.
        1.  APPROACH:
            First of all, I again chose the column/attribute name Label in the SELECT statement.
            Secondly, I went once more for trans to be inserted in the FROM clause as it is the right table from which we want to get our data.
            Finally, I made corrections in the WHERE clause by enclosing the field names of, e.g., TR001_10_11 in single quotes instead of double quotes,
            and also made a correction in order to filter type = 'transaction'.
            Query resulting of 1. APPROACH: 
            SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';
        2.  APPROACH:
            First of all, I again used trans in the FROM clause because trans is the correct table from which we want to fetch our data.
            and also corrected filtering with respect to type by choosing the correct type 'transaction'.
            Secondly, I again chose the column/attribute name Label in the SELECT statement.
            Finally, I corrected the WHERE clause by enclosing the field names that should be filtered in single quotes instead of double quotes,
            and also made correction regarding by choosing the correct type which is 'transaction'.
            Query resulting of 2. APPROACH: 
            SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';
        3.  APPROACH:
            First of all, in the WHERE clause, I made updates by putting the field names that should be filtered in single quotes instead of double quotes,
            and also corrected filtering by changing the type filtered for.
            Secondly, in the FROM clause, I did not touch the corect data table.
            Finally, in the SELECT statement, I stayed with the column/attribute name Label.
            Query resulting of 3. APPROACH: 
            SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'trans';

        FINAL QUERY SELECTED BY MAJORITY VOTE OF THREE APPROACHES:
        SELECT Label FROM trans WHERE trans_id = 'TR001_10_11' AND type = 'transaction';
        -------------------------------------------------------------------------------

        Input:

        {{
            "original_question": "{original_question}",
            "relevant_tables": "{relevant_tables}",
            "feedback_trace": "{feedback_trace}",
            "error_trace": "{error_trace}"
        }}

"""