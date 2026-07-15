import os
import json
import requests
from bs4 import BeautifulSoup

# The URL of the official UFC alphabetical directory
URL = "http://ufcstats.com"
DATA_FILE = "known_fighters.json"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_current_fighters():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    fighters = set()
    # Find all fighter links in the official statistics table
    for link in soup.find_all('a', class_='b-link b-link_style_black'):
        name = link.text.strip()
        if name:
            fighters.add(name)
    return fighters

def main():
    current_fighters = get_current_fighters()
    
    # Load previously saved fighters
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            known_fighters = set(json.load(f))
    else:
        known_fighters = set()

    # Check for brand new additions
    if known_fighters:
        new_fighters = current_fighters - known_fighters
        if new_fighters:
            for fighter in new_fighters:
                message = f"🚨 **New Fighter Added to UFC Database:** {fighter}"
                requests.post(WEBHOOK_URL, json={"content": message})
    
    # Save the updated list for next time
    with open(DATA_FILE, 'w') as f:
        json.dump(list(current_fighters), f)

if __name__ == "__main__":
    main()
