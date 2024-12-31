import os
import requests
import json
import re
from git import Repo  # Ensure GitPython is installed

# Configuration
repo_path = os.getcwd()  # Path to the repository
directory_to_scan = "Settings"  # Directory to scan within the repo
readme_file = "README.md"  # Path to the README.md file
json_url = "https://raw.githubusercontent.com/xenia-manager/Database/refs/heads/main/Database/xbox_marketplace_games.json"  # URL to the JSON file


# Initialize the repo
repo = Repo(repo_path)

# Fetch and parse the JSON data
response = requests.get(json_url)
games_data = response.json()

# Create a lookup dictionary for titles
title_lookup = {}

for game in games_data:
    # Map the main id to the title
    title_lookup[game['id']] = game['title']
    # Map alternative_ids to the title
    for alt_id in game.get('alternative_id', []):
        title_lookup[alt_id] = game['title']

# Function to generate a compact HTML table row
def generate_html_row(filename, last_commit, commit_link):
    name_without_ext = os.path.splitext(filename)[0]
    icon_src = f"http://www.xboxunity.net/Resources/Lib/Icon.php?tid={name_without_ext}"
    # Retrieve the title from the lookup dictionary; default to 'Unknown Title' if not found
    title = title_lookup.get(name_without_ext, 'Unknown Title')
    file_link = f"https://github.com/xenia-manager/Optimized-Settings/blob/main/Settings/{filename}"
    return {
        "html": (
            f"<tr>"
            f"<td><img src=\"{icon_src}\"/></td>"
            f"<td><center><a href=\"{file_link}\"><strong>{name_without_ext}</strong></a></center></td>"
            f"<td><center><strong>{title}</strong></center></td>"
            f"<td><center><a href=\"{commit_link}\">{last_commit}</a></center></td>"
            f"</tr>"
        ),
        "title": title  # Used for sorting
    }

# Scan the directory and build the table rows
rows = []
directory_path = os.path.join(repo_path, directory_to_scan)

for root, _, files in os.walk(directory_path):
    for file in files:
        file_path = os.path.relpath(os.path.join(root, file), repo_path)
        
        # Get the last commit information specific to the file
        commits = list(repo.iter_commits(paths=file_path, max_count=1))
        if commits:
            commit = commits[0]
            commit_date = commit.committed_datetime.strftime("%d/%m/%Y")
            commit_link = f"{repo.remotes.origin.url.replace('.git', '')}/commit/{commit.hexsha}"
            rows.append(generate_html_row(file, commit_date, commit_link))

# Sort rows alphabetically by title
sorted_rows = sorted(rows, key=lambda x: x["title"])

# Generate the new HTML table
new_table = (
    "<table id=\"games-table\" align=\"center\">"
    "<thead><tr><th></th><th>Title Id</th><th>Title</th><th>Last Modified</th></tr></thead><tbody>"
    + "".join(row["html"] for row in sorted_rows)
    + "</tbody></table>"
)

# Read the existing README.md file
with open(readme_file, "r") as f:
    readme_content = f.read()

# Regular expression to match the table block (table tag and all content inside)
table_pattern = r"(<table id=\"games-table\" align=\"center\">.*?</table>)"

# Replace the matched table block with the new table
updated_readme = re.sub(table_pattern, new_table, readme_content, flags=re.DOTALL)

# Write the updated README.md file back
with open(readme_file, "w") as f:
    f.write(updated_readme)

print(f"README.md updated with the new games table.")