import os
import numpy as np
import pandas as pd
import argparse
import sqlite3
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


# Actual directory path:
here = os.getcwd()


# Databse connection handling:
path_to_db = here + '/db.sqlite3'
db = sqlite3.connect(path_to_db)


# Championship estimate from 'vincenti.csv'
path_to_vincenti_csv = here + '/vincenti.csv'
stima_vincenti = pd.read_csv(path_to_vincenti_csv, index_col=0)
squadre = list(stima_vincenti.columns)


# Points mapping:
def complem_points(x:int):
    if x == 0:
        return 6
    elif x == 1:
        return 4
    elif x == 2:
        return 2
    elif x == 3:
        return 3
    elif x == 4:
        return 1
    else:
        return 0


# Sorter function:
def sorter(v:list):
    for i in range(0, len(v)-1):
        for j in range (i+1, len(v)):
            if v[i][1] <= v[j][1]:
                t = v[i]
                v[i] = v[j]
                v[j] = t
    return v


# Championship estimer:
def stima_campionato():
    for i in range(len(squadre)):
        for j in range(len(squadre)):
            if i > j:
                stima_vincenti.loc[squadre[j], squadre[i]] = complem_points(stima_vincenti[squadre[j]][squadre[i]]) # Tricky!!
    classifica = [[squadre[i], 0] for i in range(0, len(squadre))]
    for i in range(0,len(squadre)):
        classifica[i][1] = np.sum(stima_vincenti.iloc[i].to_numpy())
    classifica = np.array(sorter(classifica))
    classifica_df = {'Squadra': list(), 'Punti': list()}
    for i in range(len(classifica)):
        classifica_df['Squadra'].append(classifica[i,0])
        classifica_df['Punti'].append(classifica[i,1])
    classifica_df = pd.DataFrame.from_dict(classifica_df)
    return classifica_df


# Workaround to print right position:
def posizione_classifica(classifica:pd.DataFrame, squadra:str):
    serie = classifica['Squadra']
    for i in range(0, len(squadre)):
        if squadra == serie[i]:
            return i+1


# Webscraper function to get gazzetta.it dataframe for given year:
def dataframe_gazzetta(year:int):
    # Firefox driver:
    driver = webdriver.Firefox()
    driver.get(f"https://www.gazzetta.it/calcio/fantanews/statistiche/serie-a-{year-1}-{year%2000}/")
    full_table_rows = driver.find_element(By.TAG_NAME, 'table').text.split('\n')[48:]
    driver.close()
    columns = ['Giocatore', 'Ruolo', 'Quotazione', 'Partite Giocate', 'Goal', 'Assist', 'Ammonizioni', 'Espulsioni', 'Rigori Tirati', 'Rigori Segnati', 'Rigori Sbagliati', 'Rigori Parati', 'MV', 'MFV', 'Bonus/Malus']
    rows = dict()
    rows['Giocatore'] =        list()
    rows['Ruolo'] =            list()
    rows['Quotazione'] =       list()
    rows['Partite Giocate'] =  list()
    rows['Goal'] =             list()
    rows['Assist'] =           list()
    rows['Ammonizioni'] =      list()
    rows['Espulsioni'] =       list()
    rows['Rigori Tirati'] =    list()
    rows['Rigori Segnati'] =   list()
    rows['Rigori Sbagliati'] = list()
    rows['Rigori Parati'] =    list()
    rows['MV'] =               list()
    rows['MFV'] =              list()
    rows['Bonus/Malus'] =      list()
    for r in full_table_rows:
        l = r.split(' ')
        if l[1] in ['A', 'C', 'D', 'P', 'T']:
            rows['Giocatore'].append(               l[0]                               )
            if l[1] == 'T':
                rows['Ruolo'].append(               l[1] + l[2]                        )
                rows['Quotazione'].append(          int(l[3]) if l[3] != '-' else 0    )
                rows['Partite Giocate'].append(     int(l[4]) if l[4] != '-' else 0    )
                rows['Goal'].append(                int(l[5]) if l[5] != '-' else 0    )
                rows['Assist'].append(              int(l[6]) if l[6] != '-' else 0    )
                rows['Ammonizioni'].append(         int(l[7]) if l[7] != '-' else 0    )
                rows['Espulsioni'].append(          int(l[8]) if l[8] != '-' else 0    )
                rows['Rigori Tirati'].append(       int(l[9]) if l[9] != '-' else 0    )
                rows['Rigori Segnati'].append(      int(l[10]) if l[10] != '-' else 0  )
                rows['Rigori Sbagliati'].append(    int(l[11]) if l[11] != '-' else 0  )
                rows['Rigori Parati'].append(       int(l[12]) if l[12] != '-' else 0  )
                rows['MV'].append(                  float(l[13]) if l[13] != '-' else 0)
                rows['MFV'].append(                 float(l[14]) if l[14] != '-' else 0)
                rows['Bonus/Malus'].append(         float(l[15]) if l[15] != '-' else 0)
            else:
                rows['Ruolo'].append(               l[1]                               )
                rows['Quotazione'].append(          int(l[2]) if l[2] != '-' else 0    )
                rows['Partite Giocate'].append(     int(l[3]) if l[3] != '-' else 0    )
                rows['Goal'].append(                int(l[4]) if l[4] != '-' else 0    )
                rows['Assist'].append(              int(l[5]) if l[5] != '-' else 0    )
                rows['Ammonizioni'].append(         int(l[6]) if l[6] != '-' else 0    )
                rows['Espulsioni'].append(          int(l[7]) if l[7] != '-' else 0    )
                rows['Rigori Tirati'].append(       int(l[8]) if l[8] != '-' else 0    )
                rows['Rigori Segnati'].append(      int(l[9]) if l[9] != '-' else 0  )
                rows['Rigori Sbagliati'].append(    int(l[10]) if l[10] != '-' else 0  )
                rows['Rigori Parati'].append(       int(l[11]) if l[11] != '-' else 0  )
                rows['MV'].append(                  float(l[12]) if l[12] != '-' else 0)
                rows['MFV'].append(                 float(l[13]) if l[13] != '-' else 0)
                rows['Bonus/Malus'].append(         float(l[14]) if l[14] != '-' else 0)
        else:
            if l[2] in ['A', 'C', 'D', 'P', 'T']:
                rows['Giocatore'].append(           l[0] + ' ' + l[1]                  )
                if l[2] == 'T':
                    rows['Ruolo'].append(           l[2] + l[3]                        )
                    rows['Quotazione'].append(      int(l[4]) if l[4] != '-' else 0    )
                    rows['Partite Giocate'].append( int(l[5]) if l[5] != '-' else 0    )
                    rows['Goal'].append(            int(l[6]) if l[6] != '-' else 0    )
                    rows['Assist'].append(          int(l[7]) if l[7] != '-' else 0    )
                    rows['Ammonizioni'].append(     int(l[8]) if l[8] != '-' else 0    )
                    rows['Espulsioni'].append(      int(l[9]) if l[9] != '-' else 0    )
                    rows['Rigori Tirati'].append(   int(l[10]) if l[10] != '-' else 0  )
                    rows['Rigori Segnati'].append(  int(l[11]) if l[11] != '-' else 0  )
                    rows['Rigori Sbagliati'].append(int(l[12]) if l[12] != '-' else 0  )
                    rows['Rigori Parati'].append(   int(l[13]) if l[13] != '-' else 0  )
                    rows['MV'].append(              float(l[14]) if l[14] != '-' else 0)
                    rows['MFV'].append(             float(l[15]) if l[15] != '-' else 0)
                    rows['Bonus/Malus'].append(     float(l[16]) if l[16] != '-' else 0)
                else:
                    rows['Ruolo'].append(           l[2]                               )
                    rows['Quotazione'].append(      int(l[3]) if l[3] != '-' else 0    )
                    rows['Partite Giocate'].append( int(l[4]) if l[4] != '-' else 0    )
                    rows['Goal'].append(            int(l[5]) if l[5] != '-' else 0    )
                    rows['Assist'].append(          int(l[6]) if l[6] != '-' else 0    )
                    rows['Ammonizioni'].append(     int(l[7]) if l[7] != '-' else 0    )
                    rows['Espulsioni'].append(      int(l[8]) if l[8] != '-' else 0    )
                    rows['Rigori Tirati'].append(   int(l[9]) if l[9] != '-' else 0    )
                    rows['Rigori Segnati'].append(  int(l[10]) if l[10] != '-' else 0  )
                    rows['Rigori Sbagliati'].append(int(l[11]) if l[11] != '-' else 0  )
                    rows['Rigori Parati'].append(   int(l[12]) if l[12] != '-' else 0  )
                    rows['MV'].append(              float(l[13]) if l[13] != '-' else 0)
                    rows['MFV'].append(             float(l[14]) if l[14] != '-' else 0)
                    rows['Bonus/Malus'].append(     float(l[15]) if l[15] != '-' else 0)
            else:
                rows['Giocatore'].append(           l[0] + ' ' + l[1] + ' ' + l[2]     )
                if l[3] == 'T':
                    rows['Ruolo'].append(           l[3] + l[4]                        )
                    rows['Quotazione'].append(      int(l[5]) if l[5] != '-' else 0    )
                    rows['Partite Giocate'].append( int(l[6]) if l[6] != '-' else 0    )
                    rows['Goal'].append(            int(l[7]) if l[7] != '-' else 0    )
                    rows['Assist'].append(          int(l[8]) if l[8] != '-' else 0    )
                    rows['Ammonizioni'].append(     int(l[9]) if l[9] != '-' else 0    )
                    rows['Espulsioni'].append(      int(l[10]) if l[10] != '-' else 0  )
                    rows['Rigori Tirati'].append(   int(l[11]) if l[11] != '-' else 0  )
                    rows['Rigori Segnati'].append(  int(l[12]) if l[12] != '-' else 0  )
                    rows['Rigori Sbagliati'].append(int(l[13]) if l[13] != '-' else 0  )
                    rows['Rigori Parati'].append(   int(l[14]) if l[14] != '-' else 0  )
                    rows['MV'].append(              float(l[15]) if l[15] != '-' else 0)
                    rows['MFV'].append(             float(l[16]) if l[16] != '-' else 0)
                    rows['Bonus/Malus'].append(     float(l[17]) if l[17] != '-' else 0)
                else:
                    rows['Ruolo'].append(           l[3]                               )
                    rows['Quotazione'].append(      int(l[4]) if l[4] != '-' else 0    )
                    rows['Partite Giocate'].append( int(l[5]) if l[5] != '-' else 0    )
                    rows['Goal'].append(            int(l[6]) if l[6] != '-' else 0    )
                    rows['Assist'].append(          int(l[7]) if l[7] != '-' else 0    )
                    rows['Ammonizioni'].append(     int(l[8]) if l[8] != '-' else 0    )
                    rows['Espulsioni'].append(      int(l[9]) if l[9] != '-' else 0    )
                    rows['Rigori Tirati'].append(   int(l[10]) if l[10] != '-' else 0  )
                    rows['Rigori Segnati'].append(  int(l[11]) if l[11] != '-' else 0  )
                    rows['Rigori Sbagliati'].append(int(l[12]) if l[12] != '-' else 0  )
                    rows['Rigori Parati'].append(   int(l[13]) if l[13] != '-' else 0  )
                    rows['MV'].append(              float(l[14]) if l[14] != '-' else 0)
                    rows['MFV'].append(             float(l[15]) if l[15] != '-' else 0)
                    rows['Bonus/Malus'].append(     float(l[16]) if l[16] != '-' else 0)
    df = pd.DataFrame.from_dict(rows)
    return df


# Webscraper function to get gazzetta.it players list for given year:
def get_actual_players(year:int):
    # Firefox driver:
    driver = webdriver.Firefox()
    driver.get(f"https://www.gazzetta.it/calcio/fantanews/statistiche/serie-a-{year-1}-{year%2000}/")
    full_table = driver.find_element(By.TAG_NAME, 'table')
    rows = full_table.text.split('\n')[48:]
    table_blob = full_table.get_attribute("innerHTML").split('\n')
    team_for_player = [team.replace('\t','')[35:].replace('</span>','').capitalize() for team in table_blob if 'hidden-team-name' in team]
    role_for_player = [role.replace('\t','')[28:].replace('</td>','').replace(' ', '') for role in table_blob if ('field-ruolo' in role and not 'OLD' in role)][1:]
    driver.close()
    players_list = list()
    for r in rows:
        l = r.split(' ')
        if l[1] in ['A', 'C', 'D', 'P', 'T']:
            players_list.append(l[0])
        elif l[2] in ['A', 'C', 'D', 'P', 'T']:
            players_list.append(l[0] + ' ' + l[1])
        else:
            players_list.append(l[0] + ' ' + l[1] + ' ' + l[2])
    ret = np.array((players_list, team_for_player, role_for_player)).T
    return ret


# Create df with existent and new players divided by role:
def filter_data(lasty_df:pd.DataFrame, prevy_df:pd.DataFrame, players:list):
    columns = ['Giocatore', 'Squadra', 'Ruolo', 'Quotazione', 'Partite Giocate', 'Goal', 'Assist', 'Ammonizioni', 'Espulsioni', 'Rigori Tirati', 'Rigori Segnati', 'Rigori Sbagliati', 'Rigori Parati', 'MV', 'MFV', 'Bonus/Malus']
    full_df_dict = {col: list() for col in columns}
    new_players_dict = {col: list() for col in columns[:3]}
    full_df_dict['Giocatore'] = list(players[:,0])
    full_df_dict['Squadra'] = list(players[:,1])
    full_df_dict['Ruolo'] = list(players[:,2])
    lasty_pl = lasty_df['Giocatore']
    prevy_pl = prevy_df['Giocatore']
    erase_list = list()
    for i,p in enumerate(full_df_dict['Giocatore']):
        if (p in lasty_pl) and (p in prevy_df):
            pass 
        elif p in lasty_pl:
            pass
        elif p in prevy_pl:
            pass
        else:
            new_players_dict['Giocatore'].append(full_df_dict['Giocatore'][i])
            new_players_dict['Squadra'].append(full_df_dict['Squadra'][i])
            new_players_dict['Ruolo'].append(full_df_dict['Ruolo'][i])
            erase_list.append(i)
    for i in erase_list.reverse():
        for c in columns:
            full_df_dict[c].pop(i)
    new_players_df = pd.DataFrame.from_dict(new_players_dict)
    old_players_df = pd.DataFrame.from_dict(full_df_dict)
    exit()
    return atk, cen, dif, por, new_atk, new_cen, new_dif, new_por


# Arguments parser:
def parse_args():
    # Parser initialization:
    parser = argparse.ArgumentParser()
    # ARGUMENT EXAMPLE:
    # parser.add_argument('--clock', type=str, default='cus', choices=clock_choices, help='Desired clock configuration.')
    # Compute bool:
    parser.add_argument('--compute', action='store_true', help='To compute the data and fill the SQLite3 database.')
    # Last finished championship year:
    parser.add_argument('--year', type=int, default=2022, help='Last finished championship year.')
    # Parsed args return:
    return parser.parse_args()


# Write table to SQL:
def write_df_to_db(df:pd.DataFrame, table_name:str):
    global db
    # Push the dataframe to sql:
    df.to_sql(table_name, db, if_exists="replace", index=False)
    # Create the table:
    # db.execute(
    #     f"""
    #     create table {table_name} as 
    #     select * from {table_name}
    #     """)


# Read DB table from SQL:
def read_df_from_db(table_name:str):
    global db
    # Extract df table from db:
    return pd.read_sql_query(f'select * from {table_name}', db)


# Main Function:
def main():
    # Parse given arguments:
    args = parse_args()
    # Championship estimation:
    # classifica = stima_campionato()
    # write_df_to_db(df=classifica, table_name='Classifica')
    # classifica = read_df_from_db(table_name='Classifica')
    # print(classifica)
    # exit()
    # Get gazzetta.it data for last championship:
    # last_year_df = dataframe_gazzetta(args.year)
    # print(last_year_df)
    # Get gazzetta.it data for previous championship:
    # previous_year_df = dataframe_gazzetta(args.year-1)
    # print(previous_year_df)
    # Get actual championship players:
    players = get_actual_players(args.year+1)
    print(players)

    # filter_data(last_year_df, previous_year_df, players)
    exit()
    # Create df with existent players divided by role and new players list:
    atk, cen, dif, por, new_atk, new_cen, new_dif, new_por = filter_data(last_year_df, previous_year_df, players)


# Main script:
if __name__ == '__main__':
    main()
