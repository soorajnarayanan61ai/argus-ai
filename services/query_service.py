import pandas as pd


class QueryService:
    """Simple natural-language query service for the active dataset."""

    @staticmethod
    def answer_question(df: pd.DataFrame, question: str) -> str:
        if df is None or df.empty:
            return "No active dataset is available."

        if not question or not question.strip():
            return "Please enter a question about the dataset."

        q = question.lower().strip()

        # Total rows
        if (
            "how many rows" in q
            or "total rows" in q
            or "row count" in q
            or "number of rows" in q
        ):
            return f"The dataset contains {len(df):,} total rows."

        # Total columns
        if (
            "how many columns" in q
            or "total columns" in q
            or "column count" in q
            or "number of columns" in q
        ):
            return f"The dataset contains {len(df.columns):,} columns."

        # Missing values
        if "missing" in q or "null" in q:
            missing = int(df.isna().sum().sum())
            return f"The dataset contains {missing:,} missing values."

        # Duplicate rows
        if "duplicate" in q:
            duplicates = int(df.duplicated().sum())
            return f"The dataset contains {duplicates:,} duplicate rows."

        return (
            "I could not understand that question yet. "
            "Try asking about total rows, total columns, missing values, "
            "or duplicate rows."
        )
    def process_query(self, df: pd.DataFrame, query: str) -> dict:
            """Compatibility wrapper used by the Profiling UI."""
            answer = self.answer_question(df, query)
    
            return {
                "answer": answer,
                "evidence": f"Calculated directly from the active dataset ({len(df):,} rows).",
                "table": None,
                "chart": None,
            }
