import requests
from bs4 import BeautifulSoup
import re
import json

RK9_URL_BASE = "https://rk9.gg/"
FILE_PATH = "tourney_usage/orlando.txt"

ORLANDO_ROSTER_SUFFIX = "roster/h7kIYruNMePQMy4UZkMj"
roster_res = requests.get(RK9_URL_BASE + ORLANDO_ROSTER_SUFFIX)
roster_soup = BeautifulSoup(roster_res.text, "html.parser")

teamlist_links_raw = roster_soup.find_all(lambda predicate: predicate.name == "a" and "teamlist" in predicate.get("href"))
teamlist_links_cleaned = [link.get("href")[1:] for link in teamlist_links_raw]

team_roster_list = []
usage = {}
for index, teamlist_link in enumerate(teamlist_links_cleaned):
    full_teamlist_link = RK9_URL_BASE + teamlist_link
    # print(full_teamlist_link)
    team_res = requests.get(full_teamlist_link)
    team_soup = BeautifulSoup(team_res.text, "html.parser")
    for nested_soup in team_soup.find_all("div", attrs={"id": "lang-EN"}):
        team_roster = []
        pkmn_info_list = nested_soup.find_all("img")
        for pkmn_info in pkmn_info_list: 
            pkmn_txt = pkmn_info.next_sibling
            pkmn_txt = "".join(pkmn_txt.split())
            pkmn_txt = re.sub('".*?"', '', pkmn_txt)
            team_roster.append(pkmn_txt)
            usage[pkmn_txt] = usage.get(pkmn_txt, 0) + 1
        team_roster_text = "/".join(team_roster) + "\n"
        clean_display_team = str(1+index) + ": " + team_roster_text
        print(clean_display_team)
        with open(FILE_PATH, "a") as teams_file:
            teams_file.write(clean_display_team)

sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
print(sorted_usage)
with open(FILE_PATH, "a") as teams_file:
    for usage in sorted_usage:
        usage_str = usage[0] + ": " + str(usage[1]) + "\n"
        teams_file.write(usage_str)

