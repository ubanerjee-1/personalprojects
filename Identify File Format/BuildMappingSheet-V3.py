# Import Libraries
# import os
import glob
# import csv
import re
from collections import Counter
from datetime import date
import pandas.api.types as pdtypes
from dateutil.parser import parse
import calendar
from statistics import mode
import logging
import sys
import itertools
import pandas as pd

# Set Variables
PATH = "C:\\Logs\\"
file_pattern = '*'
OPATH = "C:\\Logs"
# TBD; Should create a consolidated mapping sheet for each sub-directory.
recursive_file_search = False
# printableChars = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;?@[\\]^_`{|}~ \t\n\r\x0b\x0c')
skipseparator = list(
    '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ:-.!"#$%&\'()*+/@[\\]\n\r\x0b\x0c')
df_master_fields = pd.DataFrame(columns=['Target Name', 'Source Name', 'Column Position', 'Column Width', 'DataType',
                                         'Length', 'Scale', 'Format', 'KEY', 'Default', 'Nullable', 'Comments', 'Unique', 'ImpactsGrain', 'HasNULLs'])
consolidate = True
ignore_header_case = True
debug = False
# acceptableColLengthStr = [1,5,10,25,100,4000] # TBD
#acceptableColLengthInt = [1,5,10,15,30]
pivot_from_column = -1           # -1 means no Pivot
pivot_column_name = 'PivotColumn'  # Only used if Manual pivot is specified
force_skip = -1              # Set to -1 for Auto; Not implemented for XL Yet
footer = 0                    # Lines from the footer to ignore, 0 for Default
# Set to 'Auto' to Auto Identify. Set to ' ' for Fixed Width Files.Will assume force_skip as 0 unless specified
force_separator = 'Auto'
# Set to a blank list to Auto Identify. Manually add column sizes if auto detect does not work.
force_fw_field_length = []
# set to 'None', explicit names, force_skip +1 or 0(Default),
force_header = force_skip + 1
# Only work with single sheet to consolidate properly, Consolidate will be False in case of multiple sheets
force_sheet = ['in']
aggresive_integer_identification = True
drop_duplicate_columns = False

# Initialize Logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
levels = {True: logging.DEBUG,
          False: logging.INFO}

logger.setLevel(levels[debug])
# logger.setFormatter(formatter)
ch = logging.StreamHandler(stream=sys.stdout)
ch.setFormatter(formatter)
logger.addHandler(ch)


# Identify if any column is duplicate. It needs to be removed from further analysis
def get_duplicate_columns(df):
    duplicate_column_names = set()
    # Iterate over all pairs of columns in df
    for a, b in itertools.combinations(df.columns, 2):
        # will check if every entry in the series is True
        if (df[a] == df[b]).all():
            duplicate_column_names.add(b)

    return list(duplicate_column_names)

# def idenfityheader_position(name, fformat, tab)


def get_char_count_by_line(file_path, skip_blanks):
    with open(file_path) as fh:
        return [Counter(line) for line in fh if not (skip_blanks and line.startswith('\n'))]


# Identify how column values are separated within a row.
def identify_separator(name):
    # this will only analyze the most common row length in the dataset.
    most_comm_length = False
    logger.debug(f"Currently analyzing file : {name}")
    # Create a list of characters by Line
    character_frequencies = get_char_count_by_line(f"{PATH}\\{name}", True)


    # Keep only the most common length rows.
    df = pd.DataFrame(character_frequencies)
    if footer > 0:
        df.drop(df.tail(footer).index, inplace=True)  # drop last n rows
    row_totals = df.fillna(0).sum(numeric_only=True, axis=1)
    logger.debug(f"Row Totals : {row_totals}")
    try:
        mode_total = mode(row_totals)
    except:
        logger.warning("Multiple mode exists, choose one")
        c = Counter(row_totals).most_common(5)
        logger.info("[(Value, Frequency),........]\n", c)
        default = Counter(row_totals).most_common(1)[0][0]
        mode_total = int(
            input(f"Choose One(Default = {default} : ") or default)

    logger.debug(f"Row Mode : {mode_total}")
    df['Totals'] = row_totals
    logger.debug(df.head())
    if most_comm_length:
        df = df[(df.Totals > mode_total*.8) & (df.Totals < mode_total*1.2)]
    logger.debug(df.head())
    df = df.drop(columns='Totals', errors='ignore')
    # Remove characters that are generally not used as separators.
    logger.debug(f"These Characters will be Skipped:  {skipseparator}")
    df.drop(columns=skipseparator, errors='ignore', inplace=True)
    logger.debug(f'\n{df.head()}')
    logger.debug("Potential separators")
    # METHOD 1: Try to identify separator with the understanding it should be present in every row.
    df_dense = df.dropna(axis='columns')
    logger.debug(df_dense.head())
    candidates = df_dense.columns
    logger.debug(
        f"Number of characters present in every row : {len(df_dense.columns)}")
    if len(df_dense.columns) == 1:
        separator = str(df_dense.columns[0])
        logger.debug(f"separator identified as : {separator} using METHOD 1")
    else:
        separator = '-1'
        logger.debug(
            "Unable to identify separator using METHOD 1 as 0 or multiple exist!!")
    # METHOD 2: Least Variance: The count of the separator should be more or less same across rows.
    logger.debug("% of rows missing the character")
    logger.debug(df.isna().sum() / df.isna().count())
    logger.debug(f"Threshold = {(df.shape[0])*.8}, \t Shape = {df.shape[0]}")
    cleanup_candidates = df.dropna(
        axis='columns', thresh=(df.shape[0])*.8).fillna(-1)
    logger.debug("Dropping characters not present in 80% of the columns")
    logger.debug(cleanup_candidates.head())
    lowest_variance = 0
    space_detected_flag = False
    separator2 = ''
    for character in cleanup_candidates.columns:
        logger.debug(f"********** {character} **********")
        x = cleanup_candidates.loc[:, character].var()
        logger.debug(f"Calculated variance : {x}")
        if character == ' ':
            space_detected_flag = True
            logger.debug("Potential position based file...")
            continue
        if lowest_variance >= x:
            lowest_variance = x
            separator2 = character
        logger.debug(f"separator identified as : {separator2} using METHOD 2")
    if separator == separator2:
        common_separator = separator
    elif len(separator2) == 1:
        common_separator = separator2
    else:
        common_separator = list(
            set(candidates).intersection(cleanup_candidates.columns))
        logger.debug(
            f"Both methods identify {common_separator} as one of the separator candidates.")
        max_mode = 0
        mode_table = cleanup_candidates.mode()
        logger.debug(mode_table)
        if len(common_separator) != 1:
            logger.debug(
                f"Multiple Common separator!! Use Max MODE \n{cleanup_candidates.columns}")
            logger.debug(cleanup_candidates.mode())
            if len(cleanup_candidates.columns) > 1:
                # Give priority to other separator instead of space
                mode_table = mode_table.drop(columns=' ', errors='ignore')
            for column in mode_table.columns:
                x = mode_table.loc[0, column]
                logger.debug(column, '\'s Mode: ', x)
                if x > max_mode:
                    common_separator = column
                    max_mode = x
                logger.debug(
                    f"Resolved ambiguity by Max Mode Method to: {common_separator}")

    # Identify if header rows need to be skipped
    if force_skip == -1:
        first_row = cleanup_candidates[common_separator].idxmax()
    else:
        first_row = force_skip
    logger.debug(f"The Header is expected to be in row: {first_row}")
    return common_separator[0], first_row


def identify_fixed_width(name):
    total_characters = 0
    max_length = 0
    character_count = []
    # get_char_count_by_line(f"{PATH}\\{name}", True)
    with open(f"{PATH}\\{name}", "r") as current_file:
        for numberLines, line in enumerate(current_file, start=1):
            total_characters += len(line)
            character_count.append(len(line))
            if len(line) <= 2:
                numberLines -= 1
            if max_length < len(line):
                max_length = len(line)
    avgChars = total_characters/numberLines
    stopPoint = numberLines - footer  # drop last n rows
    modeChars = mode(character_count)
    logger.debug(
        f"Sample file has {numberLines} lines. There are an average {avgChars} characters per line.")
    logger.debug(
        f"Sample file has {numberLines} lines. Most lines have {modeChars} characters per line.")
    counter = 0
    if force_skip >= 0:
        counter = force_skip
        logger.debug(f"Skipping {counter} rows as directed.")
    else:
        with open(f"{PATH}\\{name}", "r") as current_file:
            for counter, line in enumerate(current_file, start=counter):
                logger.debug(f"{counter} has {len(line)} chars")
                if len(line) <= modeChars*.9 or len(line) >= modeChars*1.1:
                    logger.debug(
                        f"Line {counter}: Maybe part of header and needs to be skipped")
                else:
                    logger.debug(f"First row of data is at line : {counter}")
                    break
    # Figure out Column Start and stop positions
    colPos = []
    with open(f"{PATH}\\{name}", "r") as current_file:
        for rowCounter, line in enumerate(current_file, start=0):
            if rowCounter < counter or rowCounter > stopPoint:
                continue
            blanks = [m.start() for m in re.finditer(' ', line)]
            if len(blanks) > 2:
                colPos.append([m.start() for m in re.finditer(' ', line)])
                if rowCounter <= 5:
                    logger.debug(colPos[-1])
    # Intersection
    Common = list(set.intersection(*map(set, colPos)))
    Common = sorted(Common)
    logger.debug(f"Potential field separator positions: {Common}")
    # Remove sequential values
    newCommon = []
    for x in Common:
        if (x-1) not in Common:
            newCommon.append(x)
    newCommon.append(max_length)
    logger.debug(f"Field separator positions identified as : {newCommon}")
    # Calculate Width
    width = []
    range = len(newCommon)
    i = 0
    if newCommon[i] != 0:
        width.append(newCommon[i])
    for x in newCommon[0:range-1]:
        width.append(newCommon[i+1]-newCommon[i])
        i += 1
    logger.debug(f"Column Lengths: {width}")
    return counter, width

# Parse File and collect Field Information


def identify_fields(name, separator, header_position, width):
    if separator != 'XL':
        logger.debug(f"Currently analyzing column structure for file : {name}")
        current_file = f"{PATH}\\{name}"
    if separator == 'FWF':
        df = pd.read_fwf(current_file, parse_dates=False, skiprows=header_position,
                         skipfooter=0, widths=width, header=force_header)
        logger.debug("Opening File as Fixed Width")
    elif separator == 'XL':
        df = pd.read_excel(name, skiprows=header_position, sheet_name=width)
    else:
        df = pd.read_csv(current_file, sep=separator, parse_dates=False,
                         skiprows=header_position, skipfooter=0, header=force_header, float_precision='high')
    dupCols = get_duplicate_columns(df)

    if drop_duplicate_columns: df = df.drop(columns=dupCols)
    org_columns = df.columns.str.replace(' ','_')
    if ignore_header_case:
        df.columns = map(str.upper, map(str, df.columns))
    df_field_structure = pd.DataFrame(index=[df.columns], columns=['Target Name', 'Source Name', 'Column Position', 'Column Width',
                                                                   'DataType', 'Length', 'Scale', 'Format', 'KEY', 'Default', 'Comments', 'Unique', 'ImpactsGrain', 'HasNULLs'])
    totalRowCount = df.shape[0]
    total_duplicate_rows = df[df.duplicated()].shape[0]
    if total_duplicate_rows > 0:
        logger.warning(
            f"This file contains {total_duplicate_rows} duplicate rows!")
    if len(dupCols) > 0:
        df_field_structure.loc['Duplicate',
                               'Target Name'] = 'DUPLICATE Fields:' + '-'.join(dupCols)
        logger.warning(
            f"The following columns were identified as a duplicate column and will be removed from the final mapping")
        logger.warning(dupCols)
    logger.debug(f"Columns in the Dataset \n{df.columns}")
    logger.debug(df_field_structure)
    counter = 1
    for counter, field_name in enumerate(df.columns, start=0):
        logger.info(f"Processing Field: {field_name}")
        df_field_structure.loc[field_name, 'Source Name'] = field_name
        # This will need to be mapped to a Target Column outside of this code.
        df_field_structure.loc[field_name, 'Target Name'] = org_columns[counter]
        df_field_structure.loc[field_name, 'Column Position'] = counter + 1
        if separator == 'FWF':
            df_field_structure.loc[field_name,
                                   'Column Width'] = width[counter]
        #counter += 1
        # Capture Pandas column datatype into the DataType Column
        df_field_structure.loc[field_name, 'DataType'] = str(
            df[field_name].dtypes).replace('64', '', 1).replace('32', '', 1)
        logger.debug(
            f"{field_name} column's data type by old system: {df[field_name].dtypes}")
        logger.debug(
            f"{field_name} column's data type by old system stored: {df_field_structure.loc[field_name,'DataType']}")
        #logger.debug(f"{field_name} column's data type by old system stored: {str(df[field_name].dtypes).replace('64', '',1).replace('32', '',1)}")
        logger.debug(
            f"Check if {field_name} column's data type is float: {pdtypes.is_float_dtype(df[field_name])}")
        logger.debug(
            f"Check if {field_name} column's data type is int: {pdtypes.is_integer_dtype(df[field_name])}")
        logger.debug(
            f"Check if {field_name} column's data type is timestamp: {pdtypes.is_datetime64tz_dtype(df[field_name])}")

        # aggresive_integer_identification: If a column is float only due to nulls & existing values are all int.
        # Change col to int.
        # Consolidation will validate across multiple files and change back to float if necessary.
        if aggresive_integer_identification and pdtypes.is_float_dtype(df[field_name]) == 'float':
            if df[field_name].fillna(1).apply(float.is_integer).all():
                df_field_structure.loc[field_name, 'DataType'] = 'int'

        format = ''
        if df[field_name].isnull().all():
            # If the column is alway null set datatype to unknow
            df_field_structure.loc[field_name, 'DataType'] = 'Unknown'
        # Check if object is a timestamp or a String
        if df[field_name].dtypes == 'object':
            field_value = str(
                df.loc[df.loc[:, field_name].first_valid_index(), field_name])
            logger.debug(
                f"First non NaN Index & Value: {df.loc[:,field_name].first_valid_index()}, {field_value}")
            date_flg = True
            try:
                date_time = parse(field_value, fuzzy=False)
            except ValueError:
                date_flg = False
            except OverflowError as err:
                date_flg = False
                logger.debug(err)
            if date_flg == True:
                shortMonth = False
                shortDate = False
                logger.debug(f"Input Date: {field_value}")
                logger.debug(f"Interpreted Date: {date_time}")
                logger.debug(f"Today is = {date.today()}")
                if str(date.today()) in str(date_time):
                    logger.debug(
                        "Parser possibly assumed today's date. Won't search for date in Input string")
                    format = field_value
                else:
                    yrSt = field_value.find(str(date_time.year))
                    logger.debug(
                        f"Year Start Position: {field_value.find(str(date_time.year))}")
                    # found 4 digit Year 2019, 2020
                    format = field_value.replace(
                        str(date_time.year), 'yyyy', 1)
                    if yrSt == -1:
                        # found 2 digit Year 19,20
                        format = field_value.replace(
                            str(date_time.year)[2:], 'yy', 1)
                    logger.debug(f"Format after Year Identification: {format}")

                    noMonth = False
                    monSt = format.find(str(date_time.month).zfill(2))
                    logger.debug(f"2 Digit Month Position: {monSt}")
                    format = format.replace(str(date_time.month).zfill(
                        2), 'MM', 1)  # found 2 digit month 01, 02
                    if monSt == -1:
                        monSt1 = format.find(str(date_time.month))
                        if monSt1 != -1:
                            shortMonth = True
                            # found single digit month 1,2
                            format = format.replace(
                                str(date_time.month), 'M', 1)
                        else:
                            noMonth = True
                    # Check if Month Name or Abbreviations are used
                    if noMonth:
                        abbr = map(str.upper, calendar.month_abbr[1:])
                        fmnth = map(str.upper, calendar.month_name[1:])
                        logger.debug(abbr)
                        for mon in abbr:
                            if mon in format.upper():
                                logger.debug(
                                    f"Month Abbr used in this date format {mon}")
                                noMonth = False
                                # found Month abbreviation JAN, FEB, Etc
                                format = format.replace(mon, 'MMM', 1)
                        for mon in fmnth:
                            if mon in format.upper():
                                logger.debug(
                                    f"Month Name used in this date format {mon}")
                                noMonth = False
                                # found full month name January, February
                                format = format.replace(mon, 'MMMM', 1)
                    logger.debug(
                        f"Format after Month Identification: {format}")

                    daySt = format.find(str(date_time.day).zfill(2))
                    logger.debug(f"2 Digit Day Position: {daySt}")
                    format = format.replace(str(date_time.day).zfill(
                        2), 'dd', 1)  # 2 digit date 01,02,10
                    if daySt == -1:
                        daySt1 = format.find(str(date_time.day))
                        if daySt1 != -1 and not noMonth:
                            shortDate = True
                            # single digit date 1,2
                            format = format.replace(str(date_time.day), 'd', 1)
                    logger.debug(f"Day format: {format}")

                hhSt = format.find(str(date_time.hour).zfill(2))
                logger.debug(f"2 digit Hour Position: {hhSt}")
                format = format.replace(str(date_time.hour).zfill(
                    2), 'HH', 1)  # 2 digit hour 01,02
                logger.debug(f"2 digit Hour Format: {format}")
                if hhSt == -1:
                    hhSt = format.find(str(date_time.hour).zfill(2))
                    logger.debug(f"24 Hour Format Position: {hhSt}")
                    format = format.replace(str(date_time.hour).zfill(
                        2), 'HH', 1)  # 2 digit 24 hour clock 13,14, etc
                    logger.debug(f"24 Hour Format: {format}")
                if hhSt == -1:
                    hhSt = format.find(str(date_time.hour))
                    logger.debug(f"1 digit Hour Position: {hhSt}")
                    format = format.replace(
                        str(date_time.hour), 'H', 1)  # 1 digit hour 1,2,
                    logger.debug(f"1 Digit Hour Format: {format}")

                mnSt = format.find(str(date_time.minute).zfill(2))
                logger.debug(f"Mins Position: {mnSt}")
                format = format.replace(str(date_time.minute).zfill(
                    2), 'mm', 1)  # 2 digit mins 01,02
                logger.debug(f"Mins Format: {format}")

                secSt = format.find(str(date_time.second).zfill(2))
                logger.debug(f"Seconds Position: {secSt}")
                format = format.replace(str(date_time.second).zfill(
                    2), 'SS', 1)  # 2 digit Seconds
                logger.debug(f"Seconds Format: {format}")

                # if shortMonth or shortDate:
                #    format = format + ';' + format.replace(str('mm'), 'm',1).replace(str('dd'), 'd',1)
                #    logger.debug('Date Format Identified as :', format)
                # change object datatype to Timestamp
                df_field_structure.loc[field_name, 'DataType'] = 'Timestamp'
            else:
                # change object datatype to string
                df_field_structure.loc[field_name, 'DataType'] = 'String'
        if df[field_name].isnull().all():
            df_field_structure.loc[field_name, 'Length'] = 0
        else:
            df_field_structure.loc[field_name, 'Length'] = df[field_name].map(
                str).apply(len).max()
        logger.debug(
            f"Field Data type: {df_field_structure.loc[field_name,'DataType'].values[0]}")
        if df_field_structure.loc[field_name, 'DataType'].values[0] == 'float':
            df_field_structure.loc[field_name, 'Scale'] = df[field_name].apply(lambda x: len(
                str.split(str(x), ".")[1]) if len(str.split(str(x), ".")) > 1 else 0).max()
            logger.debug(
                f"Field Precision: {df_field_structure.loc[field_name,'Scale']}")


        df_field_structure.loc[field_name, 'Format'] = format
        df_field_structure.loc[field_name, 'Unique'] = df[field_name].is_unique
        dftmp = df.drop(columns=field_name)
        logger.debug(dftmp.head())
        duplicate_rows = dftmp[dftmp.duplicated()].shape[0]
        if duplicate_rows > total_duplicate_rows:
            grainFlg = True
        else:
            grainFlg = False
        # NEEDS MORE ANALYSIS
        df_field_structure.loc[field_name, 'ImpactsGrain'] = grainFlg
        if df[field_name].isna().sum() > 0:
            df_field_structure.loc[field_name, 'HasNULLs'] = True
        else:
            df_field_structure.loc[field_name, 'HasNULLs'] = False

    logger.debug(df.columns)
    logger.debug(df_field_structure)
    return df_field_structure


# Merge all File Mappings to master mapping file.def addToMaster(df_field_structure):
def addToMaster(df_field_structure):
    logger.debug("Consolidating Multiple Mappings.....")
    logger.debug(df_field_structure.loc[:, 'Target Name'])
    # df_master_fields
    # df_master_fields.loc[:,'Format']='XXX'
    df_master_fields['Format'] = df_master_fields.Format.apply(
        lambda x: x if not (pd.isnull(x) or x == '') else 'XXX')
    logger.debug(df_master_fields['Format'])
    for index, row in df_field_structure.iterrows():
        logger.debug(row)
        logger.debug(f"{index}.) row['Target Name'] = {row['Target Name']}")
        df_master_fields.loc[row['Target Name'], 'Target Name'] = row['Target Name']
        df_master_fields.loc[row['Target Name'], 'Source Name'] = row['Source Name']
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'Column Position']):
            df_master_fields.loc[row['Target Name'],
                                 'Column Position'] = row['Column Position']
        else:
            if df_master_fields.loc[row['Target Name'], 'Column Position'] != row['Column Position']:
                logger.warning("Column positions vary by file.")
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'Column Width']):
            df_master_fields.loc[row['Target Name'],
                                 'Column Width'] = row['Column Width']
        else:
            if df_master_fields.loc[row['Target Name'], 'Column Width'] < row['Column Width']:
                logger.warning(
                   PATH = PATH + '**\\' "Column Widths vary by file.Merge may not be accurate")
                df_master_fields.loc[row['Target Name'],
                                     'Column Width'] = row['Column Width']
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'DataType']):
            df_master_fields.loc[row['Target Name'],
                                 'DataType'] = row['DataType']
        else:
            if df_master_fields.loc[row['Target Name'], 'DataType'] != row['DataType']:
                if row['DataType'] == 'float':
                    df_master_fields.loc[row['Target Name'],
                                         'DataType'] = 'float'
                if row['DataType'] == 'Timestamp':
                    df_master_fields.loc[row['Target Name'],
                                         'DataType'] = 'Timestamp'
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'Length']):
            df_master_fields.loc[row['Target Name'], 'Length'] = row['Length']
        else:
            if df_master_fields.loc[row['Target Name'], 'Length'] < row['Length']:
                df_master_fields.loc[row['Target Name'],
                                     'Length'] = row['Length']
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'Scale']):
            df_master_fields.loc[row['Target Name'], 'Scale'] = row['Scale']
        else:
            if df_master_fields.loc[row['Target Name'], 'Scale'] < row['Scale']:
                df_master_fields.loc[row['Target Name'],
                                     'Scale'] = row['Scale']
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'Format']):
            df_master_fields.loc[row['Target Name'], 'Format'] = 'XXX'
        if not(pd.isnull(row['Format']) or row['Format'] == ''):
            logger.debug(
                f"Checking if {row['Format']} not in {df_master_fields.loc[row['Target Name'],'Format']}")
            logger.debug(f"Size of Format value is: {len(row['Format'])}")
            logger.debug(
                f"Check to see if the value is NULL: {pd.isnull(row['Format'])}")
            if row['Format'] not in df_master_fields.loc[row['Target Name'], 'Format']:
                df_master_fields.loc[row['Target Name'],
                                     'Format'] += '"' + row['Format'] +'"'
                df_master_fields.loc[row['Target Name'], 'Format'] += ';'
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'Unique']):
            df_master_fields.loc[row['Target Name'], 'Unique'] = row['Unique']
        else:
            if not(row['Unique']):
                df_master_fields.loc[row['Target Name'], 'Unique'] = False
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'ImpactsGrain']):
            df_master_fields.loc[row['Target Name'],
                                 'ImpactsGrain'] = row['ImpactsGrain']
        else:
            if row['ImpactsGrain']:
                df_master_fields.loc[row['Target Name'], 'ImpactsGrain'] = True
        if pd.isnull(df_master_fields.loc[row['Target Name'], 'HasNULLs']):
            df_master_fields.loc[row['Target Name'],
                                 'HasNULLs'] = row['HasNULLs']
        else:
            if row['HasNULLs']:
                df_master_fields.loc[row['Target Name'], 'HasNULLs'] = True

    logger.debug(df_master_fields)


def print_mapping(file_name_parts, separator, header_position, df_field_structure):
    file_name_parts[-1] = 'map'
    name = '.'.join(file_name_parts)
    name += '.csv'
    logger.debug(name)
    with open(f"{OPATH}\\{name}", "w+") as current_file:
        # Add Header to Mapping File.
        current_file.write(f"Source file directory,{PATH}\n")
        current_file.write(f"Source file pattern,{file_pattern}\n")
        current_file.write("Blob Target\n")
        if separator == 'XL' :
            current_file.write(f"XL Sheet Name,{file_name_parts[0].split('_')[-1]}\n")
        else:
            current_file.write("XL Sheet Name,'NA'\n")
        current_file.write(f"Target table name,[ENTER TABLENAME]\n")
        current_file.write(f'Field separator,"{separator}"\n')
        current_file.write(f"Skip Rows,{header_position}\n")
        if str(force_header) == '0':
            current_file.write(f"Header Instructions,Use Default\n")
        elif str(force_header) == 'None':
            current_file.write(f"Header Instructions,Use Column Position\n")
        else:
            current_file.write(f"Header Instructions,{force_header}\n")
        current_file.write("Pivot From\n")
        current_file.write(f"Footer Rows,{footer}\n")
        current_file.write(f"Ignore Header Case,{ignore_header_case}\n\n")

    # Add system Fields
    df_field_structure.loc['SystemField1', 'Target Name'] = 'Source_File_Name'
    df_field_structure.loc['SystemField2', 'Target Name'] = 'LastUpdatedAt'
    df_field_structure.loc['SystemField1', 'DataType'] = 'String'
    df_field_structure.loc['SystemField2', 'DataType'] = 'Timestamp'
    df_field_structure.loc['SystemField1', 'KEY'] = 'Y'
    df_field_structure.loc['SystemField1',
                           'Comments'] = 'Store File Path + Name'
    df_field_structure.loc['SystemField2',
                           'Comments'] = 'Timestamp when the row was last modified'
    df_field_structure.loc['SystemField1', 'Nullable'] = 'N'
    df_field_structure.loc['SystemField2', 'Nullable'] = 'N'
    df_field_structure.fillna({'Nullable': 'Y'}, inplace=True)
    # Add Column Details to mapping File
    df_field_structure.to_csv(
        OPATH + "\\" + name, mode='a', index=False, header=True)


# Read all files in directory
# files = os.listdir(PATH)
if recursive_file_search:
    PATH = PATH + '**\\'
logger.info(f"Searching for files that match : {PATH+file_pattern}")
files = glob.glob(PATH+file_pattern, recursive=recursive_file_search)
master_separator = 'INIT'
text_formats = ("txt", "csv", "log")
total_files = len(files)
final_skip_row = []
files_processed_flg = False

# Process all files in directory
# with glob.iglob(PATH+file_pattern, recursive=recursive_file_search) as files:
for file_counter, name in enumerate(files, start=0):
    name = str.split(name, "\\")[-1]
    file_name_parts = str.split(name, ".")
    logger.debug(file_name_parts)
    width = [0]
    if '.map.' in name:
        logger.debug(f"Skip current file (Output File): {name}")
        continue
    logger.info(
        f"({file_counter}/{total_files})-->  CURRENTLY PROCESSING FILE: {name}")
    try:
        date_time = parse(name, fuzzy=True)
        logger.info(f"Date in File Header : {date_time}")
    except ValueError:
        date_flg = False
    if str.lower(file_name_parts[len(file_name_parts) - 1]) in text_formats:
        logger.debug("This is a text file.")
        if force_separator == 'Auto':
            separator, header_position = identify_separator(name)
        else:
            separator = force_separator
            header_position = 0
        if separator != '-1':
            logger.debug(f"separator successfully identified as: {separator}")
        else:
            logger.warning(
                "Unable to identify separator. This file will be skipped!")
            continue
        if separator == ' ':
            logger.info("This file may be a fixed width file")
            header_position, width = identify_fixed_width(name)
            if len(force_fw_field_length) > 0:
                logger.debug("Override Fixed Width column sizes to user input")
                width = force_fw_field_length
            logger.debug(f"Width Array :{width}, Size: {len(width)}")
            if len(width) <= 1:
                logger.info(
                    "This file may be space separated however it is not a fixed width file.")
                continue
            else:
                separator = 'FWF'
        if force_skip >= 0:
            header_position = force_skip
        logger.debug(
            f"final_skip_row = {final_skip_row}, header_position = {header_position}")
        if len(final_skip_row) == 0:
            final_skip_row.append(header_position)
        if str(header_position) not in map(str, final_skip_row):
            final_skip_row.append(header_position)
            if len(final_skip_row) > 1:
                logger.warning(
                    f"New Header Position Identified... Validate if files are consistent. {'|'.join(map(str,final_skip_row))}")

        df_field_structure = identify_fields(
            name, separator, header_position, width)
        if master_separator != 'INIT':
            if (master_separator != separator) and consolidate:
                logger.warning(
                    "These files have different separators so results will not be consolidated")
                consolidate = False
        else:
            master_separator = separator
        logger.debug("Field Structure identified successfully")
        files_processed_flg = True
        # Print Mapping Sheet
        if consolidate:
            addToMaster(df_field_structure)
        print_mapping(file_name_parts, separator,
                      header_position, df_field_structure)
    elif str.lower(file_name_parts[-1]) in ['xlsx', 'xls', 'xlsm']:
        if file_name_parts[0][0] == '~':
            logger.info("This is a temp file and will be Ignored")
            continue
        logger.debug("This is an Excel file.")
        separator = 'XL'
        header_position = force_skip
        xl = pd.ExcelFile(PATH+'\\'+name)

        if len(force_sheet) == 0:
            force_sheet = xl.sheet_names

        if len(force_sheet) != 1:
            consolidate = False

        for sheet in force_sheet:
            df_field_structure = identify_fields(
                xl, separator, header_position, sheet)
            if master_separator != 'INIT':
                if (master_separator != separator) and consolidate:
                    logger.warning(
                        "These files have different separators so results will not be consolidated")
                    consolidate = False
            else:
                master_separator = separator
            logger.debug("Field Structure identified successfully")
            files_processed_flg = True
            # Print Mapping Sheet
            if consolidate:
                addToMaster(df_field_structure)
            file_name_parts[0] = file_name_parts[0]+ "_" + sheet
            print_mapping(file_name_parts, separator,
                          header_position, df_field_structure)
    else:
        logger.info(f"Skip current file (Unknown Format) : {name}")
# Prepare to print consolidated results
if consolidate and files_processed_flg:
    file_name_parts = ['FinalMappingSheet', 'map']
    if separator == 'XL': file_name_parts[0] = file_name_parts[0]+ "_" + sheet
    if len(final_skip_row) > 1:
        header_position = '|'.join(map(str, final_skip_row))
    logger.info(f"header_position: {header_position}")
    df_master_fields['Format'] = [x[3:] for x in df_master_fields['Format']]
    logger.info(
        "Printing consolidated mapping results to FinalMappingSheet.map.csv")
    print_mapping(file_name_parts, separator,
                  header_position, df_master_fields)

