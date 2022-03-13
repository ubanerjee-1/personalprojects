# Import Libraries
import os
import csv
import xlrd
import pandas as pd
import cx_Oracle

# Tool Configuration Parameters
filepath = 'c:\\Tool'
fileName = 'Vendor Master - New Structure-V6.xlsx'
file = filepath + '\\' + fileName
filterByPreFix = 'VH_'
targetTablespace = 'LOL_VENDOR_HUB_DATA'
schema = 'LOL_VENDOR_HUB'
indexTablespace = 'LOL_VENDOR_HUB_IDX'
outputDir = 'c:\\Tool'
outputFileName = 'LOL_VENDOR_HUB.sql'
outputFile = outputDir + '\\' + outputFileName
outputDropFile = outputDir + '\\DROP_' + outputFileName
outputPubSynFile = outputDir + '\\SYNONYM_' + outputFileName
dropSQLFlag = True
enableTrigFlag = True
addComments = True
log= False
check = True
dropInDB = True
createInDB = True
addSequenceTrigger=False
seqStartingValue=['VH_COMMON_PARTITIONED','5000']
createPublicSynonym=True


# Start of code
# con = cx_Oracle.connect('LOL_EDW/sppaibo@endwd-scan/endw3dv2')
# print (con.version)
# con.close()
xl = pd.ExcelFile(file)
if log: print('Sheets available in the excel file for processing are: ', xl.sheet_names)
table_names = []
scriptSynonymCreate = []
scriptSynonymDrop=[]
scriptSynonymCreate.append('-- CREATE --\n')
scriptSynonymDrop.append('\n\n-- DROP --\n')
for sheet in xl.sheet_names:
    # print(sheet + ' , ' + sheet[0:2])
    if sheet[0:3].upper()==filterByPreFix or sheet[0:3].upper()=='PR_':
        table_names.append(sheet)
        scriptSynonymCreate.append('CREATE PUBLIC SYNONYM '+ sheet.upper()+' FOR '+schema+'.'+sheet.upper()+';')
        scriptSynonymDrop.append('DROP PUBLIC SYNONYM '+ sheet.upper()+';')
print('The following sheets will be processed: ', table_names)

if createPublicSynonym:
    f=open(outputPubSynFile, 'w+')
    f.write('\n'.join(scriptSynonymCreate))
    f.write('\n'.join(scriptSynonymDrop))
    f.close()

script = []
scriptDrop = []
warning =[]
scopeCounter = 1
scope=len(table_names)
for table in table_names:
    # script =[] # Comment out this line to generate one single script
    print('PROCESSING SHEET('+str(scopeCounter)+'/'+str(scope)+').................: ',table)
    # Drop table as needed
    if dropSQLFlag:
        scriptDrop.append('DROP TABLE '+schema+'.'+ table.upper() + ';\n')
    if check:
        if len(table)>= 23 :
            print('WARNING: table name length >= 23 : ', len(table))
    script.append('CREATE TABLE '+schema+'.'+ table.upper() + '(')
    # Changed to use the ExcelFile object to improve performance of the code.
    tabDefinition = pd.read_excel(xl, skiprows=14, sheet_name=table)
    # tabDefinition = pd.read_excel(file, skiprows=14, sheet_name=table)
    tabDefinition.columns = tabDefinition.columns.str.lower()
    if log: print(tabDefinition.columns)
    tabDefinition = tabDefinition[['sequence', 'hub_attribute', 'in db','data item name','data item description',\
        'hub data_type', 'hub data_or_char_len','db default','hub data_precision', 'hub nullable' ]]
    if log: print('Keeping only the fields we need for HUB: ',tabDefinition.columns)
    if log: print('Keeping only rows where in DB is set to Y')
    if log: print(tabDefinition['in db'].str.upper() == 'Y')
    tabDefinition = tabDefinition[tabDefinition['in db'].str.upper() == 'Y']
    if log: print(tabDefinition)
    last_row = tabDefinition.shape[0]
    # print(last_row)
    if log: print(script)
    counter = 0
    comments = ''
    primaryKey = ''
    indexScript = ''
    indexCounter=1
    for index, row in tabDefinition.iterrows():
        if check:
            if len(row['hub_attribute']) >30:
                print('WARNING: Column name length > 30 : ',str(row['hub_attribute']), len(row['hub_attribute']))
            if ' ' in row['hub_attribute']:
                print('WARNING: Column name contains spaces : ',str(row['hub_attribute']))
            if row['hub data_type'].upper() == 'NUMBER' and (int(row['hub data_or_char_len'])<= 0 or int(row['hub data_or_char_len'])>=38):
                print('WARNING: Column size for Number must be between 0-38 : ',str(row['hub_attribute']),str(row['hub data_or_char_len']))
            if row['hub data_type'].upper() not in ['NVARCHAR2', 'VARCHAR2', 'CHAR','NCHAR', 'FLOAT', 'NUMBER', 'DATE', 'TIMESTAMP', 'CLOB']:
                print('WARNING: Unknown datatype :',str(row['hub_attribute']),row['hub data_type'].upper())
        string = '\t' + str(row['hub_attribute']).upper().ljust(32)
        if 'SEQUENCE' in str(row['db default']).upper():
            if primaryKey == '':
                primaryKey = str(row['hub_attribute'].upper())
            else:
                primaryKey =primaryKey +', '+ str(row['hub_attribute'].upper())
        if str(row['hub data_type']).upper() == 'DATE':
            row['hub data_type'] = 'TIMESTAMP'
        colDef = str(row['hub data_type']).upper()
        if addComments:
            comments += 'COMMENT ON COLUMN ' + table.upper() +'.'+  str(row['hub_attribute']).upper() +' IS \''\
                        + str(row['data item description']).replace('\'','').replace('\n', '\\ \n') + '\';\n'
        if row['hub data_type'].upper() !='TIMESTAMP' and row['hub data_type'].upper() !='CLOB':
            colDef =colDef + '(' + str(int(row['hub data_or_char_len'])) 
            if row['hub data_precision'] >= 0 and row['hub data_type'].upper() =='NUMBER':
                colDef = colDef + ','+ str(int(row['hub data_precision']))
            if row['hub data_type'].upper() == 'CHAR' or row['hub data_type'].upper() == 'VARCHAR2':
                colDef = colDef + ' CHAR)'
            else:
                colDef = colDef + ')'
        string += colDef.ljust(20)
        if row['hub nullable'] == 'N':
            string = string + ' NOT NULL'
        counter +=1
        if counter <last_row:
            string = string + ', '
        else:
            if primaryKey != '':
                constraint = ',\nCONSTRAINT XPK' + table.upper() + ' PRIMARY KEY ('+ primaryKey +') USING INDEX TABLESPACE '+ indexTablespace +' '
                if log: print(constraint)
                string +=constraint
            string = string + ') \nTABLESPACE '+ targetTablespace + '; \n'
        if log: print(string)
        script.append(string)
        
        # Create index for system Columns
        if (str(row['hub_attribute']).upper() in ['DW_CREATE_DATE','DW_INSERT_DATE','DW_UPDATE_DATE']) or ((str(row['hub_attribute']).upper()[-3:] == '_ID') and ('SEQUENCE' not in str(row['db default']).upper())):
            index= '\nCREATE INDEX IDX_' + table.upper() + '_' + str(indexCounter)+ \
                         '\n\tON ' + table.upper()+ ' (' + str(row['hub_attribute']).upper()+ ')\n TABLESPACE '+ indexTablespace +' ;'
            indexScript+=index
            indexCounter+=1
            if log: print('This column will be indexed using the following SQL: \n',index)
            
    # Add indexes to Script
    indexScript+='\n\n'
    script.append(indexScript)
                                
    # Add comments to the table columns
    if addComments: script.append(comments)
    
    # Gererate Triggers & Sequence objects for autoIDS and audit columns
    triggerCols = tabDefinition.loc[tabDefinition['db default'].notnull()]
    triggerCols = triggerCols[['hub_attribute','db default']]
    triggerCols=triggerCols.apply(lambda x: x.astype(str).str.lower())
    if log: print('These columns require triggers to populate : \n', triggerCols)

    # Create Sequence objects
    seqCounter = 1
    if triggerCols.shape[0]>0:
        for index, row in triggerCols.loc[triggerCols['db default'].str.contains('sequence')].iterrows():
            if dropSQLFlag:
                scriptDrop.append('\nDROP SEQUENCE S_' + table.upper()+'_'+str(seqCounter)+';')
            seqSQL = '\nCREATE SEQUENCE S_' + table.upper()+'_'+str(seqCounter)
            if table.upper() in seqStartingValue:
               seqSQL=seqSQL+'\n\tSTART WITH ' + seqStartingValue[seqStartingValue.index(table.upper()) +1]
            seqSQL=seqSQL+';'
            script.append(seqSQL)
            script.append('\nGRANT SELECT ON S_' + table.upper() + '_'+str(seqCounter)+' TO '+schema+'_IUD;\n')
            if log: print('Added sequence for : ', row['hub_attribute'])
            seqCounter+=1

    # Trigger to handle insert
    flg = False
    seqCounter=1
    keywords=['sequence','insert','update']
    trigSQL = '\nCREATE OR REPLACE TRIGGER '+schema+'.T_I_'+table.upper()+ \
        '\n\tBEFORE INSERT ON '+ table.upper() +' FOR EACH ROW\n\tBEGIN '
    if triggerCols.shape[0]>0:
        for index, row in triggerCols.loc[triggerCols['db default'].str.contains('|'.join(keywords))].iterrows():
            if 'sysdate' in row['db default']:
                trigSQL +='\n\t\t:NEW.'+row['hub_attribute'].upper()+' :=SYSDATE;'
                if log: print('Added autopopulate sysdate on insert for : ', row['hub_attribute'])
                flg=True
            if addSequenceTrigger:
                if 'sequence' in row['db default']:
                    trigSQL +='\n\t\tSELECT S_'+table.upper()+'_'+str(seqCounter)+ \
                        '.nextval \n\t\t\tINTO :NEW.'+row['hub_attribute'].upper()+'\n\t\t\tFROM DUAL;'
                    seqCounter+=1
                    if log: print('Added autopopulate sequence on insert for : ', row['hub_attribute'])
                    flg=True
            else:
                if log: print(row['hub_attribute'], ' needs to be populated using : S_' +table.upper()+'_'+str(seqCounter))
            if 'dbuser' in row['db default']:
                trigSQL +='\n\t\tSELECT sys_context(\'USERENV\', \'SESSION_USER\')' + \
                    '\n\t\t\tINTO :NEW.'+row['hub_attribute'].upper()+'\n\t\t\tFROM DUAL;'
                if log: print('Added autopopulate username on insert for : ', row['hub_attribute'])
                flg=True 
    trigSQL +='\n\tEND;\n/'
    if flg:
        script.append(trigSQL)
        if enableTrigFlag: script.append('ALTER TRIGGER '+schema+'.T_I_'+table.upper()+' ENABLE;\n')
        # if dropSQLFlag: scriptDrop.append('\nDROP TRIGGER '+schema+'.T_I_'+table.upper()+ ';')

    # Trigger to handle update
    flg = False
    keywords=['update']
    trigSQL = '\nCREATE OR REPLACE TRIGGER '+schema+'.T_U_'+table.upper()+ \
        '\n\tBEFORE UPDATE ON '+ table.upper() +' FOR EACH ROW\n\tBEGIN '
    if triggerCols.shape[0]>0:
        for index, row in triggerCols.loc[triggerCols['db default'].str.contains('|'.join(keywords))].iterrows():
            if 'sysdate' in row['db default']:
                trigSQL +='\n\t\t:NEW.'+row['hub_attribute'].upper()+' :=SYSDATE;'
                if log: print('Added autopopulate date on update for : ', row['hub_attribute'])
                flg=True
            if 'dbuser' in row['db default']:
                trigSQL +='\n\t\tSELECT sys_context(\'USERENV\', \'SESSION_USER\')'+ \
                    '\n\t\t\tINTO :NEW.'+row['hub_attribute'].upper()+'\n\t\t\tFROM DUAL;'
                if log: print('Added autopopulate username on update for : ', row['hub_attribute'])
                flg=True 
    trigSQL +='\n\tEND;\n/'
    if flg:
        script.append(trigSQL)
        if enableTrigFlag: script.append('ALTER TRIGGER '+schema+'.T_U_'+table.upper()+' ENABLE;\n')
        # if dropSQLFlag: scriptDrop.append('\nDROP TRIGGER '+schema+'.T_U_'+table.upper()+ ';')

        
    # Add table grants
    if log: print('Added all necessary grants for : ', table.upper())
    script.append('GRANT SELECT ON ' + table.upper() + ' TO '+schema+'_SEL;')
    script.append('GRANT SELECT ON ' + table.upper() + ' TO '+schema+'_IUD;')
    script.append('GRANT INSERT ON ' + table.upper() + ' TO '+schema+'_IUD;')
    script.append('GRANT UPDATE ON ' + table.upper() + ' TO '+schema+'_IUD;')
    script.append('GRANT DELETE ON ' + table.upper() + ' TO '+schema+'_IUD;\n\n')
    scopeCounter+=1
    if scopeCounter >= 20:
        break
    if log: print(script)

# Print out the script file
# pd.DataFrame(script).to_csv(outputFile, mode='a', index= False, header= False )
f=open(outputFile, 'w+')
# print('\n'.join(script))
f.write('\n'.join(script))
f.close()

# Print out the script to DROP schema objects
if dropSQLFlag:
    f=open(outputDropFile, 'w+')
    f.write('\n'.join(scriptDrop))
    f.close()

