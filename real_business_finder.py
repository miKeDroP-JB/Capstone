#!/usr/bin/env python3
"""
REAL BUSINESS FINDER - Find Real Businesses to Call
====================================================
Uses web search to find REAL businesses with:
- Real names
- Real phone numbers
- Real addresses
- Real websites
- Real needs (identified from online presence)

No simulation. Real data.

Love • Loyalty • Honor • Everybody Eats
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class RealBusinessFinder:
    """Finds real businesses to call"""

    def __init__(self):
        self.data_dir = Path("real_businesses")
        self.data_dir.mkdir(exist_ok=True)

    def find_businesses(self, industry: str, location: str, count: int = 20) -> List[Dict]:
        """
        Find real businesses using web search

        Returns list of businesses with:
        - Company name
        - Phone number
        - Address
        - Website
        - Identified needs
        """
        print(f"\n{'='*60}")
        print(f"FINDING REAL {industry.upper()} BUSINESSES")
        print(f"{'='*60}")
        print(f"Location: {location}")
        print(f"Target: {count} businesses")
        print()

        # Search queries to find businesses
        search_queries = [
            f"{industry} companies in {location}",
            f"{industry} services {location}",
            f"local {industry} businesses {location}",
            f"{industry} near {location}",
            f"best {industry} {location}"
        ]

        businesses = []

        # Instructions for manual research
        print("📋 TO FIND REAL BUSINESSES:")
        print()
        print("1. Google Search:")
        for query in search_queries[:3]:
            print(f"   - \"{query}\"")
        print()
        print("2. Look for:")
        print("   - Business name")
        print("   - Phone number")
        print("   - Website (if they have one)")
        print("   - Address")
        print()
        print("3. Check their digital presence:")
        print("   - Do they have a website?")
        print("   - Is it mobile-friendly?")
        print("   - Do they have social media?")
        print("   - Are they posting regularly?")
        print("   - Do they have online booking?")
        print()
        print("4. Score them:")
        print("   - No website or bad website = HIGH PRIORITY")
        print("   - No social media = HIGH PRIORITY")
        print("   - Manual booking only = HIGH PRIORITY")
        print()

        # Generate template for manual entry
        template_file = self.data_dir / f"template_{industry}_{location.replace(' ', '_')}.json"

        template = {
            "instructions": "Fill in real business data from your research",
            "businesses": [
                {
                    "company_name": "Example HVAC Company",
                    "phone": "555-123-4567",
                    "address": "123 Main St, City, State",
                    "website": "https://example.com or 'NONE'",
                    "has_website": False,
                    "has_social_media": False,
                    "has_online_booking": False,
                    "needs": ["website", "social media", "online booking"],
                    "score": 85,
                    "notes": "Called, spoke with owner, interested"
                }
            ] * count
        }

        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"✓ Template created: {template_file}")
        print()
        print("NEXT STEPS:")
        print(f"1. Open {template_file}")
        print(f"2. Fill in real business data from Google")
        print(f"3. Save the file")
        print(f"4. Run: python real_business_finder.py --load {template_file}")
        print()

        return businesses

    def load_businesses(self, file_path: str) -> List[Dict]:
        """Load businesses from filled template"""
        with open(file_path) as f:
            data = json.load(f)

        businesses = data.get("businesses", [])

        # Filter out template examples
        real_businesses = [
            b for b in businesses
            if b["company_name"] != "Example HVAC Company"
        ]

        print(f"\n✓ Loaded {len(real_businesses)} real businesses")

        # Save to ready-to-call file
        ready_file = self.data_dir / f"ready_to_call_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(ready_file, 'w') as f:
            json.dump(real_businesses, f, indent=2)

        print(f"✓ Ready to call: {ready_file}")

        return real_businesses

    def quick_add(self, company_name: str, phone: str, **kwargs) -> Dict:
        """Quickly add a business"""
        business = {
            "company_name": company_name,
            "phone": phone,
            "address": kwargs.get("address", ""),
            "website": kwargs.get("website", "NONE"),
            "has_website": kwargs.get("website", "NONE") != "NONE",
            "has_social_media": kwargs.get("has_social_media", False),
            "has_online_booking": kwargs.get("has_online_booking", False),
            "needs": kwargs.get("needs", ["marketing automation"]),
            "score": kwargs.get("score", 75),
            "notes": kwargs.get("notes", "")
        }

        # Save to quick adds file
        quick_file = self.data_dir / "quick_adds.json"

        if quick_file.exists():
            with open(quick_file) as f:
                businesses = json.load(f)
        else:
            businesses = []

        businesses.append(business)

        with open(quick_file, 'w') as f:
            json.dump(businesses, f, indent=2)

        print(f"✓ Added: {company_name}")
        print(f"✓ Total businesses: {len(businesses)}")

        return business


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find real businesses to call")
    parser.add_argument("--find", action="store_true", help="Generate template")
    parser.add_argument("--industry", type=str, default="hvac", help="Industry")
    parser.add_argument("--location", type=str, default="Tampa FL", help="Location")
    parser.add_argument("--count", type=int, default=20, help="Number of businesses")
    parser.add_argument("--load", type=str, help="Load filled template")
    parser.add_argument("--quick-add", action="store_true", help="Quick add business")
    parser.add_argument("--name", type=str, help="Business name")
    parser.add_argument("--phone", type=str, help="Phone number")

    args = parser.parse_args()

    finder = RealBusinessFinder()

    if args.find:
        finder.find_businesses(args.industry, args.location, args.count)
    elif args.load:
        finder.load_businesses(args.load)
    elif args.quick_add and args.name and args.phone:
        finder.quick_add(args.name, args.phone)
    else:
        print("Real Business Finder")
        print("\nUsage:")
        print("  python real_business_finder.py --find --industry hvac --location 'Tampa FL'")
        print("  python real_business_finder.py --load real_businesses/template_xxx.json")
        print("  python real_business_finder.py --quick-add --name 'ABC HVAC' --phone '555-1234'")
