import numpy as np
import pandas as pd
import argparse
import sqlite3

sheet_id = '1-aqSXdI8ErfIp9mEe6K_FZ7HgzLw47-dUVHlzGpIq6k'

sheet_name = 'griglia'
path = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
griglia_portieri = pd.read_csv(path)

sheet_name = 'vincenti'
path = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
stima_vincenti = pd.read_csv(path)

sheet_name = 'stats_gazzetta'
path = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
stats_gazzetta = pd.read_csv(path)
stats_gazzetta = stats_gazzetta[stats_gazzetta['Partite Giocate'] >= 10]

sheet_name = 'stats_fantacalcio'
path = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
stats_fantacalcio = pd.read_csv(path)
stats_fantacalcio = stats_fantacalcio[stats_fantacalcio['Partite Giocate'] >= 10]

squadre = list(stima_vincenti.columns)

for i in range(0,len(squadre)):
    for j in range(i+1,len(squadre)):
        if i < j:
            stima_vincenti[squadre[j]][i] *= -1



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

def sorter(v):
    for i in range(0, len(v)-1):
        for j in range (i+1, len(v)):
            if v[i][1] <= v[j][1]:
                t = v[i]
                v[i] = v[j]
                v[j] = t
    return v

def stima_campionato():
    classifica = [[squadre[i], 0] for i in range(0, len(squadre))]
    for i in range(0,len(squadre)):
        for j in range(0, len(squadre)):
            classifica[i][1] += punti(-stima_vincenti[squadre[j]][i])
    return sorter(classifica)



def posizione(c, s):
    for i in range(0, len(squadre)):
        if s == c[i][0]:
            return i+1

def coppie_portieri():
    classifica = stima_campionato()
    coppie = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }
    for i in range(0, len(squadre)):
        for j in range(i+1, len(squadre)):
            if griglia_portieri[squadre[i]][j] == 0:
                coppie[0].append([squadre[i], squadre[j], posizione(classifica, squadre[i]), posizione(classifica, squadre[j])])
            elif griglia_portieri[squadre[i]][j] == 1:
                coppie[1].append([squadre[i], squadre[j], posizione(classifica, squadre[i]), posizione(classifica, squadre[j])])
            elif griglia_portieri[squadre[i]][j] == 2:
                coppie[2].append([squadre[i], squadre[j], posizione(classifica, squadre[i]), posizione(classifica, squadre[j])])
            elif griglia_portieri[squadre[i]][j] == 3:
                coppie[3].append([squadre[i], squadre[j], posizione(classifica, squadre[i]), posizione(classifica, squadre[j])])
            elif griglia_portieri[squadre[i]][j] == 4:
                coppie[4].append([squadre[i], squadre[j], posizione(classifica, squadre[i]), posizione(classifica, squadre[j])])
            elif griglia_portieri[squadre[i]][j] == 5:
                coppie[5].append([squadre[i], squadre[j], posizione(classifica, squadre[i]), posizione(classifica, squadre[j])])
    for i in range(0,6):
        if coppie[i]:
            popper = []
            for j in range(0, len(coppie[i])):
                if coppie[i][j][2]+coppie[i][j][3] > 19:
                    popper.append(j)
            for j in range(-len(popper)+1,1):
                coppie[i].pop(popper[-j])
    return coppie



def dataframe_gazzetta():
    portieri = stats_gazzetta[stats_gazzetta['Ruolo'] == 'P']
    portieri = portieri.sort_values(by='MFV', ascending=False)
    portieri.to_excel('fantastats/portieri_gazzetta.xlsx', index=False)

    difensori = stats_gazzetta[stats_gazzetta['Ruolo'] == 'D']
    difensori = difensori.sort_values(by='MFV', ascending=False)
    difensori.to_excel('fantastats/difensori_gazzetta.xlsx', index=False)

    centrocampisti = stats_gazzetta[(stats_gazzetta['Ruolo'] == 'C') | (stats_gazzetta['Ruolo'] == 'T (C)')]
    centrocampisti = centrocampisti.sort_values(by='MFV', ascending=False)
    centrocampisti.to_excel('fantastats/centrocampisti_gazzetta.xlsx', index=False)

    attaccanti = stats_gazzetta[(stats_gazzetta['Ruolo'] == 'A') | (stats_gazzetta['Ruolo'] == 'T (A)')]
    attaccanti = attaccanti.sort_values(by='MFV', ascending=False)
    attaccanti.to_excel('fantastats/attaccanti_gazzetta.xlsx', index=False)


def dataframe_fantacalcio():
    portieri = stats_fantacalcio[stats_fantacalcio['Ruolo'] == 'P']
    portieri = portieri.sort_values(by='MFV', ascending=False)
    portieri.to_excel('fantastats/portieri_fantacalcio.xlsx', index=False)

    difensori = stats_fantacalcio[stats_fantacalcio['Ruolo'] == 'D']
    difensori = difensori.sort_values(by='MFV', ascending=False)
    difensori.to_excel('fantastats/difensori_fantacalcio.xlsx', index=False)

    centrocampisti = stats_fantacalcio[(stats_fantacalcio['Ruolo'] == 'C') | (stats_fantacalcio['Ruolo'] == 'T (C)')]
    centrocampisti = centrocampisti.sort_values(by='MFV', ascending=False)
    centrocampisti.to_excel('fantastats/centrocampisti_fantacalcio.xlsx', index=False)

    attaccanti = stats_fantacalcio[(stats_fantacalcio['Ruolo'] == 'A') | (stats_fantacalcio['Ruolo'] == 'T (A)')]
    attaccanti = attaccanti.sort_values(by='MFV', ascending=False)
    attaccanti.to_excel('fantastats/attaccanti_fantacalcio.xlsx', index=False)


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



if __name__ == '__main__':
    classifica = stima_campionato()
    coppie = coppie_portieri()

    classifica_dict = {
        'Squadra': [],
        'Punteggio': []
    }
    for i in classifica:
        classifica_dict["Squadra"].append(i[0])
        classifica_dict["Punteggio"].append(i[1])
    classifica = pd.DataFrame(classifica_dict)
    classifica.to_excel('fantastats/classifica.xlsx', index=False)

    coppie_dict = {
        'Partite in comune': [],
        'Squadra 1': [],
        'Squadra 2': [],
        'Piazzamento 1': [],
        'Piazzamento 2': []
    }
    for i in range(0,6):
        if coppie[i]:
            for j in range(len(coppie[i])):
                coppie_dict['Partite in comune'].append(i)
                coppie_dict['Squadra 1'].append(coppie[i][j][0])
                coppie_dict['Squadra 2'].append(coppie[i][j][1])
                coppie_dict['Piazzamento 1'].append(coppie[i][j][2])
                coppie_dict['Piazzamento 2'].append(coppie[i][j][3])
    coppie = pd.DataFrame(coppie_dict)
    coppie.to_excel('fantastats/coppie_portieri.xlsx', index=False)

    dataframe_gazzetta()
    dataframe_fantacalcio()
