import pandas as pd


def min_max_normalize(data: pd.DataFrame) -> pd.DataFrame:
    """Scale each numeric column into [0, 1] using min-max normalization.

    Non-numeric columns are preserved unchanged.
    Columns with constant values are mapped to 0.0.
    """
    normalized = data.copy()
    numeric_cols = normalized.select_dtypes(include=["number"]).columns

    for col in numeric_cols:
        col_min = normalized[col].min()
        col_max = normalized[col].max()
        denom = col_max - col_min
        if denom == 0:
            normalized[col] = 0.0
        else:
            normalized[col] = (normalized[col] - col_min) / denom

    return normalized
