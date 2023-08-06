import os
import glob
import pandas as pd
from datetime import datetime
from nemosis import filters, downloader, \
    processing_info_maps, defaults, custom_tables


def dynamic_data_compiler(start_time, end_time, table_name, raw_data_location,
                          select_columns=None, filter_cols=None,
                          filter_values=None, fformat='feather',
                          keep_csv=True, data_merge=True, **kwargs):
    """
    Downloads and compiles data for all dynamic tables.
    Refer to README for tables
    Args:
        start_time (str): format 'yyyy/mm/dd HH:MM:SS'
        end_time (str): format 'yyyy/mm/dd HH:MM:SS'
        table_name (str): table as per documentation
        raw_data_location (str): directory to download and cache data to.
                                 existing data will be used if in this dir.
        select_columns (list): return select columns
        filter_cols (list): filter on columns
        filter_values (list): filter index n filter col such that values are
                              equal to index n filter value
        fformat (string): "csv", "feather" or "parquet" for storage and access
        keep_csv (bool): retains CSVs in cache
        data_merge (bool): concatenate DataFrames.
        **kwargs: additional arguments passed to the pd.to_{fformat}() function

    Returns:
        all_data (pd.Dataframe): All data concatenated.
    """

    print('Compiling data for table {}.'.format(table_name))
    # Generic setup common to all tables.
    if select_columns is None:
        select_columns = defaults.table_columns[table_name]

    # Pre loop setup, done at table type basis.
    date_filter = processing_info_maps.filter[table_name]
    setup_function = processing_info_maps.setup[table_name]
    if setup_function is not None:
        start_time, end_time = setup_function(start_time, end_time)

    search_type = processing_info_maps.search_type[table_name]

    if search_type == 'all':
        start_search = defaults.nem_data_model_start_time
    elif search_type == 'start_to_end':
        start_search = start_time
    elif search_type == 'end':
        start_search = end_time

    start_time = datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S')
    start_search = datetime.strptime(start_search, '%Y/%m/%d %H:%M:%S')

    data_tables = dynamic_data_fetch_loop(start_search, start_time, end_time,
                                          table_name, raw_data_location,
                                          select_columns, date_filter,
                                          search_type, fformat=fformat,
                                          keep_csv=keep_csv,
                                          data_merge=data_merge,
                                          write_kwargs=kwargs)

    if data_merge:
        all_data = pd.concat(data_tables, sort=False)

        finalise_data = processing_info_maps.finalise[table_name]
        if finalise_data is not None:
            for function in finalise_data:
                all_data = function(all_data, start_time, table_name)

        if filter_cols is not None:
            all_data = filters.filter_on_column_value(all_data, filter_cols,
                                                      filter_values)

        return all_data


def dynamic_data_fetch_loop(start_search, start_time, end_time, table_name,
                            raw_data_location, select_columns,
                            date_filter, search_type, fformat='feather',
                            keep_csv=True, data_merge=True, write_kwargs={}):
    data_tables = []
    read_function = {'feather': pd.read_feather,
                     'csv': pd.read_csv,
                     'parquet': pd.read_parquet}
    table_type = defaults.table_types[table_name]
    date_gen = processing_info_maps.date_gen[table_type](start_search,
                                                         end_time)

    for year, month, day, index in date_gen:
        data = None
        # Write the file names and paths
        # for where the data is stored in the cache.
        filename_stub, path_and_name = \
            processing_info_maps.write_filename[table_type](table_name, month,
                                                            year, day, index,
                                                            raw_data_location)
        full_filename = path_and_name + f'.{fformat}'

        # If the data needed is not in the cache then download it.
        if not glob.glob(full_filename):
            if day is None:
                print(f'Downloading data for table {table_name}, '
                      + f'year {year}, month {month}')
            else:
                print(f'Downloading data for table {table_name}, '
                      + f'year {year}, month {month}, day {day},'
                      + f'time {index}.')

            processing_info_maps.downloader[table_type](year, month, day,
                                                        index, filename_stub,
                                                        raw_data_location)

        # If the data exists in the desired format, read it in
        # If it does not, then read in from the csv and save to desired format
        if glob.glob(full_filename) and fformat != 'csv':
            data = read_function[fformat](full_filename,
                                          columns=select_columns)
        elif not glob.glob(path_and_name + '.[cC][sS][vV]'):
            continue
        else:
            csv_file = glob.glob(path_and_name + '.[cC][sS][vV]')[0]
            if day is None:
                print(f'Creating {fformat} file for '
                      + f'{table_name}, {year}, {month}.')
            else:
                print(f'Creating {fformat} file for '
                      + f'{table_name}, {year}, {month}, {day}, {index}.')
            # Check what headers the data has.
            if defaults.table_types[table_name] == 'MMS':
                headers = read_function['csv'](csv_file,
                                               skiprows=[0],
                                               nrows=1).columns.tolist()
                # Remove columns from the table column list
                # if they are not in the header, this deals with the fact
                # AEMO has added and removed columns over time.
                columns = [column for column in
                           defaults.table_columns[table_name]
                           if column in headers]
                data = read_function['csv'](csv_file, skiprows=[0],
                                            usecols=columns, dtype=str)
                data = data[:-1]
            else:
                columns = defaults.table_columns[table_name]
                data = read_function['csv'](csv_file, skiprows=[0],
                                            names=columns, dtype=str)

            # Remove files of the same name
            # Deals with case of corrupted files.
            if os.path.isfile(full_filename) and fformat != 'csv':
                os.unlink(full_filename)

            # Write to required format
            to_function = {'feather': data.to_feather,
                           'parquet': data.to_parquet}

            if fformat == 'feather':
                to_function[fformat](full_filename, **write_kwargs)
            elif fformat == 'parquet':
                to_function[fformat](full_filename, index=False,
                                     **write_kwargs)

            if not keep_csv:
                os.remove(csv_file)

            # Delete any columns in data that were not explicitly selected.
            if select_columns is not None:
                for column in columns:
                    if column not in select_columns:
                        del data[column]

        if data is not None:
            # Filter by the start and end time.
            if date_filter is not None:
                data = date_filter(data, start_time, end_time)
            if data_merge:
                data_tables.append(data)

    return data_tables


def static_table_wrapper_for_gui(start_time, end_time, table_name,
                                 raw_data_location, select_columns=None,
                                 filter_cols=None, filter_values=None):
    table = static_table(table_name, raw_data_location, select_columns, filter_cols, filter_values)
    return table


def static_table(table_name, raw_data_location, select_columns=None, filter_cols=None, filter_values=None):
    print('Retrieving static table {}.'.format(table_name))
    path_and_name = raw_data_location + '/' + defaults.names[table_name]
    if not os.path.isfile(path_and_name):
        print('Downloading data for table {}.'.format(table_name))
        downloader.download_csv(defaults.static_table_url[table_name],
                                raw_data_location, path_and_name)

    table = pd.read_csv(raw_data_location + '/' + defaults.names[table_name],
                        dtype=str,
                        names=defaults.table_columns[table_name])
    if select_columns is not None:
        table = table.loc[:, select_columns]
    for column in table.select_dtypes(['object']).columns:
        table[column] = table[column].map(lambda x: x.strip())

    if filter_cols is not None:
        table = filters.filter_on_column_value(table, filter_cols,
                                               filter_values)

    return table


def static_table_FCAS_elements_file_wrapper_for_gui(start_time, end_time, table_name,
                                 raw_data_location, select_columns=None,
                                 filter_cols=None, filter_values=None):
    table = static_table_FCAS_elements_file(table_name, raw_data_location, select_columns, filter_cols, filter_values)
    return table


def static_table_FCAS_elements_file(table_name, raw_data_location, select_columns=None, filter_cols=None,
                                    filter_values=None):
    print('Retrieving static table {}.'.format(table_name))
    path_and_name = raw_data_location + '/' + defaults.names[table_name]
    if not os.path.isfile(path_and_name):
        print('Downloading data for table {}.'.format(table_name))
        downloader.download_elements_file(defaults.static_table_url[table_name],
                                raw_data_location, path_and_name)

    table = pd.read_csv(raw_data_location + '/' + defaults.names[table_name],
                        dtype=str,
                        names=defaults.table_columns[table_name])
    if select_columns is not None:
        table = table.loc[:, select_columns]
    for column in table.select_dtypes(['object']).columns:
        table[column] = table[column].map(lambda x: x.strip())

    if filter_cols is not None:
        table = filters.filter_on_column_value(table, filter_cols,
                                               filter_values)

    return table


def static_table_xl_wrapper_for_gui(start_time, end_time, table_name,
                                    raw_data_location, select_columns=None,
                                    filter_cols=None, filter_values=None):
    table = static_table_xl(table_name, raw_data_location, select_columns, filter_cols, filter_values)
    return table


def static_table_xl(table_name, raw_data_location, select_columns=None, filter_cols=None, filter_values=None):
    path_and_name = (raw_data_location + '/'
                     + defaults.names[table_name] + '.xls')
    print('Retrieving static table {}.'.format(table_name))
    if not os.path.isfile(path_and_name):
        print('Downloading data for table {}.'.format(table_name))
        downloader.download_xl(defaults.static_table_url[table_name],
                               raw_data_location, path_and_name)
    xls = pd.ExcelFile(path_and_name)
    table = pd.read_excel(xls, defaults.reg_exemption_list_tabs[table_name], dtype=str)
    if select_columns is not None:
        table = table.loc[:, select_columns]
    if filter_cols is not None:
        table = filters.filter_on_column_value(table, filter_cols,
                                               filter_values)
    if table_name in defaults.table_primary_keys.keys():
        primary_keys = defaults.table_primary_keys[table_name]
        table = table.drop_duplicates(primary_keys)

    table.dropna(axis=0, how='all', inplace=True)
    table.dropna(axis=1, how='all', inplace=True)

    return table


method_map = {'DISPATCHLOAD': dynamic_data_compiler,
              'DISPATCHPRICE': dynamic_data_compiler,
              'TRADINGLOAD': dynamic_data_compiler,
              'TRADINGPRICE': dynamic_data_compiler,
              'TRADINGREGIONSUM': dynamic_data_compiler,
              'TRADINGINTERCONNECT': dynamic_data_compiler,
              'DISPATCH_UNIT_SCADA': dynamic_data_compiler,
              'DISPATCHCONSTRAINT': dynamic_data_compiler,
              'DUDETAILSUMMARY': dynamic_data_compiler,
              'DUDETAIL': dynamic_data_compiler,
              'GENCONDATA': dynamic_data_compiler,
              'SPDREGIONCONSTRAINT': dynamic_data_compiler,
              'SPDCONNECTIONPOINTCONSTRAINT': dynamic_data_compiler,
              'SPDINTERCONNECTORCONSTRAINT': dynamic_data_compiler,
              'FCAS_4_SECOND': dynamic_data_compiler,
              'ELEMENTS_FCAS_4_SECOND': static_table_FCAS_elements_file_wrapper_for_gui,
              'VARIABLES_FCAS_4_SECOND': static_table_wrapper_for_gui,
              'Generators and Scheduled Loads': static_table_xl_wrapper_for_gui,
              'FCAS Providers': static_table_xl_wrapper_for_gui,
              'BIDDAYOFFER_D': dynamic_data_compiler,
              'BIDPEROFFER_D': dynamic_data_compiler,
              'FCAS_4s_SCADA_MAP': custom_tables.fcas4s_scada_match,
              'PLANTSTATS': custom_tables.plant_stats,
              'DISPATCHINTERCONNECTORRES': dynamic_data_compiler,
              'DISPATCHREGIONSUM': dynamic_data_compiler,
              'LOSSMODEL': dynamic_data_compiler,
              'LOSSFACTORMODEL': dynamic_data_compiler,
              'MNSP_DAYOFFER': dynamic_data_compiler,
              'MNSP_PEROFFER': dynamic_data_compiler,
              'MNSP_INTERCONNECTOR': dynamic_data_compiler,
              'INTERCONNECTOR': dynamic_data_compiler,
              'INTERCONNECTORCONSTRAINT': dynamic_data_compiler,
              'MARKET_PRICE_THRESHOLDS': dynamic_data_compiler}
