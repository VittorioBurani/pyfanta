from ast import main
import os
import numpy as np
import pandas as pd
import argparse
import sqlite3


# Actual directory path:
here = os.getcwd()


# Databse connection handling:
path_to_db = here + '/db.sqlite3'
db = sqlite3.connect(path_to_db)


# Championship estimate from 'vincenti.csv'
path_to_vincenti_csv = here + '/vincenti.csv'
stima_vincenti = pd.read_csv(path_to_vincenti_csv)
squadre = list(stima_vincenti.columns)

for i in range(0,len(squadre)):
    for j in range(i+1,len(squadre)):
        if i < j:
            stima_vincenti[squadre[j]][i] *= -1

# Points mapping:
def punti(x):
    if x == 0:
        return 2
    elif x == -2:
        return 0
    elif x == -1:
        return 1
    elif x == 1:
        return 4
    else:
        return 6

# Sorter function:
def sorter(v):
    for i in range(0, len(v)-1):
        for j in range (i+1, len(v)):
            if v[i][1] <= v[j][1]:
                t = v[i]
                v[i] = v[j]
                v[j] = t
    return v

# Championship estimer:
def stima_campionato():
    classifica = [[squadre[i], 0] for i in range(0, len(squadre))]
    for i in range(0,len(squadre)):
        for j in range(0, len(squadre)):
            classifica[i][1] += punti(-stima_vincenti[squadre[j]][i])
    return sorter(classifica)

# Workaround to print right position:
def posizione(c, s):
    for i in range(0, len(squadre)):
        if s == c[i][0]:
            return i+1



def dataframe_gazzetta():
    pass


# Arguments parser:
def parse_args():
    # Parser initialization:
    parser = argparse.ArgumentParser()
    # ARGUMENT EXAMPLE:
    # parser.add_argument('--clock', type=str, default='cus', choices=clock_choices, help='Desired clock configuration.')
    # Compute bool:
    parser.add_argument('--compute', action='store_true', help='To compute the data and fill the SQLite3 database.')
    # Parsed args return:
    return parser.parse_args()


# Main Function:
def main():
    global db
    # Championship estimation:
    classifica = stima_campionato()
    


# Main script:
if __name__ == '__main__':
    main()
