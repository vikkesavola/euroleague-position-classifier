import requests
import json
import pandas as pd


def request_teams_api(season):
  """
  takes a season year as a parameter, e.g. 2021 for the season 2021-22
  returns a list of team codes, e.g. IST
  """
  url = f"https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E{season}/clubs"
  payload = {}
  headers = {
    'accept': 'application/json, text/plain, */*',
    'dnt': '1',
    'accept-language': 'fi-FI,fi;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://www.euroleaguebasketball.net',
    'priority': 'u=1, i',
    'referer': 'https://www.euroleaguebasketball.net/',
    'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36'
  }

  try:
    response = requests.request("GET", url, headers=headers, data=payload)
  except requests.exceptions.RequestException as e:
    print(f"Failed to fetch teams for season {season}: {e}")
    return []
  
  return parse_teams_api(response)


def parse_teams_api(response):
  """
  parse the teams API response of one season
  return a list of team codes, e.g. IST
  """
  data = json.loads(response.text)
  team_list = []
  for team in data["data"]:
    team_list.append(team["code"])

  return team_list


def request_roster_api(team, season):
  """
  team: team code, e.g. IST
  season: season year, e.g. 2021 for season 2021-22
  returns a dictionary of player codes corresponding to their positions
  """
  url = f"https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E{season}/clubs/{team}/people"

  payload = {}
  headers = {
    'accept': 'application/json, text/plain, */*',
    'dnt': '1',
    'accept-language': 'fi-FI,fi;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://www.euroleaguebasketball.net',
    'priority': 'u=1, i',
    'referer': 'https://www.euroleaguebasketball.net/',
    'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36'
  }

  try:
    response = requests.request("GET", url, headers=headers, data=payload)
  except requests.exceptions.RequestException as e:
    print(f"Failed roster fetch for team {team}, season {season}: {e}")
    return {}
  
  return parse_roster_api(response)


def parse_roster_api(response):
    """
    parse the roster API response
    returns a dictionary of player codes corresponding to their positions
    """
    player_positions = {}   # player codes as keys and positions as values, e.g. {013422 : 1} (where 1=guard, 2=forward, 3=center)
    data = json.loads(response.text)
    for player in data:
      player_positions[player["person"]["code"]] = player["position"]
    return player_positions



def request_players_api(season):
  """
  returns a list of player dictionaries
  """
  url = f"https://feeds.incrowdsports.com/provider/euroleague-feeds/v3/competitions/E/statistics/players/traditional?seasonMode=Single&limit=1000&sortDirection=ascending&seasonCode=E{season}&statisticMode=perGame&statisticSortMode=perGame"

  payload = {}
  headers = {
  'sec-ch-ua-platform': 'Windows',
  'Referer': 'https://www.euroleaguebasketball.net/',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36',
  'Accept': 'application/json, text/plain, */*',
  'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
  'sec-ch-ua-mobile': '?0'
  }

  try:
    response = requests.request("GET", url, headers=headers, data=payload)
  except requests.exceptions.RequestException as e:
    print(f"Failed to fetch player stats for season {season}: {e}")
    return []
  
  return parse_players_api(response)


def parse_players_api(response):
  """parse the players API response"""
  data = json.loads(response.text)
  return data["players"]


def scrape_data():
  player_stats = []       # the final dataset -- a list of player dictionaries containing stats
  teams_dict = {}         # lists the teams in a given season, e.g. key "2021" corresponds to the team codes in the season 2021-22
  seasons = range(2021, 2026, 1)    # From 2021-2022 to 2025-2026

  # Which fields to keep in player stats (other fields are dropped)
  keep = ["gamesPlayed", "gamesStarted", "minutesPlayed",
        "twoPointersMade", "twoPointersAttempted", "threePointersMade",
        "threePointersAttempted", "offensiveRebounds", "defensiveRebounds",
        "totalRebounds", "assists", "steals", "turnovers", "blocks"]

  for season in seasons:
    roster_positions = {}   # dictionary of player codes corresponding to their positions; season-specific
    teams_dict[season] = request_teams_api(season)

    for team_code in teams_dict[season]:
      roster_positions.update(request_roster_api(team_code, season))

    raw_player_stats = request_players_api(season)
    for player in raw_player_stats:
      row = {k: player[k] for k in keep}
      row["code"] = player["player"]["code"]
      row["name"] = player["player"]["name"]
      row["season"] = season
      row["position"] = roster_positions.get(row["code"])
      player_stats.append(row)

  return player_stats

data = scrape_data()
df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)