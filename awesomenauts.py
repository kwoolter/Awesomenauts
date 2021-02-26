from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import json


def parse_naut_names():
    # Parse Awesomenauts wiki for a list of URLs to the individual character pages
    URL = "https://awesomenauts.fandom.com"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    nauts_nav = soup.find_all("div", class_="portal")
    nauts_list = nauts_nav[1].find_all("li")

    nauts_urls = {}
    for naut in nauts_list:
        href = f"{URL}/{naut.a.get('href')}"
        nauts_urls[naut.string] = href

    return nauts_urls

def parse_upgrade(upgrade_html, _print = True):

    # Get the upgrade name and the URL for its image
    upgrade_name = upgrade_html.a['title']
    upgrade_img = upgrade_html.find("td").find("img").get("src")
    upgrade_img = upgrade_img[:upgrade_img.lower().find(".png" ) +4]

    # Parse the html table into a data frame
    df = pd.read_html(upgrade_html.prettify())[0]

    # Pull out upgrade description and cost
    upgrade_description =df.loc[1 ,1].split(":")[1].strip()
    cost = df.loc[0 ,2]

    # Parse the upgrade stats
    u = df.loc[1: ,2:].T
    u.columns = u.iloc[0]
    u = u.drop(u.index[0])
    u = u.dropna(axis=0, how="all")
    u = u.dropna(axis=1, how="all")
    u = u.reset_index(drop=True)

    # Build a dictionary of the upgrade data
    upgrade_dict = {"name" :upgrade_name,
                    "img" :upgrade_img,
                    "description" :upgrade_description,
                    "cost" :cost}

    if _print:
        print(f"Name:{upgrade_name} (Cost={cost})\nDescription:{upgrade_description}")

    # List of upgrade levels
    upgrade_levels = []

    # Loop throught the upgrade levels' data
    for index, row in u.iterrows():

        # build a dictionary of each level's upgrade info
        upgrade_level_details = {}
        for property in row.index:
            upgrade_level_details[property] = row[property]
            if _print:
                print(f"\t{index}:{property}:{row[property]}")

        upgrade_levels.append(upgrade_level_details)

    # Store the details of the upgrade levels in the main upgrade dictionary
    upgrade_dict["levels"] = upgrade_levels


    return upgrade_dict


def parse_skill(skill_html, _print=True):
    '''
    In: HTML of an awesomenauts character skill
    Out: Dictionary of the details of the skill
    Process:  Use pandas to convert the HTML to a dataframe and then wrangle the data into a dictionary
    '''

    # Get the skill imagine URL
    skill_img = skill_html.find("img").get("src")
    skill_img = skill_img[:skill_img.lower().find(".png" ) +4]

    # Parse the html table into a data frame
    df = pd.read_html(skill_html.prettify())[0].T
    df = df.dropna(axis=1, how="all")

    # Parse the df for the skill name and description
    skill_name = df.iloc[0 ,1].split("[")[0].strip()
    skill_description = df.iloc[0 ,2]

    # Create a new df of just the skill stats
    stats = df.loc[: ,3:]
    stats.columns = stats.iloc[0]
    stats = stats.drop(stats.index[0])
    stats = stats.reset_index(drop=True)
    stats.iloc[0]

    # Create a dictionary to store all of the skill details
    skill_dict = {"name" :skill_name,
                  "description" :skill_description,
                  "img" :skill_img}

    if _print:
        print(f"Skill:{skill_name}\n{skill_description}")

    # Add the skill stats and values to the skill dictionary
    skill_stats_dict = {}
    for stat in stats.columns:
        matching_stats = stats.loc[0 ,stat]

        # If more than one stats with the same name...
        if type(matching_stats) == pd.Series:
            for i, v in enumerate(matching_stats):
                skill_stats_dict[f"{stat.strip()}-{i}"] = v
                if _print:
                    print(f"\t{stat.strip()}-{i}={v}")
        else:
            if _print:
                print(f"\t{stat}={stats.loc[0 ,stat]}")
            skill_stats_dict[str(stat).strip()] = stats.loc[0 ,stat]

    skill_dict["stats"] = skill_stats_dict

    # Get the full details of the skill
    skill_url_name = skill_name.replace(" " ,"_")
    skill_url =f"https://awesomenauts.fandom.com/wiki/{skill_url_name}"
    page = requests.get(skill_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find all of the tables on the page
    tables = soup.find_all("table", class_="framed-table")

    # Loop thorugh each skill upgrade tables...
    if _print:
        print("### Skill Upgrades ###")

    upgrades = []

    # Build a list of upgrade details for this skill
    for i in range(2, len(tables)):
        new_upgrade = parse_upgrade(tables[i], _print)
        upgrades.append(new_upgrade)

    skill_dict["upgrades"] = upgrades


    return skill_dict


def parse_character(character_html, _print=True):
    # Get the chracter's name from the page title
    character_name = character_html.title.string.split("-")[0].strip()

    # Find all of the tables in the HTML
    tables = character_html.find_all("table", class_="framed-table")

    # Parse the html table into a data frame
    df = pd.read_html(tables[0].prettify())[0]
    df = df.dropna(axis=0, how="all")

    # Create a data frame for the character's abilities
    types_of_abilities = df.iloc[-1, 0].split(":")[1].strip()
    abilities = [x.strip() for x in types_of_abilities.split(",")]

    # Create a dataframe for the character's stats
    stats = df[1:-2]
    stats = stats.dropna(axis=0, how="all")
    stats = stats.dropna(axis=1, how="all")
    stats = stats.T
    stats.columns = stats.iloc[0]
    stats = stats.drop(stats.index[0])
    stats = stats.reset_index(drop=True)

    # Print the characters name, abilities and stats
    if _print:
        print(f"Name:{character_name}\nAbilities:{abilities}")

    character_dict = {"name": character_name,
                      "abilities": abilities}

    for stat in stats.columns:
        stat_name = stat.split(":")[0].strip()
        character_dict[stat_name] = stats.loc[0, stat]

        if _print:
            print(f"\t{stat_name}:{stats.loc[0, stat]}")

    # Loop throuth the HTML tables that have the details for each skill...
    if _print:
        print("### Skills ###")

    skills = []

    for i in range(1, len(tables) - 1, 2):
        new_skill = parse_skill(tables[i], _print)
        skills.append(new_skill)

    character_dict["skills"] = skills

    return character_dict

def create_json_file(nauts_urls : dict, file_name : str = "awesomenauts.json"):
    awesome_nauts = {}
    for name, url in nauts_urls.items():
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        try:
            character_dict = parse_character(soup, _print=False)

            awesome_nauts[name] = character_dict

            json.dumps(character_dict)
        except:
            print("ERRRRORRR" + name)
            break

    fp = open(file_name, 'w')
    json.dump(awesome_nauts, fp)
    fp.close()

def load_json_file(file_name : str = "awesomenauts.json"):
    # Load in the JSON file that contains all of the data
    fp = open(file_name, 'r')
    data = json.load(fp)
    fp.close()
    return data
