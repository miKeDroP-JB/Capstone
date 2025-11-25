# FlowSync SDK — Python

**Route through 3i-ATLAS. Summon Demigods. Build the future.**

FlowSync is the official Python SDK for [0r8](https://0r8.ai) — The Operating System for Human Potential.

## Installation

```bash
pip install flowsync
```

## Quick Start

```python
from flowsync import FlowSync

# Initialize the client
client = FlowSync(api_key="your-api-key")

# Route a message through 3i-ATLAS
response = client.route(
    user_id="user-123",
    message="Help me build a business strategy",
    mode="analyst",
    demigod="athena"
)

print(f"Demigod: {response.demigod['name']}")
print(f"Temperature: {response.temperature}")
print(f"Weights: {response.weights.to_dict()}")
```

## The 3i Framework

0r8 is built on the **3i Framework**:

- **I₁ NOUS (☿)** — Intelligence — The Mind
- **I₂ ANIMA (🜍)** — Intuition — The Soul
- **I₃ HOLOS (🜔)** — Integration — The Whole

Formula: `I₁ + I₂ = I₃`

## Processing Modes

| Mode | NOUS | ANIMA | HOLOS | Best For |
|------|------|-------|-------|----------|
| `analyst` | 90% | 30% | 50% | Analysis, research, data |
| `creator` | 50% | 90% | 60% | Creative work, art, design |
| `executor` | 70% | 40% | 90% | Getting things done |
| `sage` | 70% | 70% | 70% | Balanced wisdom |
| `transcendent` | 100% | 100% | 100% | Maximum power |

## The 7 Demigods

### NOUS Pillar (Intelligence)
- **Athena** 🦉 — Strategy & Wisdom
- **Mercury** ⚡ — Speed & Communication
- **Hephaestus** 🔨 — Building & Craft

### ANIMA Pillar (Intuition)
- **Apollo** ☀️ — Vision & Light
- **Artemis** 🏹 — Precision & Wild

### HOLOS Pillar (Integration)
- **Hermes** 🪽 — Execution & Speed
- **Ares** ⚔️ — Action & Courage

## Using the Router

```python
from flowsync import FlowSync, Router

client = FlowSync(api_key="your-key")
router = Router(client)

# Specialized routing
analysis = router.analyze("user-1", "Analyze this dataset")
creative = router.create("user-1", "Design a logo concept")
execution = router.execute("user-1", "Ship this feature")
strategy = router.strategy("user-1", "Plan market expansion")
code = router.code("user-1", "Build a REST API")
```

## Using the Demigod Selector

```python
from flowsync import DemigodSelector

selector = DemigodSelector()

# Auto-select based on message
demigod_id, info = selector.select("Help me write efficient code")
print(f"Selected: {info['name']} ({info['symbol']})")

# Select by task type
demigod_id, info = selector.select_for_task("code")
```

## Governance & Alignment

```python
# Get governance status
status = client.governance_status()
print(f"Total agents: {status.total_agents}")
print(f"Active keys: {status.active_keys}")

# Register an agent
fingerprint = client.register_agent("agent-001", "My Agent")
print(f"Alignment score: {fingerprint.alignment_score}")

# Request authorization for risky actions
result = client.request_authorization(
    action_id="action-123",
    action_type="financial_transfer",
    risk_level="high",
    agent_id="agent-001"
)
```

## Life Domains

Route for specific life contexts:

```python
from flowsync.routing import DomainRouter

domains = DomainRouter(client, "user-123")

domains.work("Optimize my workflow")
domains.school("Explain quantum physics")
domains.create("Write a poem about the ocean")
domains.health("Plan a workout routine")
```

## Historical Flavors

Infuse the wisdom of historical figures:

```python
response = client.route(
    user_id="user-123",
    message="Help me innovate",
    historical_flavor="tesla"  # Think like Nikola Tesla
)
```

Available flavors: `leonardo`, `tesla`, `jobs`, `sun_tzu`, `rumi`, `curie`, `einstein`, `aurelius`

## Custom Weights

Fine-tune the 3i balance:

```python
response = client.route(
    user_id="user-123",
    message="Creative analysis",
    custom_weights={
        "nous": 0.6,    # 60% intelligence
        "anima": 0.7,   # 70% intuition
        "holos": 0.5    # 50% integration
    }
)
```

## API Reference

### FlowSync Client

```python
FlowSync(
    api_key: str,           # Your 0r8 API key
    base_url: str = "...",  # API endpoint
    timeout: int = 30       # Request timeout
)
```

### Core Methods

- `route()` — Route a message through 3i-ATLAS
- `list_demigods()` — List all Demigods
- `list_domains()` — List life domains
- `list_modules()` — List 9 AGI modules
- `get_harmony()` — Get user harmony profile
- `governance_status()` — Get governance system status

## Community

- **The Collective** — Join the movement
- **The Awakening** — Black Friday 2025

---

**Built by one. Owned by all. Everybody eats.**

*0r8 = Transmutation Engine*
