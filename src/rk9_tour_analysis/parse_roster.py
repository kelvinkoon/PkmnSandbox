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
        for pkmn_num, pkmn_info in enumerate(get_team_list(player_info_soup), 1):
            player_info_df_entry["pkmn" + str(pkmn_num)] = pkmn_info["species"]
            player_info_df_entry["pkmn" + str(pkmn_num) + "_item"] = pkmn_info["held_item"]
            player_info_df_entry["pkmn" + str(pkmn_num) + "_moves"] = pkmn_info["moves"]
        print(player_info_df_entry)
        player_info_df_entry_list.append(player_info_df_entry)
    # TODO: Make columns a constant
    df = pd.DataFrame(player_info_df_entry_list, columns=["full_name", "standing", 
        "pkmn1", "pkmn1_item", "pkmn1_moves", "pkmn2", "pkmn2_item", "pkmn2_moves", "pkmn3", "pkmn3_item", "pkmn3_moves",
          "pkmn4", "pkmn4_item", "pkmn4_moves", "pkmn5", "pkmn5_item", "pkmn5_moves", "pkmn6", "pkmn6_item", "pkmn6_moves"])
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
    pkmn_info_soup_list = eng_team_list_soup.find_all("div", {"class": "pokemon"})
    for pkmn_info_soup in pkmn_info_soup_list: 
        pkmn_info = {}
        pkmn_info["species"] = get_species(pkmn_info_soup)
        pkmn_info["held_item"] = get_held_item(pkmn_info_soup)
        pkmn_info["moves"] = "/".join(get_moves(pkmn_info_soup))
        team_list.append(pkmn_info)
    return team_list

def get_species(soup: BeautifulSoup):
    img_soup = soup.find("img")
    soup_next_element = img_soup.next_sibling
    # Remove whitespace
    pkmn_species = "".join(soup_next_element.split())
    # Remove nickname if applicable
    pkmn_species = re.sub('".*?"', '', pkmn_species)
    # Add space back (eg. Flutter Mane)
    pkmn_species = re.sub(r"(\\w)([A-Z])", r"\1 \2", pkmn_species)
    return pkmn_species

def get_held_item(soup: BeautifulSoup):
    held_item_soup = soup.find(lambda tag:tag.name=="b" and "Held Item" in tag.text)
    soup_next_element = held_item_soup.next_sibling
    held_item = soup_next_element.text
    return held_item

def get_moves(soup: BeautifulSoup):
    move_list = []
    move_soup_list = soup.find_all("span", {"class": "badge"})
    for move_soup in move_soup_list:
        move_list.append(move_soup.text)
    return move_list

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
