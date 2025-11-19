"""
GRIMOIRE SEEDER - Pre-train with Synthetic Patterns
====================================================
Front-load the intelligence. Don't wait for organic learning.
"""

from glyph_core import GlyphEngine
import json
import random

def generate_synthetic_patterns():
    """
    Generate thousands of high-quality patterns for pre-training
    """
    
    patterns = []
    
    # ==========================================================================
    # CATEGORY 1: CODE OPERATIONS (Most common AI tasks)
    # ==========================================================================
    
    code_actions = [
        "Analyze the provided code and identify logical errors",
        "Review this code for potential bugs",
        "Optimize this function for better performance",
        "Refactor this code to be more maintainable",
        "Add error handling to this function",
        "Write unit tests for this code",
        "Document this function with docstrings",
        "Convert this code from Python to JavaScript",
        "Debug this failing test case",
        "Explain what this code does step by step",
        "Find security vulnerabilities in this code",
        "Simplify this complex nested logic",
        "Add type hints to this Python function",
        "Extract this logic into a reusable function",
        "Fix the memory leak in this code",
        "Improve the time complexity of this algorithm",
        "Add logging to this service",
        "Handle edge cases in this validation",
        "Parallelize this sequential operation",
        "Cache the results of this expensive computation",
    ]
    patterns.extend(code_actions)
    
    # ==========================================================================
    # CATEGORY 2: TASK DECOMPOSITION (Strategic thinking)
    # ==========================================================================
    
    decomposition_patterns = [
        "Break this problem into three independent micro-tasks",
        "Split this project into manageable phases",
        "Decompose this feature into user stories",
        "Fragment this complex query into simpler steps",
        "Separate concerns in this monolithic function",
        "Divide this workload across multiple agents",
        "Partition this dataset for parallel processing",
        "Break down this requirement into technical tasks",
        "Segment this audience for targeted messaging",
        "Isolate the core problem from secondary issues",
    ]
    patterns.extend(decomposition_patterns)
    
    # ==========================================================================
    # CATEGORY 3: DATA OPERATIONS (Database & search)
    # ==========================================================================
    
    data_operations = [
        "Search the database for all users with premium accounts",
        "Filter results where status equals active",
        "Sort the data by creation date descending",
        "Join user table with orders table on user_id",
        "Aggregate sales by month and region",
        "Find duplicate entries in this dataset",
        "Validate all email addresses in the database",
        "Export this query result to CSV format",
        "Index this column for faster lookups",
        "Backup the database before migration",
        "Query all records modified in the last 24 hours",
        "Count distinct values in this column",
        "Calculate the average order value by customer",
        "Delete all expired sessions from cache",
        "Update user preferences for all premium members",
    ]
    patterns.extend(data_operations)
    
    # ==========================================================================
    # CATEGORY 4: COMMUNICATION (Writing & messaging)
    # ==========================================================================
    
    communication_patterns = [
        "Write a professional email to the client about project delays",
        "Draft a press release for the product launch",
        "Create a summary of the meeting notes",
        "Compose a thank you message for the team",
        "Write an apology for the service outage",
        "Draft a proposal for the new feature",
        "Create onboarding documentation for new developers",
        "Write a changelog for this release",
        "Compose a customer support response template",
        "Draft an internal memo about policy changes",
        "Write a blog post about our new technology",
        "Create a FAQ section for common questions",
        "Draft a rejection email that maintains goodwill",
        "Write executive summary for stakeholders",
        "Compose a notification for system maintenance",
    ]
    patterns.extend(communication_patterns)
    
    # ==========================================================================
    # CATEGORY 5: ANALYSIS & RESEARCH
    # ==========================================================================
    
    analysis_patterns = [
        "Analyze market trends for AI services",
        "Research competitors in the voice AI space",
        "Evaluate the pros and cons of this approach",
        "Compare these two architectural patterns",
        "Assess the risk of this deployment strategy",
        "Investigate the root cause of this failure",
        "Study user behavior patterns in the dashboard",
        "Examine the performance bottlenecks",
        "Review the security audit findings",
        "Analyze customer feedback for insights",
        "Research best practices for API design",
        "Evaluate third-party service providers",
        "Assess technical debt in the codebase",
        "Compare cloud hosting options",
        "Analyze conversion funnel drop-offs",
    ]
    patterns.extend(analysis_patterns)
    
    # ==========================================================================
    # CATEGORY 6: CREATIVE GENERATION
    # ==========================================================================
    
    creative_patterns = [
        "Generate ten creative names for this product",
        "Create a marketing tagline that emphasizes innovation",
        "Design a user flow for the onboarding process",
        "Brainstorm solutions for the scalability problem",
        "Invent a reward system for user engagement",
        "Create a visual metaphor for the data pipeline",
        "Generate variations of this headline for A/B testing",
        "Design the architecture for a microservices system",
        "Create a gamification strategy for the app",
        "Generate sample data for testing purposes",
    ]
    patterns.extend(creative_patterns)
    
    # ==========================================================================
    # CATEGORY 7: ORBOS-SPECIFIC PATTERNS (Your domain)
    # ==========================================================================
    
    orbos_patterns = [
        "Route this query to the optimal AI provider based on complexity",
        "Compress this prompt using glyph encoding",
        "Store this pattern in the Grimoire for future recall",
        "Execute this task through the Apollo agent for strategic planning",
        "Delegate this code generation to Hephaestus agent",
        "Coordinate debate between tournament brain clusters",
        "Calculate cost savings from smart routing decision",
        "Update agent performance ratings based on results",
        "Extract winning pattern from tournament finals",
        "Optimize token usage through semantic compression",
        "Query Mercury agent for communication optimization",
        "Invoke Athena for complex problem decomposition",
        "Schedule Ares for execution and deployment tasks",
        "Consult Hermes for speed and performance optimization",
        "Engage Artemis for security and quality validation",
        "Synthesize results from all seven avatar agents",
        "Learn from this interaction and update Grimoire",
        "Calculate 1% daily improvement compound rate",
        "Fragment intent into glyph sequence for spell creation",
        "Validate ritual success rate before automation",
    ]
    patterns.extend(orbos_patterns)
    
    # ==========================================================================
    # CATEGORY 8: VARIATIONS (Same meaning, different words)
    # ==========================================================================
    
    # Generate variations to catch different phrasings
    variation_templates = [
        ("analyze", ["examine", "review", "inspect", "evaluate", "assess", "study"]),
        ("create", ["generate", "build", "make", "produce", "construct", "develop"]),
        ("optimize", ["improve", "enhance", "boost", "refine", "streamline", "accelerate"]),
        ("find", ["search", "locate", "discover", "identify", "detect", "spot"]),
        ("fix", ["repair", "resolve", "correct", "patch", "remedy", "debug"]),
        ("explain", ["describe", "clarify", "elaborate", "illustrate", "detail", "break down"]),
    ]
    
    base_sentences = [
        "{action} the performance issues in this application",
        "{action} a solution for the authentication problem",
        "{action} the database query for faster execution",
        "{action} all instances of deprecated methods",
        "{action} the bug causing data corruption",
        "{action} how this algorithm works",
    ]
    
    for base in base_sentences:
        for action_word, variations in variation_templates:
            for var in variations:
                patterns.append(base.format(action=var.capitalize()))
    
    # ==========================================================================
    # CATEGORY 9: COMPLEX COMPOUND PATTERNS
    # ==========================================================================
    
    compound_patterns = [
        "First analyze the code, then identify bugs, and finally suggest fixes",
        "Search for users, filter by premium status, and sort by signup date",
        "Generate report, format as PDF, and email to stakeholders",
        "Validate input, process transaction, and update ledger",
        "Fetch data from API, transform to required format, and cache results",
        "Parse user query, route to appropriate agent, and return response",
        "Compress prompt, execute through tournament, and store winning pattern",
        "Authenticate request, authorize action, and log audit trail",
        "Monitor metrics, detect anomalies, and trigger alerts",
        "Collect feedback, analyze sentiment, and categorize issues",
    ]
    patterns.extend(compound_patterns)
    
    # ==========================================================================
    # CATEGORY 10: QUESTION PATTERNS
    # ==========================================================================
    
    question_patterns = [
        "What is the best approach for handling concurrent requests",
        "How should we structure the database schema for scalability",
        "Why is this function returning unexpected results",
        "When should we use caching versus real-time queries",
        "Where are the performance bottlenecks in this system",
        "Which design pattern fits this use case best",
        "What are the security implications of this architecture",
        "How can we reduce latency in the API response",
        "Why does this test fail intermittently",
        "What monitoring should we implement for production",
    ]
    patterns.extend(question_patterns)
    
    return patterns


def seed_grimoire(engine: GlyphEngine, patterns: list):
    """
    Seed the Grimoire with synthetic patterns
    """
    print(f"🌱 Seeding Grimoire with {len(patterns)} patterns...")
    print("=" * 70)
    
    total_tokens_before = 0
    total_tokens_after = 0
    successful = 0
    
    for i, pattern in enumerate(patterns):
        result = engine.compress(pattern, learn=True)
        total_tokens_before += result.tokens_before
        total_tokens_after += result.tokens_after
        
        if result.compression_ratio > 0.3:
            successful += 1
        
        # Progress indicator
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(patterns)} patterns...")
    
    overall_compression = 1 - (total_tokens_after / total_tokens_before)
    
    print("=" * 70)
    print(f"✅ Seeding complete!")
    print(f"   Total patterns: {len(patterns)}")
    print(f"   Patterns learned: {successful}")
    print(f"   Tokens before: {total_tokens_before}")
    print(f"   Tokens after: {total_tokens_after}")
    print(f"   Overall compression: {overall_compression:.1%}")
    print(f"   Grimoire size: {len(engine.grimoire.glyphs)} glyphs")
    print("=" * 70)
    
    return engine


def export_seeded_grimoire(engine: GlyphEngine, filepath: str = "seeded_grimoire.json"):
    """
    Export the seeded Grimoire for deployment
    """
    data = engine.export_grimoire()
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Exported seeded Grimoire to {filepath}")
    print(f"   File size: {len(json.dumps(data)) / 1024:.1f} KB")


def test_cache_hits(engine: GlyphEngine):
    """
    Test that cache hits are working after seeding
    """
    print("\n🎯 Testing Cache Hits...")
    print("=" * 70)
    
    test_queries = [
        "Analyze the provided code and identify logical errors",
        "Break this problem into three independent micro-tasks",
        "Search the database for all users with premium accounts",
        "Route this query to the optimal AI provider based on complexity",
        "Write a professional email to the client about project delays",
    ]
    
    hits = 0
    for query in test_queries:
        result = engine.compress(query, learn=False)
        status = "✅ CACHE HIT" if result.cache_hit else "❌ MISS"
        print(f"  {status}: {query[:50]}...")
        if result.cache_hit:
            hits += 1
    
    print(f"\n  Hit rate: {hits}/{len(test_queries)} ({hits/len(test_queries)*100:.0f}%)")
    print("=" * 70)


if __name__ == "__main__":
    # Initialize engine
    engine = GlyphEngine()
    
    # Generate patterns
    patterns = generate_synthetic_patterns()
    
    # Seed the grimoire
    engine = seed_grimoire(engine, patterns)
    
    # Test cache hits
    test_cache_hits(engine)
    
    # Export for deployment
    export_seeded_grimoire(engine)
    
    # Show final stats
    print("\n📊 FINAL GRIMOIRE STATS:")
    stats = engine.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                if isinstance(v, float):
                    print(f"  {k}: {v:.2f}")
                else:
                    print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
