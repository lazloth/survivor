#!/usr/bin/env python

from bs4 import BeautifulSoup
import pandas as pd
import re
import requests

inprogress = False
elim = 'XX'
leagueId = 479915
url = 'http://games.espn.com/ffl/scoreboard?leagueId=' + str(leagueId)
r = requests.get(url)
html = BeautifulSoup(r.text, 'html.parser')
week = re.search('Scoreboard: Week (.+?) - Free Fantasy', html.title.string).group(1)
outfile = 'survivor' + str(week) + '.csv'

if len(html.find_all('div', {'id':re.compile("^team_liveproj_")})) > 0:
    inprogress = True
    
score_tds = html.find_all('td', {'class':'score'})

if inprogress:
    score_proj = html.find_all('td', {'class':'playersPlayed'})

def get_scores(score_td):
    score = score_td.get_text()
    teamname = score_td.parent()[0].find_all('a', {'target':'_top'})[0].get_text()
    owner = score_td.parent()[0].find_all('span', {'class':'owners'})[0].get_text()
    abbrev = re.sub('[()]','',score_td.parent()[0].find_all('span', {'class':'abbrev'})[0].get_text())
    return teamname, abbrev, score

def get_proj(proj_td):
    ytp = proj_td.find_all('div', {'id': re.compile("team_ytp*")})[0].get_text()
    projected = proj_td.find_all('div', {'id': re.compile("team_liveproj*")})[0].get_text()
    return ytp, projected
    
if inprogress:
    scores = pd.DataFrame([get_scores(td) for td in score_tds])
    projected = pd.DataFrame([get_proj(td) for td in score_proj])
    out = pd.concat([scores, projected], axis=1, ignore_index=True)
    out.columns = ['name','abbrev','score','ytp','projected']
else:
    out = pd.DataFrame([get_scores(td) for td in score_tds])
    out.columns = ['name','abbrev','score']

out = out[out.abbrev != elim]
out['score'] = out.score.astype('float')

if inprogress:
    out['projected'] = out.projected.astype('float')
    headers = ["name", "score", "ytp"]
    sortby = 'projected'
else:
    headers = ["name", "score"]
    sortby = 'score'
             
out.sort_values(by=sortby, ascending=True).to_csv(outfile, columns=headers, header=False, index=False)
