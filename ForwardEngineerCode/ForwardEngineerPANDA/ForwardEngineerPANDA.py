import glob
import os
import pandas as pd
import csv


MAPPINGFILELOCATIONS = 'C:\\Logs\\'
MAPPINGFILEMASK = '*Final*.map.csv'

COPY_TO_CODEBASE = False
CHARS_NOT_ALLOWED_IN_COLUMN_NAME = tuple('!"#$%&\'()*+,-./:;?@[\\]^`{|\}~\t\n\r\x0b\x0c')

DATEFORMATS_DATE = '"M/d/yyyy", "MM/dd/yyyy", "M-d-yyyy", "MM-dd-yyyy", "d-MMM-yyyy", "dd-MMM-yyyy"'
DATEFORMATS_ALL = '"M/d/yyyy", "MM/dd/yyyy", "M-d-yyyy", "MM-dd-yyyy", "d-MMM-yyyy", "dd-MMM-yyyy", "M/d/yyyy H:m", "MM/dd/yyyy H:mm","MM/dd/yyyy HH:mm", "M/d/yyyy h:m:s t","M/d/yyyy h:m:s tt", "MM/dd/yyyy hh:mm:ss tt", "M/d/yyyy h:m:s", "MM/dd/yyyy hh:mm:ss", "M/d/yyyy H:m:s", "MM/dd/yyyy HH:mm:ss"'
DATEFORMATS_DATETIME = '"M/d/yyyy H:m", "MM/dd/yyyy HH:mm","MM/dd/yyyy HH:mm", "M/d/yyyy h:m:s t","M/d/yyyy h:m:s tt", "MM/dd/yyyy hh:mm:ss tt", "M/d/yyyy h:m:s", "MM/dd/yyyy hh:mm:ss", "M/d/yyyy H:m:s", "MM/dd/yyyy HH:mm:ss"'

DEBUG = False

PROJECT_SRC_FOLDER = 'C:\\Users\\49426\\Source\\Repos\\PANDA\\src'

# Specie Configuration
BEEFCONFIG = {'NAME': 'Beef',
              'MODELSDIRECTORY': '\\Beef\\Purina.Panda.Beef.Model\\Models',
              'FILEPROCESSORDIRECTORY': '\\Beef\\Purina.Panda.Beef.FileProcessing\\FileProcessors',
              'DBSCHEMANAME': 'PANDABeef'}

EQUINECONFIG = {'NAME': 'Equine',
                'MODELSDIRECTORY': '\\Equine\\Purina.Panda.Equine.Model\\Models',
                'FILEPROCESSORDIRECTORY': '\\Equine\\Purina.Panda.Equine.FileProcessing\\FileProcessors',
                'DBSCHEMANAME': 'PANDAEquine'}

CMRCONFIG = {'NAME': 'CMR',
                'MODELSDIRECTORY': '\\CMR\\Purina.Panda.CMR.Model\\Models',
                'FILEPROCESSORDIRECTORY': '\\CMR\\Purina.Panda.CMR.FileProcessing\\FileProcessors',
                'DBSCHEMANAME': 'PANDACMR'}

COMPANIONCONFIG = {'NAME': 'Companion',
                'MODELSDIRECTORY': '\\Companion\\Purina.Panda.Companion.Model\\Models',
                'FILEPROCESSORDIRECTORY': '\\Companion\\Purina.Panda.Companion.FileProcessing\\FileProcessors',
                'DBSCHEMANAME': 'PANDACompanion'}

# Choose the Specie to Modify
SPECIECONFIG = COMPANIONCONFIG


def read_mapping_file(filename):
    header = {'source_file_directory': '',
              'source_file_pattern': '',
              'blob_target': '',
              'xl_sheet_name': '',
              'target_table_name': '',
              'field_separator': '',
              'skip_rows': '',
              'header_instructions': '',
              'pivot_from': '',
              'footer_rows': '',
              'ignore_header_case': ''}
    dataframecreated = False
    key_col_count = 0
    with open(filename) as csvfile:
        mappingfile = csv.reader(csvfile)
        for row in mappingfile:
            if DEBUG:
                print(row)
            if len(row) < 1:
                continue
            if row[0] == 'Source file directory':
                header['source_file_directory'] = row[1]
            elif row[0] == 'Source file pattern':
                header['source_file_pattern'] = row[1]
            elif row[0] == 'Blob Target':
                header['blob_target'] = row[1]
            elif row[0] == 'XL Sheet Name':
                header['xl_sheet_name'] = row[1]
            elif row[0] == 'Target table name':
                header['target_table_name'] = row[1]
            elif row[0] == 'Field separator':
                header['field_separator'] = row[1]
            elif row[0] == 'Skip Rows':
                if row[1] == '-1':
                    header['skip_rows'] = '0'
                else:
                    header['skip_rows'] = row[1]
            elif row[0] == 'Header Instructions':
                header['header_instructions'] = row[1]
            elif row[0] == 'Pivot From':
                header['pivot_from'] = row[1]
            elif row[0] == 'Footer Rows':
                header['footer_rows'] = row[1]
            elif row[0] == 'Ignore Header Case':
                header['ignore_header_case'] = row[1]
            elif row[0] == 'Target Name':
                column_details = pd.DataFrame(columns=row)
                all_columns = row
                dataframecreated = True
            else:
                if dataframecreated:
                    
                    row[1] = row[1].upper()  # Make sure Source Column is in Uppercase

                    if row[8].upper() == 'Y': 
                        row[10] = 'N'
                        key_col_count +=1

                    if (row[4].upper() == 'DATETIME[NS]' or row[4].upper() =='TIMESTAMP') and row[7] == '':
                        row[7] = 'DATEFORMATS_ALL'
                        print(f'Added DATEFORMATS_ALL to {row[0]}')
                    column_details = column_details.append(
                        pd.DataFrame([row], columns=all_columns))
                    if row[4] == '':
                        print(f'Missing Datatype for column {row[0]}. Fill in missing data and rerun the tool.')
                        exit()
                    if row[10] == '':
                        print(f'Nullable information not available for column {row[10]}. Fill and rerun.')
                        exit()
                    if row[0] == '':
                        print (f'Target Column Name missing for row {index}. This value is required. ')
                        exit()
                    


        if header['target_table_name'] == '[ENTER TABLENAME]':
            print('NOT A VALID TABLENAME, Reenter table name')
            exit()
        if key_col_count < 2:
            print('Valid Keys Not Defined')
            exit()

        if DEBUG:
            print(header)
        if DEBUG:
            print(column_details)
    return header, column_details


def generate_data_model(header, column_details):
    # Read in the model template file
    with open('CodeTemplates//modelTemplate.cs', 'r') as file:
        model_template = file.read()

    # Replace the table name
    model_template = model_template.replace(
        'INSERT_TABLE_NAME', header["target_table_name"])

    # Add Specie Name
    model_template = model_template.replace(
        'ADD_SPECIE_NAME', SPECIECONFIG["NAME"])

    # Identify and replace key expression
    keys = "e." + column_details[column_details.KEY.isin(['Y', 'y'])]
    key = ', '.join(keys["Target Name"])
    model_template = model_template.replace('INSERT_PRIMARY_KEY', key)

    # Build and add column details to model
    section_indent = "\t\t"
    column_code = ""
    for index, row in column_details.iterrows():

        if row["Target Name"] == 'Source_File_Name':
            column_code = column_code + \
                section_indent + '[StringLength(350)]\n'

        column_code += section_indent
        column_code += "public "

        if row["DataType"] == 'float':
            column_code += "double"
        elif row["DataType"] == 'int':
            column_code += "int"
        elif row["DataType"] == 'String':
            column_code += "string"
        elif row["DataType"] == 'Timestamp' or row["DataType"] == 'datetime[ns]':
            column_code += "DateTime"
        else:
            print(
                f'UNKNOWN DataType Encountered : {row["DataType"]} : Defaulting to String DataType')
            column_code += "string"
        if DEBUG:
            print(column_code[-15:])
        if (row['Nullable'] == 'Y' or row['Nullable'] == 'y') and column_code[-15:] != '\t\tpublic string':
            column_code += "?"
        column_code += f' {row["Target Name"]} {{ get; set; }}\n'
    model_template = model_template.replace('INSERT_COLUMN_LOGIC', column_code)

    # Write the model class file
    with open(f'CodeOutput//Models//{SPECIECONFIG["NAME"]}//{header["target_table_name"]}.cs', 'w') as file:
        file.write(model_template)
    print(
        f'Model Generated Successfully at CodeOutput//Models//{SPECIECONFIG["NAME"]}//{header["target_table_name"]}.cs')


def generate_create_table_sql(header, column_details):
    # Define Table
    script = f'CREATE TABLE [{SPECIECONFIG["DBSCHEMANAME"]}].[{header["target_table_name"]}]\n(\n'
    # Add Column Definitions
    for index, row in column_details.iterrows():
        if row["DataType"] == 'float':
            data_type = "[float]"
        elif row["DataType"] == 'int':
            data_type = "[int]"
        elif row["DataType"] == 'Timestamp' or row["DataType"] == 'datetime[ns]':
            data_type = "[datetime2](7)"
        else:
            data_type = "[nvarchar]"
            if row["KEY"].upper() == 'Y':
                data_type += '(350)'
            else:
                data_type +='(max)'
        if row["Nullable"].upper() == 'Y':
            data_type += ' NULL,\n'
        else:
            data_type += ' NOT NULL,\n'
        script += f'\t[{row["Target Name"]}] {data_type}'
    # Add Constraint
    script += f'CONSTRAINT [PK_{header["target_table_name"]}] PRIMARY KEY CLUSTERED\n('
    script += '\n\t'.join(column_details[column_details["KEY"].str.upper() == 'Y']["Target Name"] + ' ASC,')
    script = script[:-1] + '\n)\n)'
    # Write the model class file
    with open(f'CodeOutput//DBSchemaSQL//{SPECIECONFIG["NAME"]}//{header["target_table_name"]}-createtable.sql', 'w') as file:
        file.write(script)
    print(script)


def generate_file_processor(header, column_details):
    # Read in the processor template file
    if header['field_separator'] == 'XL':
        with open('CodeTemplates//fileProcessorTemplateXL.cs', 'r') as file:
            processor_template = file.read()
    elif header['field_separator'] == 'FWF':
        with open('CodeTemplates//fileProcessorTemplateFWF.cs', 'r') as file:
            processor_template = file.read()
    else:
        with open('CodeTemplates//fileProcessorTemplateCSV.cs', 'r') as file:
            processor_template = file.read()
    # Initialize some variables to '', so that placeholders are all replaced
    pivot_headers = ''
    pivot_headers_declaration = ''
    additional_arguments_call = ''
    additional_arguments_definition = ''
    pivot_loop_start = ''
    pivot_loop_end = ''
    entity_indent = '\t\t\t\t'
    extra_indent = ''
    footer_filter = ''
    record_variable = 'record'

    # Add Specie Name
    processor_template = processor_template.replace(
        'ADD_SPECIE_NAME', SPECIECONFIG["NAME"])

    # Add the table Name
    processor_template = processor_template.replace(
        'ADD_TABLE_NAME', header["target_table_name"])

    # Define Column Index Variables
    column_details['define_index_var'] = '\t\tprivate int ' + \
        column_details["Target Name"] + 'Index;'
    define_index_code = '\n'.join(
        column_details[column_details["Source Name"] != ""]["define_index_var"])
    processor_template = processor_template.replace(
        'DEFINE_COLUMN_INDEX_VARIABLES', define_index_code)

    # Define Acceptable Dateformat Variables
    date_columns = column_details[column_details["DataType"].isin(
        ['Timestamp', 'datetime[ns]'])][["Target Name", "Format"]]
    date_columns["Format"] = date_columns["Format"].str[:-1]
    date_columns["Format"] = date_columns["Format"].str.replace(';', ',')
    if DEBUG:
        print(date_columns)
    date_columns["code"] = '\t\tprivate readonly string[] ' + \
        date_columns["Target Name"] + \
        'DateFormats = { ' + date_columns["Format"] + ' };'
    date_columns = date_columns[date_columns["Target Name"] != 'LastUpdatedAt']
    define_date_format_code = '\n'.join(date_columns["code"]).replace('DATEFORMATS_DAT', DATEFORMATS_DATE).replace(
        'DATEFORMATS_AL', DATEFORMATS_ALL).replace('DATEFORMATS_DATETIM', DATEFORMATS_DATETIME)
    processor_template = processor_template.replace(
        'DEFINE_ACCEPTABLE_DATE_FORMATS', define_date_format_code)

    # Create and add column array for SQL Bulk Copy
    column_details['target_column_string'] = '"' + \
        column_details["Target Name"] + '"'
    column_list = ', '.join(column_details["target_column_string"])
    processor_template = processor_template.replace(
        'ADD_ALL_COLUMN_NAMES_LIST', column_list)

    # Add XL Sheet Name to reader
    processor_template = processor_template.replace(
        'XL_SHEET_NAME', header["xl_sheet_name"])

    # Add Field Separator for Delimited Files
    processor_template = processor_template.replace(
        'FIELD_SEPARATOR', header["field_separator"])

    # Header Information - Identify Header row
    if header['skip_rows'] == '-1':
        header_var_assignment = 'var header = records.ToArray()[0].ToList();'
        header_position = 0
    elif header['skip_rows'].isnumeric():
        header_var_assignment = f'var header = records.ToArray()[{header["skip_rows"]}].ToList();'
        header_position = header['skip_rows']
    else:
        # This Option allows to iterate over rows and check value of a particular string to identify the number of rows to skip
        # Ex Input: Nutrients;2;1,1 - This will add the code to skip all rows till it finds Nutrients in column 2(Start @ 0) and set the header to that +1, data to that +1
        instructions = header['skip_rows'].split(';')
        header_var_assignment = 'int i = 0; \n\t\t\tforeach (IEnumerable<string> record in records)\n\t\t\t{\n\t\t\t\t'
        header_var_assignment += f'if (!String.IsNullOrWhiteSpace(record.ElementAt({instructions[1]})) && record.ElementAt({instructions[1]}).ToUpper().Equals("{instructions[0].upper()}")) break;\n\t\t\t\ti++;\n\t\t\t}}\n'
        header_var_assignment += f'\t\t\tvar header = records.ToArray()[i + {instructions[2]}].ToList();'
        header_position = f'i + {instructions[2]}'
    processor_template = processor_template.replace(
        'SET_HEADER_VARIABLE', header_var_assignment)
    
    # Skip footer from anchor point set footer as "Total";3 in the mapping sheet. String to find and column to find it in. 
    footer_instructions = header["footer_rows"].split(";")
    if len(footer_instructions) == 2:
        record_variable = "dataRecord"
        footer_filter = '\n\t\t\tList<IEnumerable<string>> dataRecords = new List<IEnumerable<string>>();'
        footer_filter += '\n\t\t\tforeach (IEnumerable<string> record in records)\n\t\t\t{'
        footer_filter += f'\n\t\t\t\tif (!String.IsNullOrWhiteSpace(record.ElementAt({footer_instructions[1]})) && record.ElementAt({footer_instructions[1]}).ToUpper().Equals("{footer_instructions[0].upper()}")) break ;'
        footer_filter += '\n\t\t\t\tdataRecords.Add(record);\n\t\t\t}\n\n//'
    processor_template = processor_template.replace(
        'FOOTER_FILTER', footer_filter)
    processor_template = processor_template.replace(
        'RECORDS_VARABLE', record_variable)

    # Alter the code flow to handle pivot tables
    for index, row in column_details.iterrows():
        if row['Comments'] != '':
            ph_instruction = row['Comments'].split(';')
            if ph_instruction[0].upper() == 'PIVOTH':
                print(
                    f'Pivot detected from column {header["pivot_from"]} for {row["Target Name"]}')
                pivot_headers_declaration += f'\t\tprivate IEnumerable<string> {row["Target Name"]}Header;\n'
                additional_arguments_call += f', {row["Target Name"]}Header'
                additional_arguments_definition += f', IEnumerable<string> {row["Target Name"]}Header'
                if header["skip_rows"].isnumeric():
                    ph_header_position = str(
                        int(header_position) + int(ph_instruction[1]))
                else:
                    ph_header_position = f'{header_position} + {ph_instruction[1]}'
                pivot_headers += f'\t\t\t{row["Target Name"]}Header = records.ElementAt({ph_header_position});\n'

    # Add code to define pivot header variables and assign the pivot header row to it.
    processor_template = processor_template.replace(
        'GET_PIVOT_HEADER_LIST', pivot_headers)
    processor_template = processor_template.replace(
        'DEFINE_PIVOT_HEADER_VARIABLES', pivot_headers_declaration)

    # Add arguments to the add record ADDITIONALARGUMENTSCALL and ADDITIONALARGUMENTSDEFINITION
    processor_template = processor_template.replace(
        'ADDITIONALARGUMENTSCALL', additional_arguments_call)
    processor_template = processor_template.replace(
        'ADDITIONALARGUMENTSDEFINITION', additional_arguments_definition)

    # Add Loop to the AddRecords function to flatten all pivot values
    pivot_value_cols = column_details[column_details["Comments"].str.upper(
    ) == "PIVOTV"]
    increment_var = pivot_value_cols.shape[0]
    if increment_var == 1:
        increment_str = 'i++'
    else:
        increment_str = f'i+={increment_var}'
    if header["pivot_from"] != '':
        pivot_loop_start += f'\t\t\tfor (int i = {header["pivot_from"]}; i < record.Count(); {increment_str}) {{\n\t\t\t\tif ('
        for index, row in pivot_value_cols.iterrows():
            pivot_loop_start += f' !String.IsNullOrWhiteSpace(record.ElementAt(i + {index})) && !record.ElementAt(i + {index}).Trim().Equals("0") &&'
        pivot_loop_start = pivot_loop_start[:-2] + ') {\n'
        entity_indent += '\t\t'
        extra_indent = '\t\t'
        pivot_loop_end = '\t\t\t\t}\n\t\t\t}'
        
    processor_template = processor_template.replace(
        'PIVOT_LOOP_START', pivot_loop_start)
    processor_template = processor_template.replace(
        'EXTRA_INDENT', extra_indent)
    processor_template = processor_template.replace(
        'PIVOT_LOOP_END', pivot_loop_end)
    # Records Start Position
    if header["skip_rows"].isnumeric():
        header_position = str(int(header_position) + 1)
    else:
        header_position = f'i + {int(instructions[2]) + int(instructions[3])}'
    processor_template = processor_template.replace(
        'NON_DATA_ROWS', str(header_position))

    # Add number of columns in File
    num_columns_in_file = column_details[column_details["Source Name"]
                                         != ""].shape[0] - 1
    processor_template = processor_template.replace(
        'NUM_COLUMNS_IN_FILE', str(num_columns_in_file))

    # Add code to find index of columns
    column_details['assign_index_code'] = '\t\t\t' + column_details["Target Name"] + \
        'Index = header.FindIndex(s => !String.IsNullOrWhiteSpace(s) && s.ToUpper().Equals("' + \
        column_details["Source Name"] + '"));'
    assign_index_code = '\n'.join(
        column_details[column_details["Source Name"] != ""]["assign_index_code"])
    processor_template = processor_template.replace(
        'ASSIGN_COLUMN_INDEX_VARIABLES', assign_index_code)

    # Add code to map Source and Target Columns
    column_details['assign_index_code'] = 'record.ElementAt(' + \
        column_details["Target Name"] + 'Index)'
    assign_index_code = ''
    pivot_index = 0
    for index, row in column_details.iterrows():
        # Allow missing column for nullables
        if row["Nullable"].upper() == 'Y':
            row_code = row["Target Name"] + 'Index >= 0 ? '
        else:
            row_code = ''

        # Define the mapping
        if row["DataType"] == 'float' and row["Default"] == '':
            row_code += ('NumUtils.NullableDouble(' +
                         row["assign_index_code"] + ')')
        elif row["DataType"] == 'float' and row["Default"] != '':
            row_code += ('NumUtils.DefaultDouble(' +
                         row["assign_index_code"] + ', ' + row["Default"] + ')')
        elif row["DataType"] == 'int' and row["Default"] == '':
            row_code += ('NumUtils.NullableInt(' +
                         row["assign_index_code"] + ')')
        elif row["DataType"] == 'int' and row["Default"] != '':
            row_code += ('NumUtils.DefaultInt(' +
                         row["assign_index_code"] + ', ' + row["Default"] + ')')
        elif (row["DataType"] == 'Timestamp' or row["DataType"] == 'datetime[ns]') and row["Default"] == '':
            row_code += ('DateUtils.NullableDate(' +
                         row["assign_index_code"] + ', ' + row["Target Name"]+'DateFormats)')
        elif (row["DataType"] == 'Timestamp' or row["DataType"] == 'datetime[ns]') and row["Default"] != '':
            row_code += ('DateUtils.DefaultDate(' + row["assign_index_code"] +
                         ', ' + row["Target Name"]+'DateFormats, ' + row["Default"] + ')')
        elif (row["DataType"] == 'String' or row["DataType"] == 'String') and row["Default"] != '':
            row_code += ((row["assign_index_code"]) + ' ?? ' + row["Default"])
        else:
            row_code += (row["assign_index_code"])

        # Add else condition for nullable columns
        if row["Nullable"].upper() == 'Y':
            row_code += (' : null ,\t // ' + row["Target Name"])
        else:
            row_code += (',\t // ' + row["Target Name"])

        if row["Source Name"] != '':
            assign_index_code += f'\n{entity_indent}{row_code}'
        elif row["Target Name"] == 'Source_File_Name':
            assign_index_code += f'\n{entity_indent}FullBlobPath,\t// Source_File_Name'
        elif row["Target Name"] == 'LastUpdatedAt':
            assign_index_code += f'\n{entity_indent}DateTime.UtcNow\t// LastUpdatedAt'
        elif row["Comments"][:6].upper() == "PIVOTH":
            assign_index_code += f'\n{entity_indent}{row["Target Name"]}Header.ElementAt(i),\t// Pivot Header: {row["Target Name"]}'
        elif row["Comments"][:6].upper() == "PIVOTV":
            assign_index_code += f'\n{entity_indent}record.ElementAt(i + {pivot_index}),\t// Pivot Value: {row["Target Name"]}'
            pivot_index += 1
        else:
            assign_index_code += f'\n\n{entity_indent}// TODO: Add code for column {row["Target Name"]} using instructions "{row["Comments"]}"\n'
        
        if row["Source Name"] != '' and row["Comments"] != "":
            assign_index_code +=f'\n{entity_indent}// TODO: Modify above code for column {row["Target Name"]} using instructions "{row["Comments"]}"\n'

    processor_template = processor_template.replace(
        'ADD_COLUMN_DATA_MAPPINGS', assign_index_code)
        
    # Write the model class file
    with open(f'CodeOutput//Processors//{SPECIECONFIG["NAME"]}//{header["target_table_name"]}Processor.cs', 'w') as file:
        file.write(processor_template)
    print(
        f'Processor Generated Successfully at CodeOutput//Processors//{SPECIECONFIG["NAME"]}//{header["target_table_name"]}Processor.cs')


def add_to_Specie_context(header):
    class_def_flag = False
    pk_flag = False
    source_file_name_index = False
    contents=[]
    changed_flg = False

    file_path = PROJECT_SRC_FOLDER + "\\".join(SPECIECONFIG['MODELSDIRECTORY'].split('\\')[:-1]) +'\\'+ SPECIECONFIG['NAME'] + 'Context.cs'

    with open(file_path, 'r') as context_file:
        for line in  context_file:
            # print(line, len(line))
            if f"public class {SPECIECONFIG['NAME']}Context : DbContext" in line:
                class_def_flag = True
            if class_def_flag:
                if "<" + header["target_table_name"] + ">" in line:
                    print("Model exists. Nothing to do here")
                    class_def_flag = False
                    continue
                if len(line) < 2:
                    print("End of Declaration Reached. Model will be attached")
                    line=f'\t\tpublic virtual DbSet<{header["target_table_name"]}> {header["target_table_name"]} {{ get; set; }}\n\n'
                    print(line)
                    changed_flg =  True
                    class_def_flag = False
            if '#region "modelBuilder"' in line:
                pk_flag =  True
            if pk_flag:
                if "<" + header["target_table_name"] + ">" in line:
                    print("PK already defined. Nothing to add here")
                    pk_flag = False
                    continue
                if "#endregion" in line:
                    print("Could not find key definition. Will ADD")
                    line = f'\t\t\tmodelBuilder.Entity<{header["target_table_name"]}>()\n'
                    line += f'\t\t\t\t.HasKey(new {header["target_table_name"]}().PrimaryKeyExpression);\n'
                    line += '\t\t\t#endregion\n'
                    print(line)
                    changed_flg = True
                    pk_flag = False
                
            if '#region "Indices"' in line:
                source_file_name_index = True
            if source_file_name_index:
                if "<" + header["target_table_name"] + ">" in line:
                    print("Index on Source_File_Name already defined. Nothing to do here")
                    source_file_name_index = False
                    continue
                if "#endregion" in line:
                    print("Coundn't find the Index on Source_File_Name. It will be added")
                    line = f'\t\t\tmodelBuilder.Entity<{header["target_table_name"]}>()\n'
                    line += '\t\t\t\t.HasIndex(t => new { t.Source_File_Name });\n'
                    line += '\t\t\t#endregion\n'
                    print(line)
                    changed_flg = True
                    pk_flag = False
            contents +=line

    if changed_flg:
        #print(contents)
        with open(file_path, 'w') as context_file:
            context_file.write(''.join(contents))






def main():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # Find Mapping Files
    files = glob.glob(MAPPINGFILELOCATIONS+MAPPINGFILEMASK, recursive=False)

    # Loop through all files
    for file in files:
        choice = input(
            f'Do you want to Code based on {file} for Specie {SPECIECONFIG["NAME"]} (Y/N) (DEFAULT: Y): ' or 'Y').upper()
        if choice == 'N':
            continue
        # Load Mapping File
        print(f"Processing Mapping {file}")
        header, column_details = read_mapping_file(file)

        # Generate Data Model
        generate_data_model(header, column_details)

        # Generate Create Table Script
        generate_create_table_sql(header, column_details)

        # Code for context file
        with open(f'CodeOutput//AdditionalCode//{SPECIECONFIG["NAME"]}_context.cs', 'a+') as file:
            file.write(
                f'\n\n\n# *********************** \n# {header["target_table_name"]}\n# *********************** \n')
            file.write(
                f'# Add this code to the dbcontext \n\t\tpublic virtual DbSet<{header["target_table_name"]}> {header["target_table_name"]} {{ get; set; }}\n\n')
            file.write(
                f'# Use this to define primary key \n\t\t\tmodelBuilder.Entity<{header["target_table_name"]}>()\n\t\t\t\t.HasKey(new {header["target_table_name"]}().PrimaryKeyExpression);\n\n')
            file.write(
                f'# Use this to define index on Source_File_Name\n\t\t\tmodelBuilder.Entity<{header["target_table_name"]}>()\n\t\t\t\t.HasIndex(t => new {{ t.Source_File_Name }});\n\n')
        if COPY_TO_CODEBASE: 
            add_to_Specie_context(header)



        # Code for Base File
        with open(f'CodeOutput//AdditionalCode//{SPECIECONFIG["NAME"]}_base.cs', 'a+') as file:
            file.write(
                f'\n\n\n# *********************** \n# {header["target_table_name"]}\n# *********************** \n')
            switch_value = header["blob_target"].upper().replace(SPECIECONFIG['NAME'].upper() + '\\','')
            file.write(
                f'# Use this for the router\n\t\t\t\tcase "{switch_value}":\n\t\t\t\t\ttableName = strSchemaName + "{header["target_table_name"]}";\n\t\t\t\t\tfileProcessors.Add(new {header["target_table_name"]}Processor(input, blobPath, tableName, funcId));\n\t\t\t\t\tbreak;')
        # Code for Mappings.json
        with open(f'CodeOutput//AdditionalCode//{SPECIECONFIG["NAME"]}_FileUploader.json', 'a+') as file:
            file.write(
                f'\n\n\n# *********************** \n# {header["target_table_name"]}\n# *********************** \n')
            file.write(
                f'# Use this for the mappings.json\n\t{{\n\t\t"source": "{header["source_file_directory"]}",\n\t\t"destination": "{header["source_file_directory"]}",\n\t\t"fileFilter": "{header["source_file_pattern"]}"\n\t}}')

        # Generate File Processor
        generate_file_processor(header, column_details)

        # Copy files to codebase
        if COPY_TO_CODEBASE:
            print('Copying Model and Target to Project Location.')
            os.system(f'COPY  CodeOutput\\Processors\\{SPECIECONFIG["NAME"]}\\{header["target_table_name"]}Processor.cs {PROJECT_SRC_FOLDER + SPECIECONFIG["FILEPROCESSORDIRECTORY"]}' )
            os.system(f'COPY  CodeOutput\\Models\\{SPECIECONFIG["NAME"]}\\{header["target_table_name"]}.cs {PROJECT_SRC_FOLDER + SPECIECONFIG["MODELSDIRECTORY"]}' )

if __name__ == '__main__':
    main()
