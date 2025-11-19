#!/usr/bin/env python3
"""
AI PROVIDER CONNECTORS
======================
Real API calls to Claude, Gemini, GPT
Plug into Brain OS router
"""
import os
import time
import json
from typing import Dict, Optional

# =============================================================================
# API CLIENTS
# =============================================================================

class ClaudeClient:
    """Anthropic Claude API"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-sonnet-4-20250514"
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        if not self.api_key:
            return {"error": "ANTHROPIC_API_KEY not set", "provider": "claude"}
        
        try:
            import httpx
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            start = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
            
            latency = time.time() - start
            
            return {
                "provider": "claude",
                "model": self.model,
                "content": data["content"][0]["text"],
                "tokens_used": data["usage"]["input_tokens"] + data["usage"]["output_tokens"],
                "latency": latency,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "provider": "claude", "success": False}


class GeminiClient:
    """Google Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model = "gemini-1.5-pro"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        if not self.api_key:
            return {"error": "GOOGLE_API_KEY not set", "provider": "gemini"}
        
        try:
            import httpx
            
            url = f"{self.base_url}?key={self.api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
            
            start = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
            
            latency = time.time() - start
            
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            
            return {
                "provider": "gemini",
                "model": self.model,
                "content": content,
                "tokens_used": len(prompt.split()) + len(content.split()),  # Estimate
                "latency": latency,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "provider": "gemini", "success": False}


class GPTClient:
    """OpenAI GPT API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo"
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        if not self.api_key:
            return {"error": "OPENAI_API_KEY not set", "provider": "gpt"}
        
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            start = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
            
            latency = time.time() - start
            
            return {
                "provider": "gpt",
                "model": self.model,
                "content": data["choices"][0]["message"]["content"],
                "tokens_used": data["usage"]["total_tokens"],
                "latency": latency,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "provider": "gpt", "success": False}


# =============================================================================
# UNIFIED ORCHESTRATOR
# =============================================================================

class AIOrchestrator:
    """
    Routes tasks to optimal AI provider based on weights and task type.
    Tracks performance for auto-optimization.
    """
    
    def __init__(self):
        self.claude = ClaudeClient()
        self.gemini = GeminiClient()
        self.gpt = GPTClient()
        
        self.providers = {
            "claude": self.claude,
            "gemini": self.gemini,
            "gpt": self.gpt
        }
        
        self.weights = {
            "quality": 0.7,
            "speed": 0.5,
            "cost": 0.3,
            "creativity": 0.5,
            "precision": 0.6
        }
        
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "by_provider": {
                "claude": {"requests": 0, "tokens": 0, "successes": 0},
                "gemini": {"requests": 0, "tokens": 0, "successes": 0},
                "gpt": {"requests": 0, "tokens": 0, "successes": 0}
            }
        }
        
        # Cost per 1K tokens (approximate)
        self.costs = {
            "claude": 0.003,
            "gemini": 0.00125,
            "gpt": 0.0005
        }
    
    def check_config(self) -> Dict:
        """Check which providers are configured"""
        return {
            "claude": self.claude.is_configured(),
            "gemini": self.gemini.is_configured(),
            "gpt": self.gpt.is_configured()
        }
    
    def route(self, task_type: str = "general", complexity: float = 0.5) -> str:
        """Decide which provider to use"""
        
        scores = {"claude": 0, "gemini": 0, "gpt": 0}
        
        # Quality-focused tasks → Claude
        if task_type in ["strategy", "code", "reasoning", "complex", "personal"]:
            scores["claude"] += self.weights["quality"] * 30
        
        # Research/long-form → Gemini
        if task_type in ["research", "analysis", "long_form", "multimodal"]:
            scores["gemini"] += self.weights["speed"] * 25
        
        # Bulk/simple → GPT
        if task_type in ["bulk", "simple", "routine", "cheap"]:
            scores["gpt"] += self.weights["cost"] * 35
        
        # Complexity adjustment
        scores["claude"] += complexity * 20
        scores["gpt"] += (1 - complexity) * 15
        scores["gemini"] += 0.5 * 10  # Middle ground
        
        # Only consider configured providers
        config = self.check_config()
        for provider in list(scores.keys()):
            if not config[provider]:
                scores[provider] = -1000  # Effectively disable
        
        # Return highest scoring
        best = max(scores, key=scores.get)
        return best
    
    async def generate(self, prompt: str, task_type: str = "general", 
                       complexity: float = 0.5, max_tokens: int = 1024) -> Dict:
        """Generate response using optimal provider"""
        
        # Route to best provider
        provider_name = self.route(task_type, complexity)
        provider = self.providers[provider_name]
        
        # Calculate temperature from creativity weight
        temperature = 0.3 + (self.weights["creativity"] * 0.7)  # 0.3 to 1.0
        
        # Make the call
        result = await provider.generate(prompt, max_tokens, temperature)
        
        # Track stats
        self.stats["total_requests"] += 1
        self.stats["by_provider"][provider_name]["requests"] += 1
        
        if result.get("success"):
            tokens = result.get("tokens_used", 0)
            cost = (tokens / 1000) * self.costs[provider_name]
            
            self.stats["total_tokens"] += tokens
            self.stats["total_cost"] += cost
            self.stats["by_provider"][provider_name]["tokens"] += tokens
            self.stats["by_provider"][provider_name]["successes"] += 1
            
            result["cost"] = cost
        
        return result
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        return {
            **self.stats,
            "providers_configured": self.check_config(),
            "current_weights": self.weights
        }


# =============================================================================
# TEST / DEMO
# =============================================================================

async def demo():
    """Demo the orchestrator"""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              AI ORCHESTRATOR - LIVE TEST                      ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    orch = AIOrchestrator()
    
    # Check config
    config = orch.check_config()
    print("Provider Configuration:")
    for provider, is_ready in config.items():
        status = "✓ READY" if is_ready else "✗ NOT CONFIGURED"
        print(f"  {provider}: {status}")
    
    print("\n" + "="*60)
    
    if not any(config.values()):
        print("\n⚠️  No API keys configured!")
        print("\nSet environment variables:")
        print("  $env:ANTHROPIC_API_KEY = 'your-key'")
        print("  $env:GOOGLE_API_KEY = 'your-key'")
        print("  $env:OPENAI_API_KEY = 'your-key'")
        print("\nThen run again.")
        return
    
    # Test routing
    test_cases = [
        ("What's 2+2?", "simple", 0.1),
        ("Write a Python function to sort a list", "code", 0.5),
        ("Develop a comprehensive business strategy for entering the AI market", "strategy", 0.9),
        ("Summarize recent trends in renewable energy", "research", 0.6),
    ]
    
    print("\nTesting Routing Logic:")
    for prompt, task_type, complexity in test_cases:
        provider = orch.route(task_type, complexity)
        print(f"\n  Task: {task_type} (complexity: {complexity})")
        print(f"  Routes to: {provider.upper()}")
    
    print("\n" + "="*60)
    
    # Make a real call
    print("\nMaking LIVE API call...")
    prompt = "In one sentence, what is the key to building compound systems?"
    
    result = await orch.generate(prompt, task_type="strategy", complexity=0.7)
    
    if result.get("success"):
        print(f"\n✓ Response from {result['provider'].upper()}:")
        print(f"  {result['content']}")
        print(f"\n  Tokens: {result['tokens_used']}")
        print(f"  Cost: ${result['cost']:.6f}")
        print(f"  Latency: {result['latency']:.2f}s")
    else:
        print(f"\n✗ Error: {result.get('error')}")
    
    print("\n" + "="*60)
    print("Stats:")
    stats = orch.get_stats()
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Total Tokens: {stats['total_tokens']}")
    print(f"  Total Cost: ${stats['total_cost']:.6f}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
