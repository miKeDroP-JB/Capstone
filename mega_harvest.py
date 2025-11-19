import json
import requests
import os
from pathlib import Path

BRAIN_URL = "http://127.0.0.1:3000"
MASTER_KEY = "dcf76d54bd8d4aa64140aace066e9fcaab088a178c48216286b0c44f848a3e92"

def harvest_everything():
    """Feed ALL exports to Brain OS"""
    
    # Register mega harvester
    r = requests.post(f"{BRAIN_URL}/register", json={
        "agent_name": "mega_harvester",
        "master_key": MASTER_KEY
    })
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    export_folder = Path(r"C:\Users\JB\Downloads\ai_exports")
    
    total = 0
    
    # Process all JSON exports
    for json_file in export_folder.glob("**/*.json"):
        print(f"\n📂 Processing: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract text from various formats
                text = str(data)[:2000]
                
                if len(text) > 100:
                    r = requests.post(
                        f"{BRAIN_URL}/compress",
                        json={"text": text},
                        headers=headers
                    )
                    
                    if r.status_code == 200:
                        total += 1
                        if total % 10 == 0:
                            print(f"  ✓ {total} patterns harvested...")
        except:
            pass
    
    print(f"\n✅ TOTAL: {total} patterns")
    
    stats = requests.get(f"{BRAIN_URL}/stats", headers=headers).json()
    print(f"\n📊 Brain now has {stats['patterns']} total patterns")

if __name__ == "__main__":
    harvest_everything()
