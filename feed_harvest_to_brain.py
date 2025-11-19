import requests

BRAIN_URL = "http://127.0.0.1:3000"
MASTER_KEY = "dcf76d54bd8d4aa64140aace066e9fcaab088a178c48216286b0c44f848a3e92"

def feed_harvest():
    print("\n🤖 Registering Architecture Harvester...")
    
    reg = requests.post(f"{BRAIN_URL}/register", json={
        "agent_name": "architect_harvester",
        "master_key": "dcf76d54bd8d4aa64140aace066e9fcaab088a178c48216286b0c44f848a3e92"
    })
    
    if reg.status_code != 200:
        print(f"❌ Registration failed: {reg.text}")
        return
    
    token = reg.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Harvester registered\n")
    
    # Your best patterns from 100+ apps
    patterns = [
        # Voice Agency
        "Intelligent routing analyzes query complexity and routes to optimal AI provider for 90% cost savings",
        "4-hour feedback loop: make calls, analyze results, refine scripts, iterate rapidly for continuous improvement",
        "Multi-AI orchestration coordinates GPT Claude Gemini based on task requirements and cost efficiency",
        
        # TERRA ORBS
        "Physical-digital sync: LED shoes pulse in rhythm with Spirit Animal heartbeat for unified experience",
        "Grounding measurement tracks earth connection via conductive sole sensors and biometric feedback",
        "1:2 give-back model: every purchase grounds 3 humans - buyer plus 2 kids with full transparency",
        
        # Tournament Brain
        "Hierarchical debate: 100 agents debate in 3 tiers, winners advance, best solution emerges from convergence",
        "Meta-learning extracts winning patterns from debate outcomes to improve future decisions",
        "Quality scoring achieves 96% accuracy vs 85% baseline through multi-agent consensus",
        
        # Glyph Compression
        "Symbolic encoding achieves 85% token reduction through smart symbol substitution and pattern matching",
        "Semantic compression reduces tokens by 40% while preserving core meaning and intent",
        "Reference compression reaches 97% reduction using pattern library lookups and caching",
        
        # OrbOS
        "7 avatar agents with 180+ micro-skills each, coordinated by meta-brain for optimal task distribution",
        "Agent routing analyzes task requirements and selects optimal agent based on skill specialization",
        "Compound learning targets 1% daily improvement through systematic feedback and pattern recognition",
        
        # eKo Ecosystem
        "Ecosystem architecture: products strengthen each other through strategic integration and shared infrastructure",
        "Token economics: value flows through entire system transparently with built-in profit sharing",
        "Everybody eats model: regenerative business with profit distribution designed into core architecture",
        
        # Best Practices
        "Speed plus iteration plus creation beats perfection - ship fast, learn faster, improve continuously",
        "Truth above all - transparent operations, honest metrics, real results over marketing hype",
        "Love as infrastructure not aspiration - design systems that care for people by default"
    ]
    
    print(f"🌱 Feeding {len(patterns)} patterns from your 100+ apps...\n")
    
    success = 0
    for i, pattern in enumerate(patterns, 1):
        try:
            r = requests.post(f"{BRAIN_URL}/compress", json={"text": pattern}, headers=headers)
            if r.status_code == 200:
                success += 1
                if i % 5 == 0:
                    print(f"  ✓ {i}/{len(patterns)} patterns fed...")
        except Exception as e:
            print(f"  ✗ Error on pattern {i}: {e}")
    
    print(f"\n✅ Successfully fed {success}/{len(patterns)} patterns to Brain OS\n")
    
    # Get final stats
    stats = requests.get(f"{BRAIN_URL}/stats", headers=headers).json()
    print("="*60)
    print("📊 BRAIN OS STATS AFTER HARVEST:")
    print("="*60)
    print(f"  Total patterns: {stats['patterns']}")
    print(f"  Cache hits: {stats['grimoire']['hits']}")
    print(f"  Tokens saved: {stats['grimoire']['saved']}")
    print(f"  Performance: {stats['performance']}")
    print("="*60)

if __name__ == "__main__":
    feed_harvest()
