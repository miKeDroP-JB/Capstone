"""
VAPI Agent Sparring System - Referee/Scorer Module

Analyzes sales call transcripts using Claude Sonnet and provides
detailed scoring, pattern extraction, and certification tracking.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic


class SparringReferee:
    """
    Referee agent that scores sparring calls and determines agent readiness
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.certification_threshold = 45  # 90% of 50 points
        self.required_consecutive_passes = 10
        self.model = "claude-sonnet-4-20250514"

    def analyze_call(
        self,
        transcript: str,
        prospect_type: str,
        call_id: str
    ) -> Dict:
        """
        Analyzes a sparring call transcript and returns detailed scoring

        Args:
            transcript: Full call transcript
            prospect_type: Type of prospect (e.g., "Skeptical Sarah")
            call_id: Unique identifier for this call

        Returns:
            Dictionary containing scores, feedback, and recommendations
        """

        prompt = f"""
SPARRING CALL ANALYSIS

Call ID: {call_id}
Prospect Type: {prospect_type}
Timestamp: {datetime.now().isoformat()}

TRANSCRIPT:
{transcript}

Analyze this sales call and provide your referee scoring.
Score across 5 categories (0-10 each, 50 total):

1. OPENING (0-10)
   - Did they hook attention in first 10 seconds?
   - Was tonality confident but not aggressive?
   - Did they establish rapport?

2. VALUE ARTICULATION (0-10)
   - Clear benefit statement?
   - Differentiated from competitors?
   - Relevant to prospect's pain?

3. OBJECTION HANDLING (0-10)
   - Acknowledged concern without being defensive?
   - Reframed effectively?
   - Moved conversation forward?

4. PROOF/DEMO (0-10)
   - Offered voice clone demonstration?
   - Built belief through proof?
   - Handled technical questions?

5. CLOSE (0-10)
   - Clear call-to-action?
   - Risk reversal emphasized?
   - Commitment secured or clear next step?

Return your analysis as valid JSON with this structure:

{{
  "scores": {{
    "opening": {{"score": 0-10, "feedback": "detailed feedback"}},
    "value_articulation": {{"score": 0-10, "feedback": "detailed feedback"}},
    "objection_handling": {{"score": 0-10, "feedback": "detailed feedback"}},
    "proof_demo": {{"score": 0-10, "feedback": "detailed feedback"}},
    "close": {{"score": 0-10, "feedback": "detailed feedback"}}
  }},
  "total_score": 0-50,
  "would_convert": true/false,
  "confidence_percent": 0-100,
  "winning_patterns": ["pattern1", "pattern2", "pattern3"],
  "losing_patterns": ["pattern1", "pattern2", "pattern3"],
  "script_adjustments": ["adjustment1", "adjustment2", "adjustment3"],
  "specific_quotes": {{
    "best_moment": "exact quote from transcript",
    "worst_moment": "exact quote from transcript"
  }}
}}

Be brutally honest. The goal is 90%+ performance (45+ points).
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            content = response.content[0].text

            # Find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")

            json_str = content[start_idx:end_idx]
            analysis = json.loads(json_str)

            # Add metadata
            analysis['call_id'] = call_id
            analysis['prospect_type'] = prospect_type
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['model_used'] = self.model

            return analysis

        except Exception as e:
            print(f"Error analyzing call: {e}")
            # Return default failure structure
            return {
                "error": str(e),
                "call_id": call_id,
                "prospect_type": prospect_type,
                "total_score": 0,
                "would_convert": False
            }

    def update_meta_brain(
        self,
        analysis: Dict,
        transcript: str,
        storage_path: str = "./meta_brain_data"
    ) -> Dict:
        """
        Extracts learnings from analysis and stores in meta-brain

        Args:
            analysis: Analysis results from analyze_call()
            transcript: Original call transcript
            storage_path: Path to store meta-brain data

        Returns:
            Dictionary of extracted learnings
        """

        os.makedirs(storage_path, exist_ok=True)

        learnings = {
            "timestamp": datetime.now().isoformat(),
            "call_id": analysis.get("call_id", "unknown"),
            "prospect_type": analysis.get("prospect_type", "unknown"),
            "total_score": analysis.get("total_score", 0),
            "would_convert": analysis.get("would_convert", False),
            "winning_patterns": analysis.get("winning_patterns", []),
            "losing_patterns": analysis.get("losing_patterns", []),
            "script_adjustments": analysis.get("script_adjustments", []),
            "transcript_sample": transcript[:500]  # First 500 chars
        }

        # Store in JSON file (in production, use a real database)
        filename = f"{storage_path}/learning_{analysis.get('call_id', 'unknown')}.json"
        with open(filename, 'w') as f:
            json.dump(learnings, f, indent=2)

        # Also append to master log
        log_file = f"{storage_path}/master_log.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(learnings) + '\n')

        return learnings

    def check_certification(self, recent_scores: List[float]) -> Dict:
        """
        Determines if agent is ready for production deployment

        Args:
            recent_scores: List of total scores from recent calls

        Returns:
            Dictionary with certification status and details
        """

        if len(recent_scores) < self.required_consecutive_passes:
            return {
                "certified": False,
                "reason": f"Need {self.required_consecutive_passes} consecutive scores, only have {len(recent_scores)}",
                "average_score": sum(recent_scores) / len(recent_scores) if recent_scores else 0,
                "scores_needed": self.required_consecutive_passes - len(recent_scores)
            }

        # Calculate average of last N scores
        recent = recent_scores[-self.required_consecutive_passes:]
        avg_score = sum(recent) / len(recent)

        if avg_score >= self.certification_threshold:
            return {
                "certified": True,
                "average_score": avg_score,
                "message": f"🎯 AGENT CERTIFIED - {avg_score:.1f}/50 average over last {self.required_consecutive_passes} calls",
                "scores": recent
            }
        else:
            return {
                "certified": False,
                "reason": f"Average score {avg_score:.1f}/50 below threshold {self.certification_threshold}",
                "average_score": avg_score,
                "gap": self.certification_threshold - avg_score,
                "scores": recent
            }

    def generate_performance_report(
        self,
        storage_path: str = "./meta_brain_data"
    ) -> Dict:
        """
        Generates comprehensive performance report from meta-brain data

        Args:
            storage_path: Path where meta-brain data is stored

        Returns:
            Performance report dictionary
        """

        log_file = f"{storage_path}/master_log.jsonl"

        if not os.path.exists(log_file):
            return {"error": "No training data found"}

        # Load all training data
        learnings = []
        with open(log_file, 'r') as f:
            for line in f:
                learnings.append(json.loads(line))

        if not learnings:
            return {"error": "No training data found"}

        # Calculate statistics
        scores = [l['total_score'] for l in learnings]
        conversions = [l['would_convert'] for l in learnings]

        # Extract all patterns
        all_winning_patterns = []
        all_losing_patterns = []

        for l in learnings:
            all_winning_patterns.extend(l.get('winning_patterns', []))
            all_losing_patterns.extend(l.get('losing_patterns', []))

        # Count pattern frequencies
        from collections import Counter
        winning_freq = Counter(all_winning_patterns)
        losing_freq = Counter(all_losing_patterns)

        report = {
            "total_calls": len(learnings),
            "average_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores),
            "conversion_rate": sum(conversions) / len(conversions) * 100,
            "score_trend": self._calculate_trend(scores),
            "top_winning_patterns": winning_freq.most_common(5),
            "top_losing_patterns": losing_freq.most_common(5),
            "recent_performance": scores[-10:] if len(scores) >= 10 else scores,
            "generated_at": datetime.now().isoformat()
        }

        return report

    def _calculate_trend(self, scores: List[float], window: int = 10) -> str:
        """Calculate if scores are trending up, down, or stable"""

        if len(scores) < window * 2:
            return "insufficient_data"

        first_half = sum(scores[-window*2:-window]) / window
        second_half = sum(scores[-window:]) / window

        diff = second_half - first_half

        if diff > 2:
            return "improving"
        elif diff < -2:
            return "declining"
        else:
            return "stable"


# Example usage
if __name__ == "__main__":
    # Initialize referee
    referee = SparringReferee()

    # Example transcript
    sample_transcript = """
    Sales Agent: Hey! Thanks for taking my call. I'm calling because we're doing something
    pretty wild right now - I can actually clone your voice and build you a working AI agent
    while we're on this call. Takes about 5 minutes. Have you got a second to see how it works?

    Prospect: Um, I'm pretty busy actually. Can you send me some information?

    Sales Agent: I totally get it - everyone's busy. But here's the thing: if I send you
    information, you'll never look at it and we both know that. What if instead, I just show
    you in the next 2 minutes why this is worth your time?

    Prospect: Okay, 2 minutes.

    Sales Agent: Perfect. So you're in [business type], right? How many appointments do you
    need to book per month to hit your goals?

    Prospect: Probably 20-30.

    Sales Agent: And what's an appointment worth to you in revenue?

    Prospect: If they show up and convert, probably $2,000-5,000.

    Sales Agent: So even one extra appointment per month is worth $2-5K to you. What if I
    could build you an AI agent that sounds exactly like you, books appointments 24/7, and
    if it doesn't book at least $5K in appointments in month one, you pay nothing?

    Prospect: That's interesting. How does it work?

    [Call continues...]
    """

    # Analyze call
    analysis = referee.analyze_call(
        transcript=sample_transcript,
        prospect_type="Busy Barbara",
        call_id="test_001"
    )

    print("\n=== CALL ANALYSIS ===")
    print(f"Total Score: {analysis.get('total_score', 'N/A')}/50")
    print(f"Would Convert: {analysis.get('would_convert', 'N/A')}")
    print(f"\nWinning Patterns:")
    for pattern in analysis.get('winning_patterns', []):
        print(f"  ✅ {pattern}")
    print(f"\nLosing Patterns:")
    for pattern in analysis.get('losing_patterns', []):
        print(f"  ❌ {pattern}")

    # Store in meta-brain
    learnings = referee.update_meta_brain(analysis, sample_transcript)
    print(f"\n✅ Learnings stored: {learnings['timestamp']}")

    # Check certification (example with fake scores)
    example_scores = [42, 44, 46, 47, 45, 46, 48, 47, 46, 45]
    cert_status = referee.check_certification(example_scores)

    print(f"\n=== CERTIFICATION STATUS ===")
    if cert_status['certified']:
        print(cert_status['message'])
    else:
        print(f"Not certified: {cert_status['reason']}")
        if 'gap' in cert_status:
            print(f"Gap to threshold: {cert_status['gap']:.1f} points")
