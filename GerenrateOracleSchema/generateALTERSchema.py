# This Code will match the current schema defined in the file with the same in the database.

# Import all libraries
import pyodbc
import os
# import xlrd
import pandas as pd
# import numpy as np

# Variable and Defaults
filepath = 'c:\\Tool'
fileName = 'Vendor Master - New Structure-V6.xlsx'
file = filepath + '\\' + fileName
target_environment = 'ENDW3PRD'

#DB Connection
print(os.environ.get("ORAUSER"))
connection = pyodbc.connect(f'DSN={target_environment};Uid={os.environ.get("ORAUSER")};Pwd={os.environ.get("ORAPASS")}')

def getCurrentSchema():
    #Get currently deployed Schema
    SQLCommand = ("SELECT ATC.TABLE_NAME, ATC.COLUMN_NAME, \
        ATCC.COMMENTS, \
        CASE WHEN ATC.DATA_TYPE LIKE 'TIMEST%' THEN 'TIMESTAMP' ELSE ATC.DATA_TYPE END AS DATA_TYPE, \
        COALESCE(CASE WHEN ATC.DATA_TYPE = 'NUMBER' THEN ATC.DATA_PRECISION \
        WHEN ATC.DATA_TYPE = 'DATE' THEN null \
        WHEN ATC.DATA_TYPE LIKE  'N%CHAR%' THEN ATC.CHAR_COL_DECL_LENGTH \
        ELSE ATC.CHAR_LENGTH \
        END,0) AS DATA_LENGTH, \
        COALESCE(ATC.DATA_SCALE,0) AS DATA_PRECISION, \
        ATC.NULLABLE \
        FROM  \
        ALL_TAB_COLUMNS ATC, \
        ALL_COL_COMMENTS ATCC \
        WHERE ATC.TABLE_NAME=ATCC.TABLE_NAME \
        AND ATC.COLUMN_NAME=ATCC.COLUMN_NAME \
        AND ATC.OWNER = 'LOL_VENDOR_HUB' \
        ORDER BY ATC.TABLE_NAME, ATC.COLUMN_NAME")
    currentSchema = pd.read_sql(SQLCommand, connection)
    currentSchema = currentSchema.apply(lambda x: x.astype(str).str.upper())
    currentSchema["DATA_LENGTH"] = pd.to_numeric(currentSchema["DATA_LENGTH"], errors='coerce', downcast='integer')
    currentSchema["DATA_PRECISION"] = pd.to_numeric(currentSchema["DATA_PRECISION"], errors='coerce', downcast='integer')

    return currentSchema

def readNewSchema():
    xl = pd.ExcelFile(file)
    newSchema = pd.DataFrame()
    for sheet in xl.sheet_names:
        if sheet[0:3].upper()=='VH_' or sheet[0:3].upper()=='PR_':
            # print('Processing Sheet : %s' % sheet)
            tabDefinition = pd.read_excel(xl, skiprows=14, sheet_name=sheet)
            tabDefinition.columns = tabDefinition.columns.str.lower()
            tabDefinition["hub nullable"] = tabDefinition["hub nullable"].fillna('Y')
            tabDefinition = tabDefinition.fillna(0)
            tabDefinition["hub data_or_char_len"] = pd.to_numeric(tabDefinition["hub data_or_char_len"],errors='coerce',downcast='integer')
            tabDefinition["hub data_precision"] = pd.to_numeric(tabDefinition["hub data_precision"],errors='coerce',downcast='integer')
            tabDefinition = tabDefinition.apply(lambda x: x.astype(str).str.upper())
            tabDefinition["hub data_type"] = tabDefinition["hub data_type"].replace('DATE', 'TIMESTAMP', regex=True)
            tabDefinition = tabDefinition.loc[tabDefinition['in db'] == 'Y']
            tabDefinition = tabDefinition[['hub_attribute','data item description',\
        'hub data_type', 'hub data_or_char_len','hub data_precision', 'hub nullable' ]]
            tabDefinition['table_name'] = sheet.upper()
            newSchema = newSchema.append(tabDefinition, ignore_index = True)
    newSchema = newSchema.sort_values(by=['table_name', 'hub_attribute'])
    newSchema.columns = ['COLUMN_NAME','COMMENTS', 'DATA_TYPE', 'DATA_LENGTH', 'DATA_PRECISION','NULLABLE', 'TABLE_NAME']
    cols = newSchema.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    newSchema=newSchema[cols]
    return newSchema

def compareSchema(currentSchema, newSchema):
    # print(currentSchema.head())
    # print(newSchema.head())
    newSchema = newSchema.replace('\'', '', regex=True)
    # Compare Table Objects
    tablesDB = set(currentSchema.TABLE_NAME.unique())
    tablesFile = set(newSchema.TABLE_NAME.unique())
    if  len(tablesDB & tablesFile) >0 :
        for table in tablesDB & tablesFile:
            # print('Comparing table attribs: %s' % table)
            ns = newSchema.loc[newSchema['TABLE_NAME'] == table]
            es = currentSchema.loc[currentSchema['TABLE_NAME'] == table]
            colDB = set(es.COLUMN_NAME.unique())
            colFile = set(ns.COLUMN_NAME.unique())
            if len(colDB & colFile) >0 :
                match=0
                for column in (colDB & colFile):
                    sizeInfo =''
                    nsc = ns.loc[newSchema['COLUMN_NAME'] == column]
                    #if table=='VH_SYNC_SYSTEMS':print(nsc)
                    esc = es.loc[currentSchema['COLUMN_NAME'] == column]
                    #if table=='VH_SYNC_SYSTEMS':print(esc)
                    if nsc.DATA_TYPE.iloc[0] != esc.DATA_TYPE.iloc[0] \
                       or (round(float(nsc.DATA_LENGTH.iloc[0])) != round(float(esc.DATA_LENGTH.iloc[0])) \
                           and not (nsc.DATA_TYPE.iloc[0] == 'TIMESTAMP' or nsc.DATA_TYPE.iloc[0] == 'CLOB'))\
                       or (round(float(nsc.DATA_PRECISION.iloc[0])) != round(float(esc.DATA_PRECISION.iloc[0])) \
                           and nsc.DATA_TYPE.iloc[0] == 'NUMBER') \
                       or nsc.NULLABLE.iloc[0] != esc.NULLABLE.iloc[0]:
                        dtype = nsc.DATA_TYPE.iloc[0]
                        if nsc.NULLABLE.iloc[0] == 'N':
                            nullable = 'NOT NULL'
                        else:
                            nullable =''
                        if dtype in ['DATE','CLOB']:
                            sizeInfo = ''
                        if dtype in ['NCHAR','NVARCHAR2','VARCHAR2','CHAR']:
                            if dtype in ['VARCHAR2','CHAR']:
                                sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ' CHAR)'
                            else:
                                sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ')'
                        if dtype in ['NUMBER','FLOAT']:
                            if round(float(nsc.DATA_PRECISION.iloc[0])) >0 :
                                sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ','+str(round(float(nsc.DATA_PRECISION.iloc[0])))+')'
                            else:
                                sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ')'

                        print('ALTER TABLE %s MODIFY %s %s%s %s;' %(table, column, dtype, sizeInfo,nullable))
                    if nsc.COMMENTS.iloc[0].replace('\n', '') != esc.COMMENTS.iloc[0].replace('\n', '') and nsc.COMMENTS.iloc[0] != '0':
                        print("COMMENT ON COLUMN %s.%s IS '%s';" %(table, column, nsc.COMMENTS.iloc[0]))
                    match=match+1

                # print('Comparing Columns: %s' % match)
            if len(colDB - colFile)>0 :
                for column in (colDB - colFile):
                    print('ALTER TABLE %s DROP COLUMN %s;' % (table, column))
            if len(colFile - colDB)>0:
                for column in (colFile - colDB):
                    nsc = ns.loc[newSchema['COLUMN_NAME'] == column]
                    dtype = nsc.DATA_TYPE.iloc[0]
                    if nsc.NULLABLE.iloc[0] == 'N':
                        nullable = 'NOT NULL'
                    else:
                        nullable =''
                    if dtype in ['DATE','CLOB']:
                        sizeInfo = ''
                    if dtype in ['NCHAR','NVARCHAR2','VARCHAR2','CHAR']:
                        if dtype in ['VARCHAR2','CHAR']:
                            sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ' CHAR)'
                        else:
                            sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ')'
                    if dtype in ['NUMBER','FLOAT']:
                        if round(float(nsc.DATA_PRECISION.iloc[0])) >0 :
                            sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ','+str(round(float(nsc.DATA_PRECISION.iloc[0])))+')'
                        else:
                            sizeInfo = '('+ str(round(float(nsc.DATA_LENGTH.iloc[0]))) + ')'
                    print('ALTER TABLE %s ADD %s %s%s %s;' % (table, column, dtype, sizeInfo,nullable))
                    if nsc.COMMENTS.iloc[0] != '0':
                        print("COMMENT ON COLUMN %s.%s IS '%s';" %(table, column, nsc.COMMENTS.iloc[0].replace('\n', '\\ \n')))

    if len(tablesDB - tablesFile)>0 :
        for table in (tablesDB - tablesFile):
            print('DROP TABLE %s;' % table)
    if len(tablesFile - tablesDB)>0:
        for table in (tablesFile - tablesDB):
            print(' -- Generate new schema for %s using the schema generation script' % table)


    # df_all = pd.concat([currentSchema.set_index(['TABLE_NAME', 'COLUMN_NAME']), newSchema.set_index(['TABLE_NAME', 'COLUMN_NAME'])], \
    #               axis='columns', keys=['Current', 'New'])
    # print(df_all.head())
    # df_all = df_all.swaplevel(axis='columns')[currentSchema.columns[2:]]
    # print(df_all.head())

def main():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    currentSchema = getCurrentSchema()
    newSchema = readNewSchema()
    compareSchema(currentSchema, newSchema)




if __name__== '__main__':
    main()

