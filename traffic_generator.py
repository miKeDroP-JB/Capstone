#!/usr/bin/env python3
"""
TRAFFIC GENERATOR - Drive Traffic with Love, Humor & Value
===========================================================
Generate traffic to customer dashboards using:
- Social media (funny, valuable posts)
- Email (humor + value + everybody eats)
- Phone (warm, funny conversations)

Best sales techniques + jokes + spreading love = Success

Everybody eats where it starts and ends 💝

Love • Loyalty • Honor • Everybody Eats
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class TrafficGenerator:
    """Generates traffic with humor and value"""

    def __init__(self):
        self.campaigns_dir = Path("traffic_campaigns")
        self.campaigns_dir.mkdir(exist_ok=True)

        # Funny, valuable content library
        self.humor_templates = self._load_humor_templates()
        self.value_templates = self._load_value_templates()

    def _load_humor_templates(self) -> Dict:
        """Funny content templates"""
        return {
            "hvac_jokes": [
                "Why did the AC unit go to therapy? It had too many issues to work through! 😅 But seriously, we fix AC issues fast. Call us!",
                "What's an HVAC tech's favorite movie? The Coolest Runnings! ❄️ We keep things cool around here. Need service?",
                "Why don't HVAC techs ever get invited to parties? Because they're too cool! 😎 Speaking of cool, is YOUR AC working?",
                "I tried to write an HVAC joke but it wasn't hot enough... Unlike your house when the AC breaks! We're here 24/7! 📞",
                "What do you call an HVAC unit that tells jokes? A comic-cool! 🎭 We make comfort AND smiles happen!",
            ],
            "value_hooks": [
                "🎁 FREE AC checkup this week only! Because everybody eats, and everybody deserves to be cool!",
                "💰 Save $50 on any service! We believe in spreading the love (and the savings!)",
                "⚡ Same-day service available! Because your comfort can't wait!",
                "🌟 5-star rated! We don't just fix AC units, we make friends!",
                "💝 Family-owned, family-focused! We treat you like family because... well, everybody eats!",
            ],
            "story_starters": [
                "So this customer calls us at 2am... Their AC died in a Florida summer. We were there in 30 minutes. Why? Because that's what family does! 💝",
                "Last week, a customer said we saved their marriage 😂 Turns out arguing about the thermostat is real! We fixed it. Both the AC and the marriage! 🔧❤️",
                "Customer asked if we accept cookies as payment. We said no... but we DO eat them when offered! 🍪 (PS: We accept cash and cards too!)",
            ]
        }

    def _load_value_templates(self) -> Dict:
        """Value-first content templates"""
        return {
            "tips": [
                "💡 Pro tip: Change your AC filter every 30 days. Saves you $ and keeps you cool! Want us to do it for you? We got you!",
                "🌡️ Set your thermostat to 78°F when you're home. Comfortable + efficient! Need help? Call us!",
                "⚡ Your AC working overtime? Check for air leaks around windows. Free inspection from us!",
                "🧊 Ice on your AC unit? Turn it off and call us ASAP! That's not normal (but we fix it all the time!)",
                "💰 Save 15-30% on energy bills with regular AC maintenance. We make it easy!",
            ],
            "education": [
                "Did you know? 90% of AC issues are preventable with regular maintenance! Book yours today!",
                "HVAC fact: A well-maintained AC unit lasts 15-20 years. A neglected one? 8-10 years. Let's make yours last!",
                "Your AC is 50% of your energy bill! Small improvements = big savings. Let's optimize yours!",
            ],
            "community": [
                "💝 We're not just a business, we're your neighbors! When you win, we win. Everybody eats!",
                "🏠 Proud to serve this community for 15+ years! Your success is our success!",
                "🤝 Family-owned, locally operated! We live here too. Your comfort is our mission!",
            ]
        }

    def generate_social_campaign(self, customer_info: Dict, duration_days: int = 30) -> List[Dict]:
        """
        Generate social media campaign

        Mix of:
        - Humor (50%)
        - Value/tips (30%)
        - Testimonials/stories (20%)
        """

        company_name = customer_info['company_name']
        industry = customer_info.get('industry', 'HVAC')
        dashboard_url = customer_info.get('dashboard_url', '')

        posts = []

        for day in range(1, duration_days + 1):
            # Determine post type
            rand = random.random()

            if rand < 0.5:  # 50% humor
                category = random.choice(list(self.humor_templates.keys()))
                content = random.choice(self.humor_templates[category])
                post_type = "humor"
            elif rand < 0.8:  # 30% value
                category = random.choice(list(self.value_templates.keys()))
                content = random.choice(self.value_templates[category])
                post_type = "value"
            else:  # 20% story
                content = random.choice(self.humor_templates["story_starters"])
                post_type = "story"

            # Add CTA
            ctas = [
                f"\n\n👉 Book now: {dashboard_url}?source=social",
                f"\n\n📞 Call us today! Visit: {dashboard_url}?source=social",
                f"\n\n✨ Get your free quote: {dashboard_url}?source=social",
                f"\n\n💝 We're ready to help: {dashboard_url}?source=social",
            ]

            post = {
                "day": day,
                "type": post_type,
                "content": content + random.choice(ctas),
                "hashtags": ["#HVAC", "#AC", "#Heating", "#LocalBusiness", "#EverybodyEats"],
                "best_time": self._get_best_posting_time(day),
                "platform": "all"  # Facebook, Instagram, Twitter, LinkedIn
            }

            posts.append(post)

        # Save campaign
        campaign_file = self.campaigns_dir / f"social_{company_name.replace(' ', '_').lower()}.json"
        with open(campaign_file, 'w') as f:
            json.dump(posts, f, indent=2)

        print(f"✓ Generated {len(posts)} social media posts")
        print(f"✓ Saved to: {campaign_file}")

        return posts

    def generate_email_campaign(self, customer_info: Dict) -> List[Dict]:
        """Generate email campaign with humor and value"""

        company_name = customer_info['company_name']
        dashboard_url = customer_info.get('dashboard_url', '')

        emails = [
            {
                "name": "Welcome Email (Funny Intro)",
                "subject": "🎉 We're like Netflix... but for AC! (And we actually show up!)",
                "body": f"""Hey there!

Welcome to the {company_name} family! 💝

We're not your typical HVAC company. Sure, we fix air conditioners. But we also:
- Show up when we say we will (revolutionary, right?)
- Don't charge you for air (that's free!)
- Actually answer the phone (shocking!)
- Treat you like family (because everybody eats!)

Here's what we're doing for you starting TODAY:
✅ Monitoring your area for AC issues
✅ Posting helpful tips on social media
✅ Being available 24/7 for emergencies
✅ Spreading love, one cool home at a time

Need us? Click here: {dashboard_url}?source=email

Love • Loyalty • Honor • Everybody Eats,
The {company_name} Team

PS: Why did the AC unit break up with the heater? They had too many hot and cold moments! 😂
""",
                "timing": "Immediate after signup"
            },
            {
                "name": "Value Email (AC Maintenance Tips)",
                "subject": "💡 5 AC Tips That'll Save You $$$ (And one terrible joke)",
                "body": f"""Hey Friend!

Quick question: When was the last time you changed your AC filter?

If you said "uh... I don't know?" - you're not alone! 😅

Here are 5 tips that'll save you money AND keep you cool:

1️⃣ Change filters every 30 days ($200-500 saved on repairs!)
2️⃣ Clean around outdoor unit (better airflow = lower bills)
3️⃣ Set thermostat to 78°F when home (comfort + efficiency!)
4️⃣ Use ceiling fans (feels 4° cooler, uses less energy)
5️⃣ Schedule annual maintenance (prevents 90% of breakdowns!)

Want us to handle all this for you? We got you: {dashboard_url}?source=email

And now for the terrible joke:
Why don't AC units ever win races? Because they're always getting their fans! 🏃‍♂️💨

(We're better at fixing ACs than telling jokes! 😂)

Stay cool!
{company_name}

PS: Everybody eats means everybody stays COOL too! 💝
""",
                "timing": "Week 1"
            },
            {
                "name": "Urgency Email (Summer Is Coming)",
                "subject": "⚠️ Summer's Coming... Is Your AC Ready? (Spoiler: Probably not!)",
                "body": f"""Uh oh...

Summer is just around the corner. And you know what that means in Florida?

Your AC is about to work HARD. Like, really hard. Like, "I haven't exercised in 6 months and now I'm running a marathon" hard.

Here's the thing: Most AC units DIE in the first heat wave of summer. Why? Because nobody checks them!

Don't be that person! 😅

Book your FREE AC checkup NOW: {dashboard_url}?source=email

What we check:
✅ Filters (probably dirty!)
✅ Refrigerant levels (might be low!)
✅ Electrical connections (could be loose!)
✅ Airflow (might be blocked!)
✅ Overall system health (let's find out!)

Takes 30 minutes. Could save you $3,000 in emergency repairs.

Worth it? We think so!

Click here: {dashboard_url}?source=email

Love,
{company_name}

PS: What did summer say to the AC? "You better not leave me hanging!" 🌞❄️
""",
                "timing": "Early spring"
            },
            {
                "name": "Referral Email (Everybody Eats!)",
                "subject": "💝 Know someone who's too hot? (We can help... with AC!)",
                "body": f"""Hey there!

Quick question: Do you have a friend, family member, or neighbor who's always complaining about their AC?

You know the one. "It's SO hot!" "My AC is broken AGAIN!" "Why is my bill so high?!"

Send them our way! 🎁

Why? Because:
1. We'll take care of them (like we take care of you!)
2. They'll love you forever (you saved them from the heat!)
3. You get $50 off your next service (yep, free money!)
4. Everybody eats! 💝

Send them here: {dashboard_url}?source=referral

It's simple:
- They get great service
- You save money
- We grow our family
- Everybody wins!

That's what "everybody eats" means, friend. We ALL succeed together.

Share the love (and the cool air!),
{company_name}

PS: Thanks for being part of our family. Seriously. You're the best! 🙏
""",
                "timing": "Month 2"
            }
        ]

        # Save campaign
        campaign_file = self.campaigns_dir / f"email_{company_name.replace(' ', '_').lower()}.json"
        with open(campaign_file, 'w') as f:
            json.dump(emails, f, indent=2)

        print(f"✓ Generated {len(emails)} email campaigns")
        print(f"✓ Saved to: {campaign_file}")

        return emails

    def generate_phone_scripts(self, customer_info: Dict) -> List[Dict]:
        """Generate phone sales scripts with humor and warmth"""

        company_name = customer_info['company_name']
        dashboard_url = customer_info.get('dashboard_url', '')

        scripts = [
            {
                "name": "Warm Call Script (Funny Opener)",
                "scenario": "Calling past customer or referral",
                "script": f"""
Hi [NAME], this is [YOUR NAME] from {company_name}!

Don't worry, this isn't a robot call! I'm a real human! 😊

Quick question - how's your AC treating you this summer? Still keeping you cool?

[LISTEN]

Awesome! Here's why I'm calling:

We're doing FREE AC checkups this week for our favorite customers (that's you!). Takes 20 minutes, totally free, and honestly? Most people find at least ONE thing that could save them money.

Want me to swing by? I've got an opening [DAY] at [TIME].

[CLOSE]

Perfect! See you then! And hey - if you know anyone else melting in the heat, send them to {dashboard_url}. We're spreading the cool vibes! ❄️

Love,
[YOUR NAME]
""",
                "tone": "Warm, friendly, helpful"
            },
            {
                "name": "Cold Call Script (Humor + Value)",
                "scenario": "Calling new prospect",
                "script": f"""
Hi, this is [YOUR NAME] from {company_name}!

I promise this is the least annoying sales call you'll get today! 😂

Real quick - are you happy with your current AC company? Like, REALLY happy?

[LISTEN]

Gotcha. Here's the thing:

Most HVAC companies show up late, overcharge, and disappear when you need them.

We're different. We actually:
- Show up on time (wild, right?)
- Charge fair prices (no hidden fees!)
- Answer the phone (even at 2am!)
- Treat you like family (everybody eats!)

Want a free AC checkup to see the difference? No obligation, takes 20 minutes.

[CLOSE]

Awesome! And hey - even if you don't book, check out our tips at {dashboard_url}. We give away good stuff for free because... well, everybody eats!

Talk soon,
[YOUR NAME]
""",
                "tone": "Confident, funny, genuine"
            },
            {
                "name": "Emergency Follow-Up (Warm & Ready)",
                "scenario": "Customer had emergency service",
                "script": f"""
Hey [NAME], it's [YOUR NAME] from {company_name}!

Just checking in after we fixed your AC last week. Everything still running smooth?

[LISTEN]

Perfect! That's what we like to hear!

Quick thing - since your AC is getting up there in age, wanna schedule a regular maintenance checkup? Keeps it running longer, prevents expensive breakdowns.

Think of it like oil changes for your car. Boring but necessary! 😅

I can get you on the schedule for [DATE]. Sound good?

[CLOSE]

Awesome! And hey - thanks for trusting us at 2am when your AC died. That's what family does!

See you soon,
[YOUR NAME]

PS: If anyone you know needs AC help, send them to {dashboard_url}. We got 'em!
""",
                "tone": "Caring, proactive, helpful"
            }
        ]

        # Save scripts
        scripts_file = self.campaigns_dir / f"phone_{company_name.replace(' ', '_').lower()}.json"
        with open(scripts_file, 'w') as f:
            json.dump(scripts, f, indent=2)

        print(f"✓ Generated {len(scripts)} phone scripts")
        print(f"✓ Saved to: {scripts_file}")

        return scripts

    def _get_best_posting_time(self, day: int) -> str:
        """Get best posting time based on day of week"""
        day_of_week = day % 7

        # Best times for engagement
        times = {
            0: "9:00 AM",  # Monday
            1: "12:00 PM", # Tuesday
            2: "3:00 PM",  # Wednesday
            3: "11:00 AM", # Thursday
            4: "1:00 PM",  # Friday
            5: "10:00 AM", # Saturday
            6: "2:00 PM",  # Sunday
        }

        return times[day_of_week]

    def generate_complete_campaign(self, customer_info: Dict) -> Dict:
        """Generate complete traffic campaign"""

        print(f"\n{'='*60}")
        print(f"🚀 GENERATING COMPLETE TRAFFIC CAMPAIGN")
        print(f"{'='*60}\n")
        print(f"Customer: {customer_info['company_name']}")
        print()

        # Generate all campaigns
        social = self.generate_social_campaign(customer_info, duration_days=30)
        print()

        email = self.generate_email_campaign(customer_info)
        print()

        phone = self.generate_phone_scripts(customer_info)
        print()

        campaign = {
            "customer": customer_info,
            "created_date": datetime.now().isoformat(),
            "social_media": {
                "posts": len(social),
                "duration_days": 30
            },
            "email": {
                "campaigns": len(email)
            },
            "phone": {
                "scripts": len(phone)
            }
        }

        print(f"{'='*60}")
        print("✓ CAMPAIGN COMPLETE!")
        print(f"{'='*60}\n")
        print(f"Social posts: {len(social)} (30 days)")
        print(f"Email campaigns: {len(email)}")
        print(f"Phone scripts: {len(phone)}")
        print()
        print("Next steps:")
        print("1. Schedule social posts (use Buffer/Hootsuite)")
        print("2. Set up email automation (use Mailchimp)")
        print("3. Make warm phone calls using scripts")
        print("4. Drive ALL traffic to customer dashboard")
        print("5. Track conversions")
        print("6. Everybody eats! 💝")
        print()

        return campaign


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Traffic Generator")
    parser.add_argument("--company", type=str, help="Company name")
    parser.add_argument("--url", type=str, help="Dashboard URL")

    args = parser.parse_args()

    generator = TrafficGenerator()

    if args.company:
        customer_info = {
            "company_name": args.company,
            "industry": "HVAC",
            "dashboard_url": args.url or f"https://{args.company.lower().replace(' ', '')}.com"
        }

        campaign = generator.generate_complete_campaign(customer_info)
    else:
        print("Traffic Generator")
        print("\nUsage:")
        print('  python traffic_generator.py --company "ABC HVAC" --url "https://abchvac.com"')
