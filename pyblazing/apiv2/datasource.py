from enum import IntEnum

import cudf

from .bridge import internal_api

# TODO BIG TODO percy blazing-io didn't expose the wildcard API of FileSystem API


class Type(IntEnum):
    cudf = 0
    pandas = 1
    arrow = 2
    csv = 3
    parquet = 4
    result_set = 5
    distributed_result_set = 6


class DataSource:

    def __init__(self, client, type, **kwargs):
        self.client = client

        self.type = type

        #remove
        # declare all the possible fields (will be defined in _load)
        self.cudf_df = None  # cudf, pandas and arrow data will be passed/converted into this var
        self.csv = None
        self.parquet = None
        self.path = None

        # init the data source
        self.valid = self._load(type, **kwargs)

    def __repr__(self):
        return "TODO"

    def __str__(self):
        if self.valid == False:
            return 'Invalid datasource'

        type_str = {
            Type.cudf: 'cudf',
            Type.pandas: 'pandas',
            Type.arrow: 'arrow',
            Type.csv: 'csv',
            Type.parquet: 'parquet',
            Type.result_set: 'result_set'
        }

        # TODO percy path and stuff

        return type_str[self.type]

    #def is_valid(self):
    #    return self.valid

    # cudf.DataFrame in-gpu-memory
    def is_cudf(self):
        return self.type == Type.cudf

    # pandas.DataFrame in-memory
    def is_pandas(self):
        return self.type == Type.pandas

    # arrow file on filesystem or arrow in-memory
    def is_arrow(self):
        return self.type == Type.arrow

    # csv file on filesystem
    def is_csv(self):
        return self.type == Type.csv

    # parquet file on filesystem
    def is_parquet(self):
        return self.type == Type.parquet

    # blazing result set handle
    def is_result_set(self):
        return self.type == Type.result_set

    def is_distributed_result_set(self):
        return self.type == Type.distributed_result_set

    def is_from_file(self):
        return self.type == Type.parquet or self.type == Type.csv

    def dataframe(self):
        # TODO percy add more support

        if self.type == Type.cudf:
            return self.cudf_df
        elif self.type == Type.pandas:
            return self.cudf_df
        elif self.type == Type.arrow:
            return self.cudf_df
        elif self.type == Type.result_set:
            return self.cudf_df

        return None

    def schema(self):
        if self.type == Type.csv:
            return self.csv
        elif self.type == Type.parquet:
            return self.parquet
        elif self.type == Type.cudf:
            return self.cudf_df

        return None

# BEGIN remove
    def _load(self, type, **kwargs):
        table_name = kwargs.get('table_name', None)
        if type == Type.cudf:
            cudf_df = kwargs.get('cudf_df', None)
            return self._load_cudf_df(table_name, cudf_df)
        elif type == Type.pandas:
            pandas_df = kwargs.get('pandas_df', None)
            return self._load_pandas_df(table_name, pandas_df)
        elif type == Type.arrow:
            arrow_table = kwargs.get('arrow_table', None)
            return self._load_arrow_table(table_name, arrow_table)
        elif type == Type.result_set:
            result_set = kwargs.get('result_set', None)
            return self._load_result_set(table_name, result_set)
        elif type == Type.distributed_result_set:
            result_set = kwargs.get('result_set', None)
            return self._load_distributed_result_set(table_name, result_set)
        elif type == Type.csv:
            path = kwargs.get('path', None)
            csv_column_names = kwargs.get('csv_column_names', [])
            csv_column_types = kwargs.get('csv_column_types', [])
            csv_delimiter = kwargs.get('csv_delimiter')
            csv_lineterminator = kwargs.get('csv_lineterminator')
            csv_skiprows = kwargs.get('csv_skiprows')
            csv_header = kwargs.get('csv_header')
            csv_nrows = kwargs.get('csv_nrows')
            csv_skipinitialspace = kwargs.get('csv_skipinitialspace')
            csv_delim_whitespace = kwargs.get('csv_delim_whitespace')
            csv_skip_blank_lines = kwargs.get('csv_skip_blank_lines')
            csv_quotechar = kwargs.get('csv_quotechar')
            csv_quoting = kwargs.get('csv_quoting')
            csv_doublequote = kwargs.get('csv_doublequote')
            csv_decimal = kwargs.get('csv_decimal')
            csv_skipfooter = kwargs.get('csv_skipfooter')
            csv_na_filter = kwargs.get('csv_na_filter')
            csv_keep_default_na = kwargs.get('csv_keep_default_na')
            csv_dayfirst = kwargs.get('csv_dayfirst')
            csv_thousands = kwargs.get('csv_thousands')
            csv_comment = kwargs.get('csv_comment')
            csv_true_values = kwargs.get('csv_true_values')
            csv_false_values = kwargs.get('csv_false_values')
            csv_na_values = kwargs.get('csv_na_values')

            return self._load_csv(table_name, path,
                csv_column_names,
                csv_column_types,
                csv_delimiter,
                csv_skiprows,
                csv_lineterminator,
                csv_header,
                csv_nrows,
                csv_skipinitialspace,
                csv_delim_whitespace,
                csv_skip_blank_lines,
                csv_quotechar,
                csv_quoting,
                csv_doublequote,
                csv_decimal,
                csv_skipfooter,
                csv_na_filter,
                csv_keep_default_na,
                csv_dayfirst,
                csv_thousands,
                csv_comment,
                csv_true_values,
                csv_false_values,
                csv_na_values)

        elif type == Type.parquet:
            table_name = kwargs.get('table_name', None)
            path = kwargs.get('path', None)
            return self._load_parquet(table_name, path)
        else:
            # TODO percy manage errors
            raise Exception("invalid datasource type")

        # TODO percy compare against bz proto Status_Success or Status_Error
        # here we need to use low level api pyblazing.create_table
        return False

    def _load_cudf_df(self, table_name, cudf_df):
        self.cudf_df = cudf_df

        column_names = list(cudf_df.dtypes.index)
        column_dtypes = [internal_api.get_np_dtype_to_gdf_dtype(x) for x in cudf_df.dtypes]
        return_result = internal_api.create_table(
            self.client,
            table_name,
            type = internal_api.SchemaFrom.Gdf,
            names = column_names,
            dtypes = column_dtypes,
            gdf = cudf_df
        )

        # TODO percy see if we need to perform sanity check for cudf_df object
        self.valid = True

        return self.valid

    def _load_pandas_df(self, table_name, pandas_df):
        cudf_df = cudf.DataFrame.from_pandas(pandas_df)

        return self._load_cudf_df(table_name, cudf_df)

    def _load_arrow_table(self, table_name, arrow_table):
        pandas_df = arrow_table.to_pandas()

        return self._load_pandas_df(table_name, pandas_df)

    def _load_result_set(self, table_name, result_set):
        cudf_df = result_set.columns

        return self._load_cudf_df(table_name, cudf_df)

    def _load_distributed_result_set(self, table_name, distributed_result_set):
        print(distributed_result_set)
        internal_api.create_table(
            self.client,
            table_name,
            type = internal_api.SchemaFrom.Distributed,
            resultToken = distributed_result_set[0].resultToken
        )

        self.valid = True

        return self.valid


    def _load_csv(self, table_name, path, column_names, column_types, delimiter, skiprows, lineterminator, header, nrows, skipinitialspace, delim_whitespace,
        skip_blank_lines, quotechar, quoting, doublequote, decimal, skipfooter, na_filter, keep_default_na, dayfirst, thousands, comment, true_values,
        false_values, na_values):
        # TODO percy manage datasource load errors
        if path == None:
            return False

        self.path = path

        return_result = internal_api.create_table(
            self.client,
            table_name,
            type = internal_api.SchemaFrom.CsvFile,
            path = path,
            delimiter = delimiter,
            names = column_names,
            dtypes = internal_api.get_dtype_values(column_types),
            skiprows = skiprows,
            lineterminator = lineterminator,
            header = header,
            nrows = nrows,
            skipinitialspace = skipinitialspace,
            delim_whitespace = delim_whitespace,
            skip_blank_lines = skip_blank_lines,
            quotechar = quotechar,
            quoting = quoting,
            doublequote = doublequote,
            decimal = decimal,
            skipfooter = skipfooter,
            na_filter = na_filter,
            keep_default_na = keep_default_na,
            dayfirst = dayfirst,
            thousands = thousands,
            comment = comment,
            true_values = true_values,
            false_values = false_values,
            na_values = na_values
        )

        # TODO percy see if we need to perform sanity check for arrow_table object
        #return success or failed
        self.valid = return_result

        return self.valid

    def _load_parquet(self, table_name, path):
        # TODO percy manage datasource load errors
        if path == None:
            return False

        self.path = path

        return_result = internal_api.create_table(
            self.client,
            table_name,
            type = internal_api.SchemaFrom.ParquetFile,
            path = path
        )

        # TODO percy see if we need to perform sanity check for arrow_table object
        #return success or failed
        self.valid = return_result

        return self.valid
#END remove

# BEGIN DataSource builders


def from_cudf(cudf_df, table_name):
    return DataSource(None, Type.cudf, table_name = table_name, cudf_df = cudf_df)


def from_pandas(pandas_df, table_name):
    return DataSource(None, Type.pandas, table_name = table_name, pandas_df = pandas_df)


def from_arrow(arrow_table, table_name):
    return DataSource(None, Type.arrow, table_name = table_name, arrow_table = arrow_table)

def from_result_set(result_set, table_name):
    return DataSource(None, Type.result_set, table_name = table_name, result_set = result_set)

def from_distributed_result_set(result_set, table_name):
    return DataSource(None, Type.distributed_result_set, table_name = table_name, result_set = result_set)


def from_csv(client, table_name, path, column_names, column_types, delimiter, skiprows, lineterminator, header, nrows, skipinitialspace, delim_whitespace,
    skip_blank_lines, quotechar, quoting, doublequote, decimal, skipfooter, na_filter, keep_default_na, dayfirst, thousands, comment, true_values, false_values,
    na_values):
    return DataSource(client, Type.csv,
        table_name = table_name,
        path = path,
        csv_column_names = column_names,
        csv_column_types = column_types,
        csv_delimiter = delimiter,
        csv_skiprows = skiprows,
        csv_lineterminator = lineterminator,
        csv_header = header,
        csv_nrows = nrows,
        csv_skipinitialspace = skipinitialspace,
        csv_delim_whitespace = delim_whitespace,
        csv_skip_blank_lines = skip_blank_lines,
        csv_quotechar = quotechar,
        csv_quoting = quoting,
        csv_doublequote = doublequote,
        csv_decimal = decimal,
        csv_skipfooter = skipfooter,
        csv_na_filter = na_filter,
        csv_keep_default_na = keep_default_na,
        csv_dayfirst = dayfirst,
        csv_thousands = thousands,
        csv_comment = comment,
        csv_true_values = true_values,
        csv_false_values = false_values,
        csv_na_values = na_values
    )


# TODO percy path (with wildcard support) is file system transparent
def from_parquet(client, table_name, path):
    return DataSource(client, Type.parquet, table_name = table_name, path = path)

# END DataSource builders
