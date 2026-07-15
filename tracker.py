import os
import json
import requests
from bs4 import BeautifulSoup
import string

DATA_FILE = "known_fighters.json"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_current_fighters():
    fighters = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # UFC Stats categorizes alphabetically by the first letter of the fighter's LAST name
    for letter in string.ascii_lowercase:
        url = f"http://ufcstats.com/statistics/fighters?char={letter}&page=all"
        try:
            response = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Target the specific table row links containing the fighter names
            for link in soup.select('td.b-statistics__table-col a.b-link_style_black'):
                name = " ".join(link.text.split())
                if name:
                    fighters.add(name)
        except Exception as e:
            print(f"Error scraping letter {letter}: {e}")
            continue
            
    return fighters

def main():
    if not WEBHOOK_URL:
        print("Error: Missing DISCORD_WEBHOOK_URL in GitHub Secrets!")
        return

    current_fighters = get_current_fighters()
    print(f"Found {len(current_fighters)} total fighters on UFC Stats.")

    if len(current_fighters) == 0:
        print("Warning: No fighters retrieved. Web scraper might be blocked or selector changed.")
        return

    # Safely load the file
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                known_fighters = set(json.load(f))
            except json.JSONDecodeError:
                known_fighters = set()
    else:
        known_fighters = set()

    # Look for new entries if we already had a master list saved
    if len(known_fighters) > 0:
        new_fighters = current_fighters - known_fighters
        if new_fighters:
            print(f"Alert! Found {len(new_fighters)} new additions.")
            for fighter in new_fighters:
                message = f"🚨 **New Fighter Added to UFC Database:** {fighter}"
                requests.post(WEBHOOK_URL, json={"content": message})
        else:
            print("No new fighters detected since last check.")
    else:
        print("First initial run. Registering baseline roster list to file.")
    
    # Save the roster
    with open(DATA_FILE, 'w') as f:
        json.dump(list(current_fighters), f)

if __name__ == "__main__":
    main()
