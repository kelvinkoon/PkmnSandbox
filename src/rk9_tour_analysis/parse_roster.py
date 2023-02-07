import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import List

RK9_URL_BASE = "https://rk9.gg"

DATA_DIR = "data/"
ROSTER_CSV_FILE_NAME = "roster.csv"
ROSTER_CSV_FILE_PATH = DATA_DIR + ROSTER_CSV_FILE_NAME
ORLANDO_ROSTER_ID = "h7kIYruNMePQMy4UZkMj"
RK9_ROSTER_URL = RK9_URL_BASE + "/roster/" + ORLANDO_ROSTER_ID
MASTERS_DIV_STR = "Masters"

FIRST_NAME_COL_INDEX = 1
LAST_NAME_COL_INDEX = 2
DIVISION_COL_INDEX = 4
STANDING_COL_INDEX = -1


def get_roster_soup(roster_url: str):
    roster_res = requests.get(roster_url)
    roster_soup = BeautifulSoup(roster_res.text, "html.parser")
    return roster_soup

def get_team_list_soup(team_list_id: str):
    team_list_res = requests.get(RK9_URL_BASE + "/" + team_list_id)
    team_list_soup = BeautifulSoup(team_list_res.text, "html.parser")
    return team_list_soup

def get_roster_info_df(soup: BeautifulSoup):
    player_info_df_entry_list = []
    # Get player info, ignoring table header
    player_info_soup_list = soup.find_all("tr")[1:]
    for player_info_soup in player_info_soup_list:
        player_info_df_entry = {}
        player_info_entry = (player_info_soup.text).split()
        # Take only Masters division teams
        if get_division(player_info_entry) != MASTERS_DIV_STR:
            continue

        player_info_df_entry["full_name"] = get_full_name(player_info_entry)
        player_info_df_entry["standing"] = get_standing(player_info_entry)
        # Team List is parsed with soup as the URI isn't part of text
        for num, pkmn in enumerate(get_team_list(player_info_soup), 1):
            player_info_df_entry["pkmn" + str(num)] = pkmn
        print(player_info_df_entry)
        player_info_df_entry_list.append(player_info_df_entry)
    # TODO: Make columns a constant
    df = pd.DataFrame(player_info_df_entry_list, columns=["full_name", "standing", 
        "pkmn1", "pkmn2", "pkmn3", "pkmn4", "pkmn5", "pkmn6"])
    return df

def write_df_to_csv(df: pd.DataFrame):
    # TODO: Make CSV a constant
    df.to_csv(ROSTER_CSV_FILE_PATH, index=False)

def get_team_list(soup: BeautifulSoup):
    team_list = []
    team_list_id = soup.find("a", href=True)["href"]
    team_list_soup = get_team_list_soup(team_list_id)
    # Get English team list
    eng_team_list_soup = team_list_soup.find("div", attrs={"id": "lang-EN"})
    # Separate Pokémon info by "img" tag
    pkmn_info_soup_list = eng_team_list_soup.find_all("img")
    for pkmn_info_soup in pkmn_info_soup_list: 
        # Get text after img tag
        pkmn_txt = pkmn_info_soup.next_sibling
        pkmn_txt = "".join(pkmn_txt.split())
        pkmn_txt = re.sub('".*?"', '', pkmn_txt)
        team_list.append(pkmn_txt)
    return team_list

def get_full_name(player_info_entry: List[str]):
    first_name = player_info_entry[FIRST_NAME_COL_INDEX]
    last_name = player_info_entry[LAST_NAME_COL_INDEX]
    return "{first_name} {last_name}".format(first_name=first_name, last_name=last_name)

def get_division(player_info_entry: List[str]):
    return player_info_entry[DIVISION_COL_INDEX]

def get_standing(player_info_entry: List[str]):
    return player_info_entry[STANDING_COL_INDEX]

def main():
    soup = get_roster_soup(RK9_ROSTER_URL)
    df = get_roster_info_df(soup)
    write_df_to_csv(df)

main()
