class SQLFixerAgent:
    def __init__(self):
        pass

    def fix_sql_query(self, incorrect_query, error_message) -> str:
        """
        Fixes the syntactically incorrect SQL query based on the error message provided.

        Args:
            incorrect_query (str): The syntactically incorrect SQL query.
            error_message (str): The error message describing the syntax issue.

        Returns:
            str: The corrected SQL query.
        """
        corrected_query = incorrect_query  # Start with the provided query
        
        # Analyze the error message and apply corrections
        if "syntax error near" in error_message or "unexpected" in error_message:
            if ";" not in incorrect_query.strip():  # Add missing semicolon
                corrected_query += ";"
            if "WHERE" in incorrect_query and "AND" in error_message:  # Check for logical issues
                corrected_query = corrected_query.replace("WHERE AND", "WHERE")
        elif "missing keyword" in error_message:
            if "SELECT" not in incorrect_query:
                corrected_query = "SELECT * " + corrected_query
            if "FROM" not in incorrect_query:
                corrected_query = corrected_query.replace("SELECT", "SELECT * FROM")
        elif "unknown column" in error_message:
            # Handle unknown columns by suggesting correction (in real scenario, you'd infer or ask for clarification)
            corrected_query = corrected_query.replace("unknown_column", "valid_column")
        else:
            # Handle generic cases (e.g., duplicate keywords, unmatched parentheses, etc.)
            corrected_query = corrected_query.replace("  ", " ").strip()  # Clean extra spaces
            if corrected_query.count("(") != corrected_query.count(")"):
                corrected_query += ")"  # Attempt to balance parentheses

        return corrected_query

# Example usage
sql_fixer = SQLFixerAgent()

incorrect_query = "SELECT name, age FROM users WHERE AND age > 30"
error_message = "syntax error near 'AND'"

corrected_query = sql_fixer.fix_sql_query(incorrect_query, error_message)
print("Corrected Query:", corrected_query)
