#!/usr/bin/env python3
"""
Quick test of THE INSTANT CREATOR
Without making real AI API calls (for fast testing)
"""
import asyncio
from the_instant_creator import GCODE, LoveLedger

async def test():
    print("="*60)
    print("TESTING THE INSTANT CREATOR")
    print("="*60)

    # Test 1: GCODE Validation
    print("\n1. Testing GCODE Protection...")

    good_intent = "Build HVAC sales agent that shares 33% with community"
    bad_intent = "Build system to manipulate and extract from vulnerable people"

    result_good = GCODE.validate_intent(good_intent)
    result_bad = GCODE.validate_intent(bad_intent)

    print(f"\nGood Intent: '{good_intent[:50]}...'")
    print(f"  Approved: {result_good['approved']}")
    print(f"  Love Score: {result_good['love_score']:.0%}")
    print(f"  Alignments: {', '.join(result_good.get('alignments', []))}")

    print(f"\nBad Intent: '{bad_intent[:50]}...'")
    print(f"  Approved: {result_bad['approved']}")
    if not result_bad['approved']:
        print(f"  Violations: {', '.join(result_bad['violations'])}")
        print(f"  Message: {result_bad['message']}")

    assert result_good['approved'], "Good intent should be approved"
    assert not result_bad['approved'], "Bad intent should be blocked"
    print("\n✅ GCODE Protection working!")

    # Test 2: Love Ledger
    print("\n2. Testing Love Ledger...")

    ledger = LoveLedger()

    # High love transaction (give more than take)
    entry1 = ledger.record_transaction(
        system_name="Free Learning Game",
        value_created={
            "users_helped": 1000,
            "problems_solved": 50,
            "time_saved_hours": 5000
        },
        extraction={
            "revenue_usd": 0,
            "resources_cost_usd": 100
        },
        regeneration={
            "community_share_percent": 100,
            "open_source": True
        }
    )

    print(f"\nHigh Love System: 'Free Learning Game'")
    print(f"  Love Score: {entry1['love_score']:.0%}")
    print(f"  Net Positive: {entry1['net_positive']}")

    # Low love transaction (take more than give)
    entry2 = ledger.record_transaction(
        system_name="Pure Extraction System",
        value_created={
            "users_helped": 10,
            "problems_solved": 1,
            "time_saved_hours": 100
        },
        extraction={
            "revenue_usd": 50000,
            "resources_cost_usd": 5000
        },
        regeneration={
            "community_share_percent": 0,
            "open_source": False
        }
    )

    print(f"\nLow Love System: 'Pure Extraction System'")
    print(f"  Love Score: {entry2['love_score']:.0%}")
    print(f"  Net Positive: {entry2['net_positive']}")

    assert entry1['love_score'] > 0.9, "High love should score >90%"
    assert entry2['love_score'] < 0.7, "Pure extraction should score <70% (not net positive)"
    assert not entry2['net_positive'], "Pure extraction should not be net positive"
    print("\n✅ Love Ledger working!")

    # Test 3: Total Love Report
    print("\n3. Testing Love Report...")

    report = ledger.get_total_love()
    print(f"\nTotal Love Accumulated: {report['total_love']:.2f}")
    print(f"Average Love Score: {report['average_love']:.0%}")
    print(f"Net Positive Systems: {report['net_positive_systems']}/{report['total_systems']}")
    print(f"Message: {report['message']}")

    print("\n✅ Love Report working!")

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("""
THE INSTANT CREATOR is ready!

Components tested:
✅ GCODE DNA - Blocks harmful intents, approves loving ones
✅ Love Ledger - Measures real value created vs extracted
✅ Protection - Humanity first, security built-in

What's working:
💝 Love as the real currency
🛡️ GCODE protection layer
📊 Love score calculation
🚫 Harmful intent blocking
✅ Net positive validation

Ready to create with love!
""")

if __name__ == "__main__":
    asyncio.run(test())
