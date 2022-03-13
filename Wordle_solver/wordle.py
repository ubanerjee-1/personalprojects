import json
import pandas as pd
from random import randrange
import sys

df = pd.read_json('word_list.json')
df = df['list'].apply(lambda x: pd.Series(list(x)))

usage = ['B','B','B','B','B']
safe_letters = []
while True:
    print(F'STARTING ROUND WITH {len(df)} POSSIBILITIES !!')
    random_row = randrange(len(df))
    print(f"Type in the following word, Use [S] if you want a new word.")
    print(df.iloc[[random_row]])
    letters = [df.iloc[random_row][0],df.iloc[random_row][1],df.iloc[random_row][2],df.iloc[random_row][3],df.iloc[random_row][4]]
    first = True
    next_word = False
    for i in range(0,5):
        
        if usage[i].upper() != 'G':
            usage[i] = input( f" Color of letter {letters[i]} was [G]reen, [Y]ellow, [B]lack, [S]kip:")
            if first:
                first = False
                if usage[i].upper() == 'S':
                    next_word = True
                    break
            # Capture to make sure if  a second instance the letter is black, it is not removed from the list of possibilities
            if usage[i].upper() == 'Y':
                safe_letters.append(letters[i].upper())
    if next_word:
        next_word = False
        continue
    for i in range(0,5):
        
        if usage[i].upper() == 'G':
            df = df[df[i] ==  letters[i]]
            
        if usage[i].upper() == 'Y':
            df = df[df[i] !=  letters[i]]
            df['filter'] = df.applymap(lambda x: letters[i] in str(x).lower()).any(1)
            df = df[df['filter'] == True]
            df = df.drop('filter', 1)
            
        if usage[i].upper() == 'B' and letters[i].upper() not in safe_letters:
            # Make sure a second instance of the letter is not Green
            for j in range(0,5):
                if usage[j].upper() == 'G':
                    continue
                df = df[df[j] !=  letters[i]]
        
        print(f'Possible combinations remaining {len(df)}')
    #print(df)
    df = df.reset_index().drop('index', 1, errors='ignore')
    if len(df) < 100:
        output = ''
        for i,row in df.iterrows():
            output += f"{row[0]}{row[1]}{row[2]}{row[3]}{row[4]},\t"
            if i % 5 == 0:
                output += '\n'
        print(output)
        if len(output) < 11:
            print('SOLVED!!')
            sys.exit(0)
            
