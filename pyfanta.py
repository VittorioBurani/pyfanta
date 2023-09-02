import os
import re
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
    rows = {
        'Giocatore':        list(),
        'Ruolo':            list(),
        'Quotazione':       list(),
        'Partite Giocate':  list(),
        'Goal':             list(),
        'Assist':           list(),
        'Ammonizioni':      list(),
        'Espulsioni':       list(),
        'Rigori Tirati':    list(),
        'Rigori Segnati':   list(),
        'Rigori Sbagliati': list(),
        'Rigori Parati':    list(),
        'MV':               list(),
        'MFV':              list(),
        'Bonus/Malus':      list(),
    }
    # Loop through table:
    for r in full_table_rows:
        # Get Player name:
        player_name = re.findall(r'^.+?(?=\s[PDCTA]\s)', r)[0]
        rows['Giocatore'].append(player_name)
        partial_row = r[len(player_name)+1:]
        # Get Player Role:
        player_role = re.findall(r'^[PDCTA]{1}(?:\s\([PCA]\)){0,1}', partial_row)[0]
        player_role = player_role.replace(' (P)','')
        rows['Ruolo'].append(player_role)
        partial_row = partial_row[len(player_role)+1:]
        # Get all other data:
        l = partial_row.split(' ')
        rows['Quotazione'].append(          int(l[0])    if l[0]  != '-' else 0)
        rows['Partite Giocate'].append(     int(l[1])    if l[1]  != '-' else 0)
        rows['Goal'].append(                int(l[2])    if l[2]  != '-' else 0)
        rows['Assist'].append(              int(l[3])    if l[3]  != '-' else 0)
        rows['Ammonizioni'].append(         int(l[4])    if l[4]  != '-' else 0)
        rows['Espulsioni'].append(          int(l[5])    if l[5]  != '-' else 0)
        rows['Rigori Tirati'].append(       int(l[6])    if l[6]  != '-' else 0)
        rows['Rigori Segnati'].append(      int(l[7])    if l[7]  != '-' else 0)
        rows['Rigori Sbagliati'].append(    int(l[8])    if l[8]  != '-' else 0)
        rows['Rigori Parati'].append(       int(l[9])    if l[9]  != '-' else 0)
        rows['MV'].append(                  float(l[10]) if l[10] != '-' else 0)
        rows['MFV'].append(                 float(l[11]) if l[11] != '-' else 0)
        rows['Bonus/Malus'].append(         float(l[12]) if l[12] != '-' else 0)
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
    driver.close()
    players_list    = [re.findall(r'^.+?(?=\s[PDCTA]\s)', r)[0] for r in rows]
    team_for_player = [team.replace('\t','')[35:].replace('</span>','').capitalize() for team in table_blob if 'hidden-team-name' in team]
    role_for_player = [role.replace('\t','')[28:].replace('</td>','').replace('(P)','').replace(' ', '') for role in table_blob if ('field-ruolo' in role and not 'OLD' in role)][1:]
    quot_for_player = [int(quot.replace('\t','')[38:].replace('</td>','').replace(' ', '')) for quot in table_blob if 'field-q selectedField' in quot]
    ret = np.array((players_list, team_for_player, role_for_player, quot_for_player)).T
    return ret


# Create df with existent and new players divided by role:
def filter_data(lasty_df:pd.DataFrame, prevy_df:pd.DataFrame, players:list):
    columns = ['Giocatore', 'Squadra', 'Ruolo', 'Quotazione', 'Partite Giocate', 'Goal', 'Assist', 'Ammonizioni', 'Espulsioni', 'Rigori Tirati', 'Rigori Segnati', 'Rigori Sbagliati', 'Rigori Parati', 'MV', 'MFV', 'Bonus/Malus']
    full_df_dict = {col: list() for col in columns}
    new_players_dict = {col: list() for col in columns[:4]}
    act_pl = list(players[:,0])
    lasty_pl = list(lasty_df['Giocatore'])
    prevy_pl = list(prevy_df['Giocatore'])
    for i,p in enumerate(act_pl):
        if (p in lasty_pl) and (p in prevy_pl):
            # Old players:
            full_df_dict['Giocatore'].append(players[i,0])
            full_df_dict['Squadra'].append(players[i,1])
            full_df_dict['Ruolo'].append(players[i,2])
            full_df_dict['Quotazione'].append(players[i,3])
            ly_serie = lasty_df.loc[lasty_df['Giocatore'] == p]
            py_serie = prevy_df.loc[prevy_df['Giocatore'] == p]
            for col in columns[4:]:
                if col in ('MV', 'MFV'):
                    ly_totv = ly_serie['Partite Giocate'].iloc[0] * ly_serie[col].iloc[0]
                    py_totv = py_serie['Partite Giocate'].iloc[0] * py_serie[col].iloc[0]
                    res = (ly_totv + py_totv) / (ly_serie['Partite Giocate'].iloc[0] + py_serie['Partite Giocate'].iloc[0]) if (ly_totv + py_totv) else 0
                    full_df_dict[col].append(float(f'{res:.2f}'))
                else:
                    full_df_dict[col].append(ly_serie[col].iloc[0]+py_serie[col].iloc[0])
        elif p in lasty_pl:
            # Old players:
            full_df_dict['Giocatore'].append(players[i,0])
            full_df_dict['Squadra'].append(players[i,1])
            full_df_dict['Ruolo'].append(players[i,2])
            full_df_dict['Quotazione'].append(players[i,3])
            ly_serie = lasty_df.loc[lasty_df['Giocatore'] == p]
            for col in columns[4:]:
                full_df_dict[col].append(ly_serie[col].iloc[0])
        elif p in prevy_pl:
            # Old players:
            full_df_dict['Giocatore'].append(players[i,0])
            full_df_dict['Squadra'].append(players[i,1])
            full_df_dict['Ruolo'].append(players[i,2])
            full_df_dict['Quotazione'].append(players[i,3])
            py_serie = prevy_df.loc[prevy_df['Giocatore'] == p]
            for col in columns[4:]:
                full_df_dict[col].append(py_serie[col].iloc[0])
        else:
            # New players:
            new_players_dict['Giocatore'].append(players[i,0])
            new_players_dict['Squadra'].append(players[i,1])
            new_players_dict['Ruolo'].append(players[i,2])
            new_players_dict['Quotazione'].append(players[i,3])
    new_players_df = pd.DataFrame.from_dict(new_players_dict)
    old_players_df = pd.DataFrame.from_dict(full_df_dict)
    atk = old_players_df.loc[(old_players_df['Ruolo'] == 'A') | (old_players_df['Ruolo'] == 'T(A)')]
    cen = old_players_df.loc[(old_players_df['Ruolo'] == 'C') | (old_players_df['Ruolo'] == 'T(C)')]
    dif = old_players_df.loc[old_players_df['Ruolo'] == 'D']
    por = old_players_df.loc[old_players_df['Ruolo'] == 'P']
    new_atk = new_players_df.loc[(new_players_df['Ruolo'] == 'A') | (new_players_df['Ruolo'] == 'T(A)')]
    new_cen = new_players_df.loc[(new_players_df['Ruolo'] == 'C') | (new_players_df['Ruolo'] == 'T(C)')]
    new_dif = new_players_df.loc[new_players_df['Ruolo'] == 'D']
    new_por = new_players_df.loc[new_players_df['Ruolo'] == 'P']
    print(atk, cen, dif, por, new_atk, new_cen, new_dif, new_por)
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
    # Create csv file with general data:
    parser.add_argument('--general-csv', action='store_true', help='Create csv file with general tables data.')
    # Parsed args return:
    return parser.parse_args()


# Write table to SQL:
def write_df_to_db(df:pd.DataFrame, table_name:str):
    global db
    # Push the dataframe to sql:
    df.to_sql(table_name, db, if_exists="replace", index=False)


# Read DB table from SQL:
def read_df_from_db(table_name:str):
    global db
    # Extract df table from db:
    return pd.read_sql_query(f'select * from {table_name}', db)


# Main Function:
def main():
    # Parse given arguments:
    args = parse_args()
    # Compute tables:
    if args.compute:
        # Championship estimation:
        classifica = stima_campionato()
        write_df_to_db(df=classifica, table_name='Classifica')
        # Get gazzetta.it data for last championship:
        last_year_df = dataframe_gazzetta(args.year)
        # Get gazzetta.it data for previous championship:
        previous_year_df = dataframe_gazzetta(args.year-1)
        # Get actual championship players:
        players = get_actual_players(args.year+1)
        # Create df with existent players divided by role and new players list:
        atk, cen, dif, por, new_atk, new_cen, new_dif, new_por = filter_data(last_year_df, previous_year_df, players)
        write_df_to_db(df=atk, table_name='Attaccanti')
        write_df_to_db(df=cen, table_name='Centrocampisti')
        write_df_to_db(df=dif, table_name='Difensori')
        write_df_to_db(df=por, table_name='Portieri')
        write_df_to_db(df=new_atk, table_name='Nuovi_Attaccanti')
        write_df_to_db(df=new_cen, table_name='Nuovi_Centrocampisti')
        write_df_to_db(df=new_dif, table_name='Nuovi_Difensori')
        write_df_to_db(df=new_por, table_name='Nuovi_Portieri')
    # Genrate general csv data:
    if args.general_csv:
        # Table names:
        tables_name = ['Classifica', 'Attaccanti', 'Centrocampisti', 'Difensori', 'Portieri', 'Nuovi_Attaccanti', 'Nuovi_Centrocampisti', 'Nuovi_Difensori', 'Nuovi_Portieri']
        # Path to stats dir:
        stats_dirpath = os.path.join(os.curdir, 'fantastats/')
        # Generate csv with data tables:
        for i in tables_name:
            read_df_from_db(table_name=i).to_csv(stats_dirpath + i + '.csv', index=False)

# Main script:
if __name__ == '__main__':
    main()
