"""
Competition Brain Python Client

Simple Python wrapper for the Competition Brain API.
For production use, consider using the requests library directly
or creating a full Python SDK.
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime


class CompetitionBrain:
    """Competition Brain API Client"""

    def __init__(self, base_url: str = "http://localhost:3001", timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def health(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_models(self) -> List[Dict]:
        """Get available models"""
        response = self.session.get(f"{self.base_url}/api/models", timeout=self.timeout)
        response.raise_for_status()
        return response.json()["models"]

    def query(
        self,
        query: str,
        models: List[str],
        power_level: int = 80,
        time_limit: int = 60,
        free_only: bool = False,
        use_cache: bool = True,
    ) -> Dict:
        """
        Query multiple AI models

        Args:
            query: The question or prompt
            models: List of model IDs to query
            power_level: Power level percentage (0-100)
            time_limit: Time limit in seconds (5-300)
            free_only: Only use free models
            use_cache: Enable response caching

        Returns:
            Query result dictionary
        """
        payload = {
            "query": query,
            "config": {
                "models": models,
                "powerLevel": power_level,
                "timeLimit": time_limit,
                "freeOnly": free_only,
                "useCache": use_cache,
            },
        }

        response = self.session.post(
            f"{self.base_url}/api/query", json=payload, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def competition_query(self, query: str) -> Dict:
        """Query with competition preset (top 5 models, max power)"""
        models_data = self.get_models()
        top_models = sorted(models_data, key=lambda m: m["power"], reverse=True)[:5]
        model_ids = [m["id"] for m in top_models]

        return self.query(query, models=model_ids, power_level=95, time_limit=180)

    def fast_query(self, query: str) -> Dict:
        """Query with fast preset (3 models, 30s)"""
        models_data = self.get_models()
        model_ids = [m["id"] for m in models_data[:3]]

        return self.query(query, models=model_ids, power_level=50, time_limit=30)

    def free_query(self, query: str) -> Dict:
        """Query with free models only"""
        models_data = self.get_models()
        free_models = [m["id"] for m in models_data if m["free"]]

        return self.query(
            query, models=free_models, power_level=70, time_limit=60, free_only=True
        )

    def get_stats(self, result: Dict) -> Dict:
        """Calculate statistics from query result"""
        individual = result["individual"]
        successful = [r for r in individual if r["success"]]

        if not successful:
            return {
                "total_models": len(individual),
                "successful_models": 0,
                "failed_models": len(individual),
                "avg_confidence": 0,
                "avg_time": 0,
                "total_time": result["totalTime"],
            }

        return {
            "total_models": len(individual),
            "successful_models": len(successful),
            "failed_models": len(individual) - len(successful),
            "avg_confidence": sum(r["confidence"] for r in successful) / len(successful),
            "avg_time": sum(r["time"] for r in successful) / len(successful),
            "total_time": result["totalTime"],
            "cached": result.get("cached", False),
            "cache_age": result.get("cacheAge"),
        }

    def export_markdown(self, result: Dict) -> str:
        """Export result to Markdown format"""
        stats = self.get_stats(result)

        md = f"# Competition Brain Result\n\n"
        md += f"**Query**: {result['query']}\n\n"
        md += f"**Timestamp**: {result['timestamp']}\n\n"
        md += f"**Total Time**: {result['totalTime']:.2f}s\n\n"

        if result.get("cached"):
            cache_age_min = result["cacheAge"] / 1000 / 60
            md += f"**Cached**: Yes ({cache_age_min:.1f} minutes old)\n\n"

        md += f"## Synthesized Response\n\n"
        md += f"{result['synthesized']}\n\n"

        md += f"## Statistics\n\n"
        md += f"- Models Queried: {stats['total_models']}\n"
        md += f"- Successful: {stats['successful_models']}\n"
        md += f"- Failed: {stats['failed_models']}\n"
        md += f"- Average Confidence: {stats['avg_confidence']*100:.1f}%\n"
        md += f"- Average Response Time: {stats['avg_time']:.2f}s\n\n"

        md += f"## Individual Responses\n\n"

        for i, resp in enumerate(result["individual"], 1):
            md += f"### {i}. {resp['model']}\n\n"
            md += f"- **Confidence**: {resp['confidence']*100:.1f}%\n"
            md += f"- **Time**: {resp['time']:.2f}s\n"
            status = "✅ Success" if resp["success"] else "❌ Failed"
            md += f"- **Status**: {status}\n\n"
            md += f"**Response**:\n\n{resp['response']}\n\n"
            md += f"---\n\n"

        return md


def main():
    """Example usage"""
    print("🚀 Competition Brain Python Client\n")

    # Initialize client
    client = CompetitionBrain(base_url="http://localhost:3001")

    try:
        # Check health
        health = client.health()
        print(f"✅ API Status: {health['status']} (v{health['version']})\n")

        # Get models
        models = client.get_models()
        print(f"📋 Available Models: {len(models)}\n")

        for model in models[:5]:
            free_tag = "[FREE]" if model["free"] else ""
            print(
                f"  {model['name']} ({model['provider']}) - Power: {model['power']}% {free_tag}"
            )

        # Make a query
        print('\n💭 Query: "What is machine learning?"\n')

        result = client.query(
            "What is machine learning?",
            models=["gpt-4o-mini", "claude-3-5-haiku", "gemini-1.5-flash"],
            power_level=70,
            time_limit=30,
        )

        # Show results
        print("📊 Results:\n")
        print(f"Synthesized Answer: {result['synthesized'][:200]}...\n")

        stats = client.get_stats(result)
        print(f"Total Time: {stats['total_time']:.2f}s")
        print(f"Successful Models: {stats['successful_models']}/{stats['total_models']}")
        print(f"Average Confidence: {stats['avg_confidence']*100:.1f}%")
        print(f"Cached: {stats.get('cached', False)}\n")

        # Export to markdown
        markdown = client.export_markdown(result)
        with open("result.md", "w") as f:
            f.write(markdown)

        print("💾 Exported to: result.md\n")

        # Try competition mode
        print("🏆 Running competition mode query...\n")
        comp_result = client.competition_query("Explain quantum entanglement briefly")
        comp_stats = client.get_stats(comp_result)

        print(
            f"Competition Result: {comp_stats['successful_models']} models, {comp_stats['total_time']:.2f}s\n"
        )

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Server response: {e.response.text}")


if __name__ == "__main__":
    main()
