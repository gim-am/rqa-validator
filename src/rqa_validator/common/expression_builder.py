import polars as pl
from polars import DataType, Expr


def normalise_list(items: list[str], dtype: DataType) -> list[str]:
    """converts a list of strings that are actually numeric types to floats.

    passing in datatype in case this needs to be expanded later.


    Args:
        items (list[str]): list of items to convert
        dtype (DataType): datatype to check against

    Returns:
        list[str]: returns the normalised list
    """
    if dtype.is_numeric():
        normalized: list[str] = []
        for item in items:
            try:
                val = float(item)
                normalized.append(str(val))
            except ValueError:
                normalized.append(item)
        return normalized

    return items


def create_column_difference_expression(
    column_1: str, column_2: str, data_type_1: DataType, data_type_2: DataType
) -> Expr:
    """Builds an expression that compares the values between two dataframe columns.

        If either of the columns is a numeric data type then a numeric comparison
        is made by converting both values to floats

        If either of the columns is a temporal data type then a temporal comparison
        is made by converting both to datetimes

        Else a string comparison is done

        If one of the values is null then a null comparison is made

    Args:
        column_1 (str): name of first column to compare
        column_2 (str): name of second column to compare
        data_type_1 (DataType): data type of first column
        data_type_2 (DataType): data type of second column
    """

    def normalize_to_null_if_empty(expression: Expr, data_type: DataType) -> Expr:
        """Convert empty strings to null for consistent comparison."""
        return (
            pl.when(data_type == pl.String)
            .then(pl.when(expression.str.strip_chars() == "").then(None).otherwise(expression))
            .otherwise(expression)
        )

    def handle_nulls_and_empty(
        expression_result: Expr, column_1_normalized: Expr, column_2_normalized: Expr
    ):
        """Handle null/empty string equivalence in comparison results.

        When expr_result is null (meaning at least one input was null/empty):
        - If both are null/empty → they are equal → return False (not different)
        - If only one is null/empty → they are different → return True
        """
        return (
            pl.when(expression_result.is_null())
            .then(
                pl.when(column_1_normalized.is_null() & column_2_normalized.is_null())
                .then(False)
                .otherwise(
                    pl.when(column_1_normalized.is_null() | column_2_normalized.is_null())
                    .then(True)
                    .otherwise(expression_result)
                )
            )
            .otherwise(expression_result)
        )

    if data_type_1.is_temporal() or data_type_2.is_temporal():
        # Normalize to Datetime
        # use the str.to_datetime logic here if strings are involved
        def to_dt(column_expr: Expr, column_dtype: DataType):
            if column_dtype.is_temporal():
                return column_expr.cast(pl.Datetime, strict=False)
            elif column_dtype == pl.String:
                return column_expr.str.to_datetime(strict=False)  # .cast(pl.Datetime, strict=False)
            else:
                # if a float (possibly utc) or other is returned
                return pl.lit(None).cast(pl.Datetime)

        column_1_normalised = to_dt(pl.col(column_1), data_type_1)
        column_2_normalised = to_dt(pl.col(column_2), data_type_2)

        # Check if both conversions were successful
        both_valid = ~column_1_normalised.is_null() & ~column_2_normalised.is_null()

        # Typed comparison
        temporal_diff = column_1_normalised != column_2_normalised

        # Fallback: String comparison for rows where date parsing failed
        column_1_str = pl.col(column_1).cast(pl.Utf8)
        column_2_str = pl.col(column_2).cast(pl.Utf8)
        str_diff = column_1_str != column_2_str

        # Combine logic
        raw_diff = pl.when(both_valid).then(temporal_diff).otherwise(str_diff)

        column_1_normalised_final = normalize_to_null_if_empty(pl.col(column_1), data_type_1).cast(
            pl.Utf8
        )
        column_2_normalised_final = normalize_to_null_if_empty(pl.col(column_2), data_type_2).cast(
            pl.Utf8
        )

        # Check if columns are effectively null

        column_1_null = pl.col(column_1).is_null() | (
            pl.col(column_1).cast(pl.Utf8).str.strip_chars() == ""
        )

        column_2_null = pl.col(column_2).is_null() | (
            pl.col(column_2).cast(pl.Utf8).str.strip_chars() == ""
        )

        final_result = (
            pl.when(column_1_null & column_2_null)
            .then(pl.lit(False))
            .when(column_1_null | column_2_null)
            .then(pl.lit(True))
            .otherwise(raw_diff)
        )

        return final_result

    elif data_type_1.is_numeric() or data_type_2.is_numeric():
        # Cast to Float64 to handle Int vs Float
        # Note: If one is string and not numeric, this cast might fail or return null.
        def cast_to_float(column: str, dtype: DataType):
            return (
                pl.when(dtype == pl.String)
                .then(
                    pl.when(pl.col(column).str.strip_chars() == "")
                    .then(None)
                    .otherwise(pl.col(column))
                    .cast(pl.Float64, strict=False)
                )
                .otherwise(pl.col(column).cast(pl.Float64, strict=False))
            )

        column_1_normalised = cast_to_float(column_1, data_type_1)
        column_2_normalised = cast_to_float(column_2, data_type_2)

        # Check if both conversions were successful
        both_numeric = ~column_1_normalised.is_null() & ~column_2_normalised.is_null()
        # Typed comparison (only valid if both are numbers)
        numeric_diff = column_1_normalised != column_2_normalised
        # Fallback: String comparison for rows where conversion failed
        column_1_str = pl.col(column_1).cast(pl.Utf8)
        column_2_str = pl.col(column_2).cast(pl.Utf8)
        str_diff = column_1_str != column_2_str

        raw_diff = pl.when(both_numeric).then(numeric_diff).otherwise(str_diff)
        # We pass the original columns (normalized for empty strings) to the null handler
        # to ensure empty strings are treated as nulls correctly
        column_1_normalised_final = normalize_to_null_if_empty(pl.col(column_1), data_type_1)
        column_2_normalised_final = normalize_to_null_if_empty(pl.col(column_2), data_type_2)

        return handle_nulls_and_empty(
            raw_diff, column_1_normalised_final, column_2_normalised_final
        )

    else:
        column_1_normalised = normalize_to_null_if_empty(pl.col(column_1), data_type_1)
        column_2_normalised = normalize_to_null_if_empty(pl.col(column_2), data_type_2)

        raw_diff = column_1_normalised.cast(pl.Utf8) != column_2_normalised.cast(pl.Utf8)
        return handle_nulls_and_empty(raw_diff, column_1_normalised, column_2_normalised)
