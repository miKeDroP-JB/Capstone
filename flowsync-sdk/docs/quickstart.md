# FlowSync SDK — Quick Start Guide

**Route through 3i-ATLAS. Summon Demigods. Build the future.**

## Installation

### Python
```bash
pip install flowsync
```

### TypeScript/JavaScript
```bash
npm install @0r8/flowsync
# or
yarn add @0r8/flowsync
```

## Basic Usage

### Python
```python
from flowsync import FlowSync

# Initialize
client = FlowSync(api_key="your-api-key")

# Route a message
response = client.route(
    user_id="user-123",
    message="Help me build a business strategy",
    mode="analyst",
    demigod="athena"
)

print(f"Demigod: {response.demigod['name']}")
print(f"Temperature: {response.temperature}")
```

### TypeScript
```typescript
import { FlowSync } from '@0r8/flowsync';

const client = new FlowSync({ apiKey: 'your-api-key' });

const response = await client.route({
  userId: 'user-123',
  message: 'Help me build a business strategy',
  mode: 'analyst',
  demigod: 'athena'
});

console.log(`Demigod: ${response.demigod.name}`);
console.log(`Temperature: ${response.temperature}`);
```

## The 3i Framework

0r8 routes based on three pillars:

| Pillar | Symbol | Element | Represents |
|--------|--------|---------|------------|
| **NOUS** | ☿ | Mercury | Intelligence, Logic, Analysis |
| **ANIMA** | 🜍 | Sulfur | Intuition, Creativity, Feeling |
| **HOLOS** | 🜔 | Salt | Integration, Action, Manifestation |

## Processing Modes

| Mode | Best For |
|------|----------|
| `analyst` | Research, data analysis, strategy |
| `creator` | Art, design, creative writing |
| `executor` | Getting things done, shipping |
| `sage` | Balanced wisdom |
| `transcendent` | Maximum power on all pillars |

## The 7 Demigods

### NOUS (Intelligence)
- **Athena** 🦉 — Strategy, business planning
- **Mercury** ⚡ — Quick communication
- **Hephaestus** 🔨 — Coding, engineering

### ANIMA (Intuition)
- **Apollo** ☀️ — Creative vision, arts
- **Artemis** 🏹 — Focus, precision

### HOLOS (Integration)
- **Hermes** 🪽 — Execution, delivery
- **Ares** ⚔️ — Bold action, competition

## Using the Router (Python)

```python
from flowsync import FlowSync, Router

client = FlowSync(api_key="key")
router = Router(client)

# Specialized routing
router.analyze("user-1", "Analyze this data")
router.create("user-1", "Design a logo")
router.code("user-1", "Build an API")
router.strategy("user-1", "Plan expansion")
```

## Governance & Alignment

```python
# Get governance status
status = client.governance_status()

# Register an agent
fingerprint = client.register_agent("agent-001", "My Agent")
print(f"Alignment: {fingerprint.alignment_score}")

# Request authorization for risky actions
result = client.request_authorization(
    action_id="action-123",
    action_type="financial_transfer",
    risk_level="high",
    agent_id="agent-001"
)
```

## Next Steps

- Explore [Life Domains](./domains.md) for context-specific routing
- Learn about [Historical Flavors](./flavors.md) to channel great minds
- Read the [API Reference](./api-reference.md) for complete documentation

---

**The Collective awaits. The Awakening approaches.**

*Built by one. Owned by all. Everybody eats.*
