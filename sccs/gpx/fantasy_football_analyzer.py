# -*- coding: utf-8 -*-
"""
Created on Sun Aug 29 20:42:59 2021

@author: A485753
"""

import requests
import pandas as pd
import numpy as np
from pprint import pprint


def get_bootstrap_static(item='Player'):
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    r = requests.get(url)
    json = r.json()
    
    
    elements_df = pd.DataFrame(json['elements'])
    elements_types_df = pd.DataFrame(json['element_types'])
    teams_df = pd.DataFrame(json['teams'])
    
    elements_df['position'] = elements_df.element_type.map(elements_types_df.set_index('id').singular_name)
    elements_df['team'] = elements_df.team.map(teams_df.set_index('id').name)
    
    if item == 'Player':
        return elements_df
    if item == 'Team':
        print(teams_df.info())
        return teams_df


def get_fixtures(match_id):
    """Match ID mellom 0,380  """
    url = 'https://fantasy.premierleague.com/api/fixtures/'
    r = requests.get(url)
    json = r.json()

    fixture_df = pd.DataFrame(json[match_id])
    # Usikker på hvorfor den printer det ut 10 ganger...
    return fixture_df.head(1)


def pretty_print_fixture(match_id): 
    teams_df = get_bootstrap_static(item='Team')
    matches_df = pd.DataFrame()
    
    for match in range(1,60):
        event_df = get_fixtures(match)

        event_df['team_h_name'] = event_df['team_h'].map(teams_df.set_index('id').name)
        event_df['team_a_name'] = event_df['team_a'].map(teams_df.set_index('id').name)
        event_df['strength_overall_home'] = event_df['team_h'].map(teams_df.set_index('id').strength_overall_home)
        event_df['strength_overall_away'] = event_df['team_a'].map(teams_df.set_index('id').strength_overall_away)
        event_df['strength_attack_home'] = event_df['team_h'].map(teams_df.set_index('id').strength_attack_home)
        event_df['strength_attack_away'] = event_df['team_a'].map(teams_df.set_index('id').strength_attack_away)
        event_df['strength_defence_home'] = event_df['team_h'].map(teams_df.set_index('id').strength_defence_home)
        event_df['strength_defence_away'] = event_df['team_a'].map(teams_df.set_index('id').strength_defence_away)
        event_df['strengt_diff'] =event_df['strength_overall_home']-event_df['strength_overall_away']
        event_df['home_team_score_diff'] = event_df['strength_attack_home']-event_df['strength_defence_away']
        event_df['away_team_score_diff'] = event_df['strength_attack_away']-event_df['strength_defence_home']
        event_df['match_difficulty'] = event_df['team_h_difficulty'] -event_df['team_a_difficulty']
        
        event_df['score_diff'] = event_df['team_h_score'] - event_df['team_a_score']
        
        
        matches_df = pd.concat([matches_df,event_df])
    
    
    matches_df.plot(x='team_a_score',y='away_team_score_diff',style='o')
    print(matches_df[['team_h_name','team_a_name','match_difficulty','strengt_diff']].sort_values('strengt_diff'))



def get_event(GW):
    url = 'https://fantasy.premierleague.com/api/event/{}/live/'.format(str(GW))
    r = requests.get(url)
    json = r.json()
    
    event_df = pd.DataFrame(json['elements'])
    gw_database = []
    
    for player in event_df['stats']:
        gw_database.append(player)

    gw_database_df = pd.DataFrame(gw_database)
    return gw_database_df[['total_points']]


def checkMyTeam():
    new_df = pd.DataFrame()
    gw_a =7
    gw_b =12
    period = gw_b-gw_a
    for i in range(gw_a,gw_b):
        tmp_df = get_event(i)
        new_df = pd.concat([new_df,tmp_df],axis=1)
        new_df['GW'+str(i)] =  tmp_df['total_points'] 
    
    new_df = new_df.drop(columns='total_points')
    new_df['Total'] =   new_df.sum(axis=1,skipna=True)/period
    
    players_df = get_bootstrap_static()

    players_df['id'] = players_df['id']-1

    new_df['first_name'] = new_df.index.map(players_df
                                            .set_index('id')
                                            .first_name)
    new_df['second_name'] = new_df.index.map(players_df
                                             .set_index('id')
                                             .second_name)
    new_df['team'] = new_df.index.map(players_df
                                      .set_index('id')
                                      .team)
    new_df['position'] = new_df.index.map(players_df
                                          .set_index('id')
                                          .position)
    new_df['total_points'] = new_df.index.map(players_df
                                              .set_index('id')
                                              .total_points)
    new_df['now_cost'] = new_df.index.map(players_df
                                          .set_index('id')
                                          .now_cost)
    new_df['chance_of_playing_this_round'] = new_df.index.map(players_df
                                                   .set_index('id')
                                                   .chance_of_playing_this_round)
    new_df['selected_by_percent'] = new_df.index.map(players_df
                                                     .set_index('id')
                                                     .selected_by_percent)
    new_df['id'] = new_df.index
    
    
    new_df['myValue'] = new_df['Total']/new_df['now_cost']*100
    
    new_df = new_df.sort_values('myValue',ascending=False).reset_index()
    myTeam = [288, 90, 204, 418, 239, 352, 79, 55, 483, 
              120, 582, 232, 258, 429]
    mySwap = [80,244,271,412,121,336]
    
    
    myTeam2 = pd.DataFrame()
    for player in myTeam:
        playerInfo = new_df[new_df['id']==player][['id','first_name','second_name','myValue','Total',"team"]]
        myTeam2 = pd.concat([myTeam2,playerInfo])
    
    print(myTeam2.sort_values('myValue',ascending=False))

    print('\nTransferred')
    myTeam2 = pd.DataFrame()
    
    for player in mySwap:
        playerInfo = new_df[new_df['id']==player][['id','first_name','second_name','myValue','Total',"team"]]
        myTeam2 = pd.concat([myTeam2,playerInfo])
    
    print(myTeam2.sort_values('myValue',ascending=False))    
    
    print('\n New Player')
    
    new_df2 = new_df[new_df['position'] == 'Midfielder']
    new_df2 = new_df2[new_df2['now_cost'] >= 40]
    new_df2 = new_df2[new_df2['now_cost'] <= 50]
#    new_df2 = new_df2[new_df2['team'] == 'Man City']
    print(new_df2[['team','second_name','myValue','Total','now_cost']].head(20).sort_values('Total',ascending=False))

def findBestTeam2():
    # Define teams setup
    c_goalkeeper = 1
    c_defender = 1
    c_midfielder = 1
    c_forward = 1

    # Define weeks
    gw_a = 15
    gw_b = 23
    period = gw_b-gw_a
    
    max_prize = 100 - (15-c_goalkeeper-c_defender-c_midfielder-c_forward)*4
    max_prize = 27.4
    
    
    new_df = pd.DataFrame()
    for i in range(gw_a, gw_b):
        tmp_df = get_event(i)
        new_df = pd.concat([new_df, tmp_df], axis=1)
        new_df['GW'+str(i)] = tmp_df['total_points']

    new_df = new_df.drop(columns='total_points')
    new_df['Total'] =   new_df.sum(axis=1,skipna=True)/period
    
    players_df = get_bootstrap_static()

    players_df['id'] = players_df['id']-1
    
    df_headers = ['first_name', 'second_name', 'team', 'position', 
                  'total_points', 'now_cost', 'chance_of_playing_this_round', 
                  'selected_by_percent']
    
    for colName in df_headers: 
        new_df[colName] = new_df.index.map(players_df.set_index('id')[colName])
    new_df['id'] = new_df.index
    
    
    new_df['myValue'] = new_df['Total']/new_df['now_cost']*100
    new_df['myValue'] = new_df['Total']/new_df['now_cost']*100
    new_df = new_df.sort_values('Total',ascending=False).reset_index()

    print(new_df[['second_name', 'position', 'Total',
                  'total_points', 'myValue']].head(15))
    
    preferredTeams = getPreferredTeams('all')
    removedPlayers = removePlayers('')
    print(removedPlayers)
    
    new_df = new_df[new_df['team'].isin(preferredTeams)]
    new_df = new_df[~new_df['second_name'].isin(removedPlayers)]
    new_df = new_df.sort_values('Total',ascending=False).reset_index()
    print(new_df[['second_name', 'position', 'Total',
                  'total_points', 'myValue']].head(15))

    teamSetup = {'Goalkeeper': c_goalkeeper,
                 'Defender': c_defender,
                 'Midfielder': c_midfielder,
                 'Forward': c_forward}
    
    c_players = c_goalkeeper+c_defender+c_midfielder+c_forward


    bestTeam_df = pd.DataFrame()
    
    j = 0
    while len(bestTeam_df) < c_players:
        
        if checkTeamCount(bestTeam_df, new_df[j:j+1]) and checkTeamPos(bestTeam_df, new_df[j:j+1], teamSetup):
            bestTeam_df = pd.concat([bestTeam_df, new_df[j:j+1]], axis=0)
            
            new_df = new_df.drop(j)
            new_df.reset_index(drop=True, inplace=True)
            j = 0
            
        else:
            j += 1
            print('No player added')
            
        
    bestTeam_df.sort_values('myValue', ascending=False, inplace=True )
    bestTeam_df.reset_index(drop=True, inplace=True)
    print(bestTeam_df)
    
    print('Original best Team\n')
    print(bestTeam_df[['second_name', 'index', 'Total',
                       'position', 'team']])
    
    print(bestTeam_df['now_cost'].head(c_players).sum()/10,'< maxPrice: ', max_prize)    
    print('Total poeng: ',bestTeam_df['Total'].head(c_players).sum()*period)
    swappedPlayers_df = pd.DataFrame()
    
    u = 0
    v = 1
    
    for i in range(30):

        swapPlayerOut = bestTeam_df[len(bestTeam_df)-v : len(bestTeam_df)-v+1]
        swapPos = swapPlayerOut.iloc[0]['position']
        swapCost = swapPlayerOut.iloc[0]['now_cost']
        swapMyVal = swapPlayerOut.iloc[0]['myValue']
    
        
        swap_df = new_df[new_df['position'] == swapPos]
        swap_df = swap_df[swap_df['now_cost'] < swapCost]
        swap_df = swap_df[swap_df['myValue'] > swapMyVal]
        swap_df.reset_index(drop=True, inplace=True)
        
        if len(swap_df) == 0:
            print('\n\nERROR - Not able to switch')
            v += 1
            continue
        
        swapPlayerIn = swap_df[u:u+1]
        print('\nAntall kandidater:',len(swap_df))
        print('Player out:')
        print(swapPlayerOut[['second_name', 'index', 'Total', 'position', 'now_cost']])
        print('Player in:')
        print(swapPlayerIn[['second_name', 'index', 'Total', 'position', 'now_cost']])
        
        swapInIndex = swapPlayerIn.iloc[0]['index']
    
        temp_df = bestTeam_df.drop(c_players-v).copy()
        
        if checkTeamCount(temp_df,swapPlayerIn):
            bestTeam_df = pd.concat([temp_df,swapPlayerIn], axis=0)
            swappedPlayers_df = pd.concat([swappedPlayers_df,swapPlayerOut],axis=0)
            new_df = new_df.drop(new_df[new_df['index'] == swapInIndex].index)
            
            u = 0
            v = 1
            
        else:
            u+=1 
            
        
        bestTeam_df.sort_values('myValue', ascending=False, inplace=True )
        bestTeam_df.reset_index(drop=True, inplace=True)
        print(bestTeam_df['now_cost'].head(c_players).sum()/10,'< maxPrice: ', max_prize)
        

        if bestTeam_df['now_cost'].head(c_players).sum()/10 < max_prize:
            break

    bestTeam_df.sort_values('position', ascending=False, inplace=True )
    bestTeam_df.reset_index(drop=True, inplace=True)    
    print('\nSecond best Team')
    print(bestTeam_df[['first_name','second_name', 'team', 'Total', 'position', 'now_cost']])
    print(bestTeam_df['now_cost'].head(c_players).sum()/10,'< maxPrice: ', max_prize)
    print('Total poeng: ',bestTeam_df['Total'].head(c_players).sum()*period)
               
    
    print('\n')
    print(swappedPlayers_df[['second_name', 'team', 'Total', 'position', 'now_cost']])
    



def checkTeamCount(df_team,player):
    if len(df_team) < 1:
        return True
    
    pTeam = player['team'].iloc(0)[0]
    teamVal = df_team['team'].value_counts()

    if pTeam in teamVal.index:
        if teamVal[pTeam]>2:
            return False
        else:
            return True
    
    else:
        return True

def checkTeamPos(df_team,player,teamSetup):
    pPos = player['position'].iloc(0)[0]
    
    if len(df_team) < 1 and teamSetup[pPos] > 0:
        print(pPos)
        return True
    if len(df_team) < 1 and teamSetup[pPos] == 0:
        return False   
    
    
    teamVal = df_team['position'].value_counts()
    
    if pPos in teamVal.index:
        if teamVal[pPos] >= teamSetup[pPos]:
            return False

        else:
            return True

    else:
        if teamSetup[pPos] == 0:
            return False
        else:
            return True
    
    print('checkTeamPos Failed!!')
    return True

def getPreferredTeams(arg):
    teams_dict = {
        'Arsenal'       : 1,
        'Aston Villa'   : 0,
        'Brentford'     : 0,
        'Brighton'      : 0,
        'Burnley'       : 0,
        'Chelsea'       : 0,
        'Crystal Palace': 0,
        'Everton'       : 0,
        'Leeds'         : 0,
        'Leicester'     : 0,
        'Liverpool'     : 0,
        'Man City'      : 1,
        'Man Utd'       : 0,
        'Newcastle'     : 0,
        'Norwich'       : 0,
        'Southampton'   : 0,
        'Spurs'         : 0,
        'Watford'       : 0,
        'West Ham'      : 0,
        'Wolves'        : 0,
        }
    
    teams_list = []
    if arg == 'all':
        for val in teams_dict:        
            teams_list.append(val)
    else:
        for val in teams_dict:
            if teams_dict[val] == 1:
                teams_list.append(val)
            
    return teams_list       
            
def removePlayers(arg):
    player_dict = {
        'Haaland'       : 1,
        'Cancelo'       : 1,
        'Toney'         : 1
        }
    
    player_list = []
    if arg == 'none':
        return []
    else:
        for val in player_dict:
            if player_dict[val] == 1:
                player_list.append(val)
            
    return player_list 
    

def findPointsInRound(team, captain, gwa,gwb):
    
    new_df = pd.DataFrame()
    gw_a =gwa
    gw_b =gwb
    period = gw_b-gw_a
    
    for i in range(gw_a,gw_b):
        tmp_df = get_event(i)
        new_df = pd.concat([new_df,tmp_df],axis=1)
        new_df['GW'+str(i)] =  tmp_df['total_points'] 
    
    new_df = new_df.drop(columns='total_points')
    new_df['Total'] =   new_df.sum(axis=1,skipna=True)/period
    
    players_df = get_bootstrap_static()

    players_df['id'] = players_df['id']-1
    
    
    new_df['first_name'] = new_df.index.map(players_df.set_index('id').first_name)
    new_df['second_name'] = new_df.index.map(players_df.set_index('id').second_name)
    new_df['team'] = new_df.index.map(players_df.set_index('id').team)
    new_df['position'] = new_df.index.map(players_df.set_index('id').position)
    new_df['total_points'] = new_df.index.map(players_df.set_index('id').total_points)
    new_df['now_cost'] = new_df.index.map(players_df.set_index('id').now_cost)
    new_df['chance_of_playing_this_round'] = new_df.index.map(players_df.set_index('id').chance_of_playing_this_round)
    new_df['selected_by_percent'] = new_df.index.map(players_df.set_index('id').selected_by_percent)
    new_df['id'] = new_df.index
    
    sumTeam = 0
    
    for player in team:
        sumTeam += new_df.loc[(new_df['id']==player),'Total'].values[0]
        
    sumTeam += new_df.loc[(new_df['id']==captain),'Total'].values[0]
   
    print(sumTeam)


findBestTeam2()
