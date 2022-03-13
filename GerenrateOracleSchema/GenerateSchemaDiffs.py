# Import Libraries
import os
import difflib
import re
import pandas as pd

# Tool Configuration Parameters
file1 = 'C:\Tool\LOL_VENDOR_HUB - Copy.sql'
file2 = 'C:\Tool\LOL_VENDOR_HUB.sql'

keywords = ['CREATE TABLE', 'CREATE INDEX','CREATE OR REPLACE TRIGGER','GRANT', 'COMMENT ON COLUMN', 'ALTER TRIGGER', 'CONSTRAINT']
datatypes = ['NVARCHAR2', 'VARCHAR2', 'CHAR','NCHAR', 'FLOAT', 'NUMBER', 'DATE', 'TIMESTAMP', 'CLOB']
log= False

#  Check and Print Diffs
def identifyDiffs():
    text1 = open(file1).readlines()
    text2 = open(file2).readlines()
    if log: print('Files Opened')
    lineCounter1 = 0
    lineCounter2 = 0
    actions = pd.DataFrame(columns=['Location1','Location2','Source','changeType','SQLAction','Line'])
    for line in difflib.unified_diff(text1, text2):
        changeType = 'Ignore'
        sqlAction = 'Unknown'
        if log: print (line)
        if line[0:2] == '@@':
            changeType = 'Location'
            pattern='\d+'
            result = re.findall(pattern, line)
            if log: print ('Values extracted : ', result)
            lineCounter1 = int(result[0])
            lineCounter2 = int(result[2])
            if log: print('Set counters to lineCounter1 = %s and lineCounter2= %s' % (lineCounter1, lineCounter2))
        else:
            lineCounter1 +=1
            lineCounter2 +=1
            
        if line[0:1] == '+':
            changeType = 'Add'
            lineCounter2 -=1
            if log: print ('new line found @ position: %s' % (lineCounter2))            
        if line[0:1] == '-':
            changeType = 'Remove'
            lineCounter1 -=1
            if log: print ('old line removed @ position: %s' % (lineCounter1))
            
        if len(line) <3 or line[0:3]=='---' or line [0:3]=='+++':
            changeType = 'Ignore'
            if log: print('Blank Line')
        if log: print('Change Type Identified as %s' % (changeType))
        # Add to dataframe
        if changeType !='Ignore' and changeType !='Location' :
            # Identify the SQL Action Required
            # Check for Key Words
            for command in keywords:
                if command in line:
                    sqlAction = command
                    if log: print('Command found')
                    break
            if sqlAction == 'Unknown':
                for command in datatypes:
                    if command in line:
                        sqlAction = 'COLUMN'
                        if log: print('datatype found')
                        break
            if sqlAction == 'Unknown':
                sqlAction = 'COMMENT CONTINUED'
            if log: print(sqlAction)
            actions = actions.append({'Location1': lineCounter1, \
                                      'Location2': lineCounter2, \
                                      'Source': 'TBD', \
                                      'changeType': changeType, \
                                      'SQLAction': sqlAction, \
                                      'Line': line, \
                                      }, ignore_index=True)
    return actions

def buildDeltaScript(df):
    print(df)

def main():
    print ('Comparing File:%s to File:%s' % (file1, file2))
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    df = identifyDiffs()
    print(df)
    buildDeltaScript(df)

if __name__== '__main__':
    main()
