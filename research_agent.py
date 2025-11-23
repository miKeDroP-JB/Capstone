#!/usr/bin/env python3
"""
RESEARCH AGENT - Find Best Targets
===================================
Uses AI to find the best prospects to call.

Strategy:
1. Analyze market data
2. Find businesses that need digital solutions
3. Score them by:
   - Likelihood to need help
   - Ability to pay
   - Growth potential
4. Return ranked list

Usage:
    python research_agent.py --industry "HVAC" --count 50

Love • Loyalty • Honor • Everybody Eats
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class ResearchAgent:
    """Finds best targets to call"""

    def __init__(self):
        self.results_dir = Path("research_results")
        self.results_dir.mkdir(exist_ok=True)

    def find_targets(self, industry: str, count: int = 50, criteria: dict = None) -> List[Dict]:
        """Find best targets in an industry"""
        print(f"\n🔍 RESEARCH AGENT - Finding targets")
        print(f"   Industry: {industry}")
        print(f"   Count: {count}")

        # Research criteria
        if criteria is None:
            criteria = {
                "min_employees": 2,
                "max_employees": 50,
                "min_years": 1,
                "has_website": True,
                "needs": ["digital transformation", "automation", "online presence"]
            }

        print(f"\n   Criteria:")
        for k, v in criteria.items():
            print(f"     {k}: {v}")

        # Simulate research (in production, this uses real APIs)
        targets = self._simulate_research(industry, count, criteria)

        # Score and rank
        scored_targets = self._score_targets(targets)

        # Save results
        results_file = self.results_dir / f"targets_{industry}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(scored_targets, f, indent=2)

        print(f"\n✓ Found {len(scored_targets)} targets")
        print(f"✓ Saved to: {results_file}")

        return scored_targets

    def _simulate_research(self, industry: str, count: int, criteria: dict) -> List[Dict]:
        """Simulate research (replace with real APIs in production)"""
        print(f"\n   🔎 Researching {industry} businesses...")

        # Simulate finding businesses
        business_types = {
            "hvac": [
                "Air Conditioning Repair",
                "Heating & Cooling",
                "HVAC Installation",
                "Climate Control Services",
                "Ventilation Systems"
            ],
            "restaurant": [
                "Italian Restaurant",
                "Mexican Food",
                "Pizza Place",
                "Cafe & Bistro",
                "Fine Dining"
            ],
            "dental": [
                "Family Dentistry",
                "Cosmetic Dentistry",
                "Orthodontics",
                "Dental Implants",
                "Pediatric Dentistry"
            ],
            "auto": [
                "Auto Repair",
                "Car Dealership",
                "Body Shop",
                "Oil Change Service",
                "Tire Shop"
            ]
        }

        types_list = business_types.get(industry.lower(), ["General Service Business"])

        targets = []
        cities = ["Miami, FL", "Tampa, FL", "Orlando, FL", "Jacksonville, FL", "Atlanta, GA",
                  "Charlotte, NC", "Dallas, TX", "Houston, TX", "Phoenix, AZ", "Denver, CO"]

        for i in range(count):
            business_type = random.choice(types_list)
            city = random.choice(cities)

            target = {
                "id": f"target_{i+1:03d}",
                "company": f"{business_type} #{i+1}",
                "type": business_type,
                "location": city,
                "phone": f"+1-555-{random.randint(1000,9999)}",
                "employees": random.randint(2, 50),
                "years_in_business": random.randint(1, 20),
                "has_website": random.choice([True, True, True, False]),  # 75% have website
                "estimated_revenue": random.randint(100000, 5000000),
                "digital_presence": random.choice(["weak", "moderate", "strong"]),
                "needs_assessment": {
                    "online_booking": random.random() > 0.5,
                    "customer_management": random.random() > 0.6,
                    "marketing_automation": random.random() > 0.7,
                    "mobile_app": random.random() > 0.8,
                }
            }
            targets.append(target)

        return targets

    def _score_targets(self, targets: List[Dict]) -> List[Dict]:
        """Score and rank targets"""
        print(f"\n   📊 Scoring targets...")

        for target in targets:
            score = 0

            # Revenue potential (30%)
            if target["estimated_revenue"] > 1000000:
                score += 30
            elif target["estimated_revenue"] > 500000:
                score += 20
            else:
                score += 10

            # Digital presence (20%) - weak is good for us!
            if target["digital_presence"] == "weak":
                score += 20
            elif target["digital_presence"] == "moderate":
                score += 10

            # Years in business (15%)
            if 3 <= target["years_in_business"] <= 10:
                score += 15  # Sweet spot
            elif target["years_in_business"] > 10:
                score += 10

            # Employee count (10%)
            if 5 <= target["employees"] <= 20:
                score += 10  # Sweet spot
            elif target["employees"] < 5:
                score += 5

            # Needs (25%)
            needs_count = sum(target["needs_assessment"].values())
            score += min(25, needs_count * 6)

            # Add score
            target["score"] = min(100, score)
            target["priority"] = "HIGH" if score > 70 else "MEDIUM" if score > 50 else "LOW"

        # Sort by score
        targets.sort(key=lambda x: x["score"], reverse=True)

        return targets

    def print_top_targets(self, targets: List[Dict], count: int = 10):
        """Print top targets"""
        print(f"\n{'='*80}")
        print(f"TOP {count} TARGETS")
        print(f"{'='*80}\n")

        for i, target in enumerate(targets[:count], 1):
            print(f"{i}. {target['company']}")
            print(f"   Score: {target['score']}/100 | Priority: {target['priority']}")
            print(f"   Location: {target['location']}")
            print(f"   Phone: {target['phone']}")
            print(f"   Revenue: ${target['estimated_revenue']:,} | Employees: {target['employees']}")
            print(f"   Digital: {target['digital_presence']} | Website: {target['has_website']}")

            needs = [k for k, v in target['needs_assessment'].items() if v]
            if needs:
                print(f"   Needs: {', '.join(needs)}")
            print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Research Agent - Find Best Targets")
    parser.add_argument("--industry", default="hvac", help="Industry to research")
    parser.add_argument("--count", type=int, default=50, help="Number of targets")
    args = parser.parse_args()

    agent = ResearchAgent()
    targets = agent.find_targets(args.industry, args.count)
    agent.print_top_targets(targets, 10)

    print(f"\n✓ Research complete!")
    print(f"✓ {len(targets)} targets found and scored")
    print(f"✓ Top priority: {len([t for t in targets if t['priority'] == 'HIGH'])} HIGH priority targets")
