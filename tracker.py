import os
import json
import requests

DATA_FILE = "known_fighters.json"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_current_fighters():
    fighters = set()
    
    # We are using an open source, structured data repository that extracts UFC roster profiles daily
    url = "https://githubusercontent.com"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Loop through the clean data list to pull out names
            for item in data:
                first_name = item.get("firstName", "").strip()
                last_name = item.get("lastName", "").strip()
                full_name = f"{first_name} {last_name}".strip()
                if full_name:
                    fighters.add(full_name)
        else:
            print(f"Server responded with error status: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")
            
    return fighters

def main():
    if not WEBHOOK_URL:
        print("Error: Missing DISCORD_WEBHOOK_URL in GitHub Secrets!")
        return

    current_fighters = get_current_fighters()
    print(f"Found {len(current_fighters)} total fighters in the dataset.")

    if len(current_fighters) == 0:
        print("Warning: List is completely empty. Stream source failed.")
        return

    # Load file status securely
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                known_fighters = set(json.load(f))
            except json.JSONDecodeError:
                known_fighters = set()
    else:
        known_fighters = set()

    # Alert rules engine
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
    
    # Save step 
    with open(DATA_FILE, 'w') as f:
        json.dump(list(current_fighters), f)

if __name__ == "__main__":
    main()
