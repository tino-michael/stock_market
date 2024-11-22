import polars as pl

(
    pl.Config
    .set_tbl_rows(50)
    .set_float_precision(0)
    .set_tbl_cell_numeric_alignment("RIGHT")
    .set_tbl_hide_column_data_types(True)
    .set_tbl_hide_dataframe_shape(True)
)
