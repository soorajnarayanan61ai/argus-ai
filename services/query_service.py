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

        def normalize(text):
            return "".join(ch.lower() for ch in str(text) if ch.isalnum())

        def find_column():
            q_norm = normalize(q)

            matches = []
            for col in df.columns:
                col_norm = normalize(col)

                if col_norm and col_norm in q_norm:
                    matches.append((len(col_norm), col))

            if matches:
                matches.sort(reverse=True)
                return matches[0][1]

            return None

        # Total rows
        if any(x in q for x in [
            "how many rows",
            "total rows",
            "row count",
            "number of rows"
        ]):
            return f"The dataset contains {len(df):,} total rows."

        # Total columns
        if any(x in q for x in [
            "how many columns",
            "total columns",
            "column count",
            "number of columns"
        ]):
            return f"The dataset contains {len(df.columns):,} columns."

        # Missing values
        if "missing" in q or "null" in q:
            col = find_column()

            if col is not None:
                missing = int(df[col].isna().sum())
                return f"Column '{col}' contains {missing:,} missing values."

            missing = int(df.isna().sum().sum())
            return f"The dataset contains {missing:,} missing values."

        # Duplicate rows
        if "duplicate" in q:
            duplicates = int(df.duplicated().sum())
            return f"The dataset contains {duplicates:,} duplicate rows."

        col = find_column()

        # Column-specific analytics
        if col is not None:
            numeric_series = pd.to_numeric(df[col], errors="coerce")
            has_numeric = numeric_series.notna().any()

            if "average" in q or "mean" in q:
                if has_numeric:
                    value = numeric_series.mean()
                    return f"The average {col} is {value:,.2f}."

            if "median" in q:
                if has_numeric:
                    value = numeric_series.median()
                    return f"The median {col} is {value:,.2f}."

            if "sum" in q or "total" in q:
                if has_numeric:
                    value = numeric_series.sum()
                    return f"The total {col} is {value:,.2f}."

            if (
                "maximum" in q
                or "highest" in q
                or "max " in q
            ):
                if has_numeric:
                    value = numeric_series.max()
                    return f"The maximum {col} is {value:,.2f}."

            if (
                "minimum" in q
                or "lowest" in q
                or "min " in q
            ):
                if has_numeric:
                    value = numeric_series.min()
                    return f"The minimum {col} is {value:,.2f}."

            if "unique" in q or "distinct" in q:
                value = int(df[col].nunique(dropna=True))
                return f"Column '{col}' contains {value:,} unique values."

            if (
                "top" in q
                or "most common" in q
                or "highest frequency" in q
            ):
                counts = df[col].dropna().astype(str).value_counts()

                if not counts.empty:
                    top_value = counts.index[0]
                    top_count = int(counts.iloc[0])

                    return (
                        f"The most common value in '{col}' is "
                        f"'{top_value}' with {top_count:,} records."
                    )

            if "count" in q or "how many" in q:
                non_null = int(df[col].notna().sum())
                return (
                    f"Column '{col}' contains "
                    f"{non_null:,} non-missing records."
                )

        # Count a specific value anywhere in the dataset
        if "how many" in q or "count" in q:
            best_match = None

            for column in df.columns:
                series = df[column].dropna().astype(str)

                for value in series.unique():
                    value_text = str(value).strip()

                    if (
                        len(value_text) >= 2
                        and value_text.lower() in q
                    ):
                        count = int(
                            series.str.lower()
                            .eq(value_text.lower())
                            .sum()
                        )

                        if best_match is None or len(value_text) > len(best_match[0]):
                            best_match = (
                                value_text,
                                column,
                                count
                            )

            if best_match is not None:
                value_text, column, count = best_match

                return (
                    f"There are {count:,} records where "
                    f"'{column}' is '{value_text}'."
                )

        return (
            "I could not confidently calculate that question yet. "
            "Try asking about rows, columns, missing values, duplicates, "
            "average, median, sum, minimum, maximum, unique values, "
            "most common values, or counts for a specific column/value."
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
