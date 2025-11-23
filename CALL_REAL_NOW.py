#!/usr/bin/env python3
"""
CALL REAL NOW - Make Real Calls RIGHT NOW
==========================================
Complete system to make real calls to real businesses today.

Simple workflow:
1. Find real businesses (Google search)
2. Make calls (guided by assistant)
3. Close deals
4. Collect money (Stripe)
5. Onboard clients

NO SIMULATION. REAL MONEY.

Love • Loyalty • Honor • Everybody Eats
"""

import json
import sys
from pathlib import Path

def main():
    print(f"\n{'='*60}")
    print("📞 CALL REAL NOW - Make Money Today")
    print(f"{'='*60}\n")

    print("Choose your path:\n")
    print("1. Quick Start (I have businesses to call RIGHT NOW)")
    print("2. Find businesses first (Google search)")
    print("3. Add businesses manually (quick add)")
    print()

    choice = input("Select (1-3): ").strip()

    if choice == "1":
        quick_start()
    elif choice == "2":
        find_businesses()
    elif choice == "3":
        add_manually()
    else:
        print("Invalid choice")

def quick_start():
    """Quick start with businesses you already have"""
    print(f"\n{'='*60}")
    print("QUICK START")
    print(f"{'='*60}\n")

    # Check for existing business files
    real_biz_dir = Path("real_businesses")

    if real_biz_dir.exists():
        json_files = list(real_biz_dir.glob("*.json"))

        if json_files:
            print("Found these business lists:")
            for i, file in enumerate(json_files, 1):
                print(f"{i}. {file.name}")
            print()

            file_choice = input(f"Select file (1-{len(json_files)}) or 'n' to enter manually: ").strip()

            if file_choice.lower() != 'n':
                try:
                    selected_file = json_files[int(file_choice) - 1]

                    with open(selected_file) as f:
                        data = json.load(f)

                    businesses = data if isinstance(data, list) else data.get("businesses", [])

                    print(f"\n✓ Loaded {len(businesses)} businesses")
                    print()

                    start_calling(businesses)
                    return
                except:
                    pass

    # Manual entry
    print("Let's add businesses manually.")
    print()
    businesses = []

    while True:
        print(f"\nBusiness #{len(businesses) + 1}")
        name = input("Company name (or 'done'): ").strip()

        if name.lower() == 'done':
            break

        phone = input("Phone number: ").strip()

        business = {
            "company_name": name,
            "phone": phone,
            "address": input("Address (optional): ").strip() or "N/A",
            "website": input("Website (or 'none'): ").strip() or "NONE",
            "needs": ["marketing automation"]
        }

        businesses.append(business)
        print(f"✓ Added {name}")

    if businesses:
        # Save for later
        save_path = Path("real_businesses") / f"manual_{len(businesses)}_businesses.json"
        save_path.parent.mkdir(exist_ok=True)

        with open(save_path, 'w') as f:
            json.dump(businesses, f, indent=2)

        print(f"\n✓ Saved {len(businesses)} businesses to {save_path}")
        print()

        start_calling(businesses)
    else:
        print("\nNo businesses added.")

def find_businesses():
    """Find businesses using Google"""
    print(f"\n{'='*60}")
    print("FIND REAL BUSINESSES")
    print(f"{'='*60}\n")

    industry = input("Industry (hvac, dental, restaurant, auto): ").strip() or "hvac"
    location = input("Location (e.g., Tampa FL): ").strip() or "Tampa FL"
    count = input("How many businesses? (default 10): ").strip()
    count = int(count) if count else 10

    print(f"\n🔍 Finding {count} {industry} businesses in {location}...\n")

    print("=" * 60)
    print("GOOGLE SEARCH INSTRUCTIONS")
    print("=" * 60)
    print()
    print(f"1. Go to Google and search:")
    print(f'   "{industry} companies in {location}"')
    print(f'   "{industry} services {location}"')
    print()
    print("2. For each business, note:")
    print("   - Company name")
    print("   - Phone number")
    print("   - Website (if they have one)")
    print()
    print("3. Prioritize businesses with:")
    print("   - No website or bad website")
    print("   - No social media presence")
    print("   - No online booking")
    print()
    print("=" * 60)
    print()

    input("Press ENTER when you've found some businesses...")

    # Now collect them
    businesses = []

    print(f"\nLet's add the {count} businesses you found:\n")

    for i in range(count):
        print(f"Business #{i+1}:")
        name = input("  Company name (or 'done'): ").strip()

        if name.lower() == 'done':
            break

        phone = input("  Phone: ").strip()
        website = input("  Website (or 'none'): ").strip() or "NONE"

        business = {
            "company_name": name,
            "phone": phone,
            "website": website,
            "has_website": website.lower() != "none",
            "needs": []
        }

        # Identify needs
        if not business["has_website"]:
            business["needs"].append("website")
        business["needs"].append("marketing automation")

        businesses.append(business)
        print(f"  ✓ Added\n")

    if businesses:
        # Save
        save_path = Path("real_businesses") / f"{industry}_{location.replace(' ', '_')}_{len(businesses)}.json"
        save_path.parent.mkdir(exist_ok=True)

        with open(save_path, 'w') as f:
            json.dump(businesses, f, indent=2)

        print(f"✓ Saved {len(businesses)} businesses to {save_path}\n")

        ready = input("Ready to start calling? (y/n): ").strip().lower()
        if ready == 'y':
            start_calling(businesses)

def add_manually():
    """Add businesses manually one by one"""
    print(f"\n{'='*60}")
    print("ADD BUSINESSES MANUALLY")
    print(f"{'='*60}\n")

    from real_business_finder import RealBusinessFinder

    finder = RealBusinessFinder()

    while True:
        print()
        name = input("Company name (or 'done'): ").strip()

        if name.lower() == 'done':
            break

        phone = input("Phone: ").strip()

        finder.quick_add(name, phone)

    # Load and start calling
    quick_file = Path("real_businesses/quick_adds.json")
    if quick_file.exists():
        with open(quick_file) as f:
            businesses = json.load(f)

        ready = input(f"\n{len(businesses)} businesses ready. Start calling? (y/n): ").strip().lower()
        if ready == 'y':
            start_calling(businesses)

def start_calling(businesses: list):
    """Start the calling session"""
    print(f"\n{'='*60}")
    print(f"🚀 STARTING CALLING SESSION")
    print(f"{'='*60}\n")

    print(f"You're about to call {len(businesses)} businesses.")
    print(f"Expected closes: ~{int(len(businesses) * 0.3)} (30% close rate)")
    print(f"Expected revenue: ~${len(businesses) * 0.3 * 3000:,.0f}")
    print()

    ready = input("Ready? (y/n): ").strip().lower()

    if ready != 'y':
        print("\nOkay, saved for later!")
        return

    # Launch calling assistant
    from live_calling_assistant import LiveCallingAssistant

    assistant = LiveCallingAssistant()
    assistant.start_session(businesses)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
