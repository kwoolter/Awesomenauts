from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import jsontree

def json_to_HTML(data, template_file_name: str):

    # Create a JSON tree to allow easy navigation of the data in the file
    tree = jsontree.jsontree(data)

    # Load in the template to be used for each Flash card
    templateLoader = FileSystemLoader(searchpath=".")
    env = Environment(loader=templateLoader)

    template = env.get_template(template_file_name)

    # Create HTML Flash cards for every characters skill uopgrades

    # HTML output
    output = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Awesomenauts Skill Upgrades</title> \
        <link rel="stylesheet" href="template.css"></head><body>'

    # Loop through all of teh characters in the JSON tree...
    for character_name in tree.keys():

        # character_name = "Yuri"

        # Get a specific character from the tree
        character = tree.get(character_name)

        # Get their skills list
        skills = character.get('skills')

        # Loop through all of their skills...
        for skill in skills:

            skill_stats = ""
            stats = skill.get('stats')
            for k, v in stats.items():
                skill_stats += f"{k}:{v}<br>"

            # Get the list of upgrades the this skill
            upgrades = skill.get('upgrades')

            # Loop thourh all of the upgrades
            for upgrade in upgrades:

                # Get the basic details of the upgrade
                upgrade_name = upgrade.get('name')
                cost = upgrade.get('cost')

                # Get the effect of the upgrade at different levels
                levels = upgrade.get('levels')

                # Array to store 1-2 level descriptions for this upgrade
                level_descriptions = [f"Upgrade Lv{i + 1} : None" for i in range(len(levels) + 1)]

                # loop through the levels of effect for this upgrade
                for i, level in enumerate(levels):

                    # Build a description of each level effect
                    level_description = ""

                    # Loop through each effect
                    for ii, kv in enumerate(level.items()):
                        k, v = kv
                        level_description += f"{k} {v}"
                        if ii == 0:
                            level_description += ": "
                        elif ii < len(level) - 1:
                            level_description += ", "

                    level_descriptions[i] = level_description

                # Pass all of the data into the renderer to make an html card
                html = template.render(name=character.get("name"),
                                       skill=skill.get("name"),
                                       skill_stats=skill_stats,
                                       upgrade=f"{upgrade_name} [${cost}]",
                                       description=upgrade.get("description"),
                                       image=upgrade.get("img"),
                                       skill_image=skill.get("img"),
                                       level1=level_descriptions[0],
                                       level2=level_descriptions[1],
                                       )

                # Add the card to the complete list
                output += html

        # Just do one character for now
        # break
        output += "<div></div>"

    output += "</body></html>"

    return output





