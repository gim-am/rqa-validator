import polars as pl
from polars import Expr, DataType


def create_column_difference_expression(column_1: str, column_2: str, dtype1: DataType, dtype2: DataType) -> Expr:
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
   
    
    def handle_nulls(expr_result: Expr, column_1_expr: Expr, column_2_expr: Expr):
        # If result is null (meaning one or both inputs were null)
        return pl.when(expr_result.is_null()) \
            .then((column_1_expr.is_null() != column_2_expr.is_null())) \
            .otherwise(expr_result)

    if dtype1.is_numeric() or dtype2.is_numeric():
        # Cast to Float64 to handle Int vs Float
        # Note: If one is string and not numeric, this cast might fail or return null.
        norm_c1 = pl.col(column_1).cast(pl.Float64)
        norm_c2 = pl.col(column_2).cast(pl.Float64)
        
        raw_diff = norm_c1 != norm_c2
        return handle_nulls(raw_diff, norm_c1, norm_c2)

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
        return handle_nulls(raw_diff, norm_c1, norm_c2)

    else:
        raw_diff = pl.col(column_1).cast(pl.Utf8) != pl.col(column_2).cast(pl.Utf8)
        return handle_nulls(raw_diff, pl.col(column_1), pl.col(column_2))