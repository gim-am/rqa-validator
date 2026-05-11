import polars as pl
from polars import DataType, Expr


def create_column_difference_expression(
    column_1: str, column_2: str, dtype1: DataType, dtype2: DataType
) -> Expr:
    """Builds an expression that compares the values between two dataframe columns.

        If either of the columns is a numeric data type then a numeric comparison is made
        by converting both values to floats

        If either of the columns is a temporal data type then a temporal comparison is made
        by converting both to datetimes

        Else a string comparison is done

        If one of the values is null then a null comparison is made

    Args:
        column_1 (str): name of first column to compare
        column_2 (str): name of second column to compare
        dtype1 (DataType): data type of first column
        dtype2 (DataType): data type of second column
    """

    def normalize_to_null_if_empty(expr: Expr, dtype: DataType) -> Expr:
        """Convert empty strings to null for consistent comparison."""
        return (
            pl.when(dtype == pl.String)
            .then(pl.when(expr.str.strip_chars() == "").then(None).otherwise(expr))
            .otherwise(expr)
        )

    def handle_nulls_and_empty(
        expr_result: Expr, col1_normalized: Expr, col2_normalized: Expr
    ):
        """Handle null/empty string equivalence in comparison results.

        When expr_result is null (meaning at least one input was null/empty):
        - If BOTH are null/empty → they are equal → return False (not different)
        - If ONLY ONE is null/empty → they are different → return True
        """
        return (
            pl.when(expr_result.is_null())
            .then(
                pl.when(col1_normalized.is_null() & col2_normalized.is_null())
                .then(False)
                .otherwise(
                    pl.when(col1_normalized.is_null() | col2_normalized.is_null())
                    .then(True)
                    .otherwise(expr_result)
                )
            )
            .otherwise(expr_result)
        )

    if dtype1.is_numeric() or dtype2.is_numeric():
        # Cast to Float64 to handle Int vs Float
        # Note: If one is string and not numeric, this cast might fail or return null.
        norm_c1 = (
            pl.when(dtype1 == pl.String)
            .then(
                pl.when(pl.col(column_1).str.strip_chars() == "")
                .then(None)
                .otherwise(pl.col(column_1))
                .cast(pl.Float64)
            )
            .otherwise(pl.col(column_1).cast(pl.Float64))
        )

        norm_c2 = (
            pl.when(dtype2 == pl.String)
            .then(
                pl.when(pl.col(column_2).str.strip_chars() == "")
                .then(None)
                .otherwise(pl.col(column_2))
                .cast(pl.Float64)
            )
            .otherwise(pl.col(column_2).cast(pl.Float64))
        )

        raw_diff = norm_c1 != norm_c2
        return handle_nulls_and_empty(raw_diff, norm_c1, norm_c2)

    elif dtype1.is_temporal() or dtype2.is_temporal():
        # Normalize to Datetime
        # use the str.to_datetime logic here if strings are involved
        def to_dt(column_expr: Expr, column_dtype: DataType):
            if column_dtype.is_temporal():
                return column_expr.cast(pl.Datetime)
            else:
                return column_expr.str.to_datetime(strict=False)

        norm_c1 = to_dt(pl.col(column_1), dtype1)
        norm_c2 = to_dt(pl.col(column_2), dtype2)

        raw_diff = norm_c1 != norm_c2
        return handle_nulls_and_empty(raw_diff, norm_c1, norm_c2)

    else:
        norm_c1 = normalize_to_null_if_empty(pl.col(column_1), dtype1)
        norm_c2 = normalize_to_null_if_empty(pl.col(column_2), dtype2)

        raw_diff = norm_c1.cast(pl.Utf8) != norm_c2.cast(pl.Utf8)
        return handle_nulls_and_empty(raw_diff, norm_c1, norm_c2)
