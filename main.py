# Read the README.md file before starting

import pandas as pd
import inquirer
import requests

#Get Value from user
def GetinputCheckBox(choiceid,message,choices):
        questions=[
                inquirer.Checkbox(choiceid,
                              message=message,
                              choices=choices,)]
        return inquirer.prompt(questions)
def GetinputText(choiceid,message):
        questions=[
                inquirer.Text(choiceid,
                              message=message,)]
        Text_entered = inquirer.prompt(questions)[choiceid].replace(' ','').split(',')
        Text_entered=[x.lower() for x in Text_entered]
        return Text_entered

#**********************      CHAMPION SELECTION     *************
#Get the file with the dictionnary of Champion Stats
def requestsChampionDf():
        URL_champion = 'http://ddragon.leagueoflegends.com/cdn/11.15.1/data/en_US/championFull.json'
        response = requests.get(URL_champion)
        return response.json()

#Create a dataFrame with the Champion description and Stats
responseJSON=requestsChampionDf()
Champion_Df=pd.DataFrame(columns=responseJSON['data']['Aatrox'].keys())
for key in responseJSON['data'].keys():
        Champion_Df=Champion_Df.append(pd.DataFrame([responseJSON['data'][key]]),ignore_index=True)
Champion_Df['key']=Champion_Df['key'].astype(str).astype(int)


#Draft Position
Role = GetinputCheckBox('role','Which position do you want to play ? ',['TOP','JUNGLE','MIDDLE','BOTTOM','UTILITY'])['role']
print(Role)

#Champion type
AllTag=['Fighter','Tank','Mage','Assassin','Marksman','Support']
Tag=GetinputCheckBox('tag','Which type of champion do you want to play ? ',AllTag)['tag']
print(Tag)

#Ability
Ability = GetinputText('ability','What ability do you want ? ex : stun,dash etc...')
print(Ability)


#Filter to get the champion with the right Tag
count_Tag=[]
if len(Tag)==0:
        Tag=AllTag
for label, row in Champion_Df.iterrows():
        if any(item in Tag for item in row['tags']):
                count_Tag.append(row['name'])

#Filter to get the champion's ability
Crowd_Control=['Knock','Stun','Fear','Charm','Slow','Disabl','Pull','Silenc','Root',
               'Taunt','Airbone','Asleep','Polymorph','Suppresse','Immobiliz','Disarmed','Ground','Blind']
Dict_Crowd_Control = {'stun':['Stun','Root','Asleep','Immobiliz','Ground','Charm'],
                      'knock':['Knock','Airbone','Pull'],
                      'fear':['Fear'],
                      'disable':['Disabl'],
                      'silence':['Silence','Suppresse'],
                      'taunt':['Taunt'],
                      'polymorph':['Polymorph'],
                      'disarmed':['Disarmed'],
                      'blind':['Blind']}
for item in Ability:
        if item in Dict_Crowd_Control.keys():
                Ability=Ability+Dict_Crowd_Control[item]
print(Ability)
Champion_Df['Attribute']=pd.Series(dtype='str')
Champion_Df['Attribute']=''

for label, row in Champion_Df.iterrows():
        for i in Ability:
                if i in Crowd_Control:
                        for row2 in Champion_Df['spells'][label]:
                                if ([row2][0]['tooltip'].find('<status>'+i))>0 :
                                        Champion_Df.iloc[label,Champion_Df.columns.get_loc('Attribute')]=i +', '+ Champion_Df.iloc[label,Champion_Df.columns.get_loc('Attribute')]
                                        break
                else:
                        for row2 in Champion_Df['spells'][label]:
                                if ([row2][0]['tooltip'].find(i))>0 :
                                        Champion_Df.iloc[label,Champion_Df.columns.get_loc('Attribute')]=i +', '+ Champion_Df.iloc[label,Champion_Df.columns.get_loc('Attribute')]
                                        break
Champion_Df['Attribute']=Champion_Df['Attribute'].str.rstrip(', ')

# Function to look after a Champion's Ability
def Lookfor_ChampionAbility(Champion_Name):
        for label, row in Champion_Df.iterrows():
                if row['id']==Champion_Name:
                        for row2 in Champion_Df['spells'][label]:
                                print([row2][0]['tooltip'])

# Get Champion's draft Position on the rift
def get_champion_role_stat():
        URL_champion_role = 'https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json'
        response = requests.get(URL_champion_role)
        j = response.json()
        data = {}
        for champion_id, positions in j["data"].items():
                champion_id = int(champion_id)
                play_rates = {}
                for position, rates in positions.items():
                        if rates['playRate'] >0.2:
                                play_rates[position.upper()] = rates["playRate"]
                data[champion_id] = play_rates
        df_data=pd.DataFrame(data)
        df_data.fillna(0,inplace=True)
        return df_data.transpose()

Champion_role=get_champion_role_stat()
Champion_role['key']=Champion_role.index
Champion_Df=pd.merge(Champion_Df,Champion_role, on='key')

'''print(len(Champion_Df[['name','Attribute']+Role].where((Champion_Df['Attribute'].str.len()>0)&
                                                          (Champion_Df['id'].isin(count_Tag))&
                                                           (Champion_Df[Role].sum(axis=1)>0)).dropna(how='any')))'''
print(Champion_Df[['name','Attribute']+Role].where((Champion_Df['Attribute'].str.len()>0)&
                                                          (Champion_Df['id'].isin(count_Tag))&
                                                           (Champion_Df[Role].sum(axis=1)>0)).dropna(how='any'))
