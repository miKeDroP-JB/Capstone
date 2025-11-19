import requests
import json

BASE_URL = "http://127.0.0.1:3000"
MASTER_KEY ="5a69270d255064b5e28ab43b1fe471f55b949d4f57cc7aa28f680de981a4f446"

def seed_brain():
    print("Registering seeder agent...")
    reg = requests.post(f"{BASE_URL}/register", json={"agent_name": "seeder", "master_key": MASTER_KEY})
    
    if reg.status_code != 200:
        print(f"Failed: {reg.text}")
        return
    
    token = reg.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Agent registered!\n")
    
    patterns = [
        "Analyze the provided code and identify logical errors",
        "Review this code for potential bugs and security issues",
        "Optimize this function for better performance",
        "Refactor this code to be more maintainable",
        "Add error handling to this function",
        "Write unit tests for this code",
        "Document this function with docstrings",
        "Debug this failing test case",
        "Break this problem into independent micro-tasks",
        "Split this project into manageable phases",
        "Decompose this feature into user stories",
        "Separate concerns in this monolithic function",
        "Search the database for all users with premium accounts",
        "Filter results where status equals active",
        "Sort the data by creation date descending",
        "Join user table with orders table on user_id",
        "Aggregate sales by month and region",
        "Find duplicate entries in this dataset",
        "Validate all email addresses in the database",
        "Export query result to CSV format",
        "Write a professional email to client about delays",
        "Draft a press release for product launch",
        "Create a summary of meeting notes",
        "Compose a thank you message for the team",
        "Write an apology for service outage",
        "Draft a proposal for new feature",
        "Create onboarding documentation for developers",
        "Analyze market trends for AI services",
        "Research competitors in voice AI space",
        "Evaluate pros and cons of this approach",
        "Compare these two architectural patterns",
        "Assess risk of deployment strategy",
        "Investigate root cause of system failure",
        "Generate ten creative names for this product",
        "Create a marketing tagline emphasizing innovation",
        "Design user flow for onboarding process",
        "Brainstorm solutions for scalability problem",
        "Route query to optimal AI provider based on complexity",
        "Compress this prompt using glyph encoding",
        "Store this pattern in Grimoire for future recall",
        "Calculate cost savings from smart routing",
        "Update agent performance ratings based on results",
        "Extract winning pattern from tournament finals",
        "Optimize token usage through semantic compression",
        "Synthesize results from multiple agents",
        "Learn from this interaction and update patterns",
        "What is best approach for handling concurrent requests",
        "How should we structure database schema for scalability",
        "Why is this function returning unexpected results",
        "When should we use caching versus real-time queries",
        "Where are performance bottlenecks in this system",
        "Which design pattern fits this use case best"
    ]
    
    print(f"Seeding {len(patterns)} patterns...\n")
    
    successful = 0
    for i, pattern in enumerate(patterns, 1):
        try:
            r = requests.post(f"{BASE_URL}/compress", json={"text": pattern}, headers=headers)
            if r.status_code == 200:
                successful += 1
                if i % 10 == 0:
                    print(f"  {i}/{len(patterns)} patterns seeded...")
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\nDONE! {successful}/{len(patterns)} patterns seeded\n")
    
    stats = requests.get(f"{BASE_URL}/stats", headers=headers).json()
    print(f"Patterns stored: {stats['patterns']}")
    print(f"Cache hits: {stats['grimoire']['hits']}")
    print(f"Tokens saved: {stats['grimoire']['saved']}")

if __name__ == "__main__":
    seed_brain()
