# 0RB_AETHER

**USB-Bootable RAM-Only Encrypted Meta-OS with Local AI Orchestration**

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████╗ ██████╗ ██████╗      █████╗ ███████╗████████╗    ║
║    ██╔═████╗██╔══██╗██╔══██╗    ██╔══██╗██╔════╝╚══██╔══╝    ║
║    ██║██╔██║██████╔╝██████╔╝    ███████║█████╗     ██║       ║
║    ████╔╝██║██╔══██╗██╔══██╗    ██╔══██║██╔══╝     ██║       ║
║    ╚██████╔╝██║  ██║██████╔╝    ██║  ██║███████╗   ██║       ║
║     ╚═════╝ ╚═╝  ╚═╝╚═════╝     ╚═╝  ╚═╝╚══════╝   ╚═╝       ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
```

## Overview

0RB_AETHER is a secure, privacy-focused operating system that runs entirely from RAM after booting from an encrypted USB drive. It provides AI orchestration capabilities with multi-provider support while maintaining strict security controls.

### Key Features

- **USB Boot**: Boot from any USB port, leave no trace
- **RAM-Only**: Entire system runs from memory - no disk writes
- **Encrypted**: LUKS2 + AES-256-XTS + Argon2id
- **Air-Gap Capable**: Fully functional without network
- **Voice Authenticated**: Speaker verification + passphrase
- **AI Orchestration**: Claude, Gemini, GPT with smart routing
- **Cost Optimized**: Track spending, route by complexity

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      0RB_AETHER SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐   │
│   │   Voice     │    │    Brain    │    │   Compositor    │   │
│   │   Auth      │───▶│ Orchestrator│───▶│   (Aether UI)   │   │
│   └─────────────┘    └─────────────┘    └─────────────────┘   │
│          │                  │                    │             │
│   ┌──────┴──────────────────┴────────────────────┴──────────┐ │
│   │              Security Layer (LUKS2, AppArmor)           │ │
│   └─────────────────────────────────────────────────────────┘ │
│   ┌─────────────────────────────────────────────────────────┐ │
│   │           RAM Filesystem (tmpfs + overlayfs)            │ │
│   └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Rust toolchain (for brain orchestrator)
- Linux system (for USB boot testing)

### Installation

```bash
# Clone the repository
git clone https://github.com/miKeDroP-JB/Capstone.git
cd Capstone

# Install Python dependencies
pip install -r requirements.txt

# Build Rust components (optional)
cd 0rb-aether/core/brain && cargo build --release && cd ../../..

# Run the launcher
python launcher.py
```

### Configuration

Edit `config.toml` to customize:

```toml
[system]
mode = "development"  # development | production | demo

[ai]
default_provider = "gemini"

[brain_os]
daily_budget = 10.0
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY="your-claude-key"
export GOOGLE_API_KEY="your-gemini-key"
export OPENAI_API_KEY="your-gpt-key"
```

## Project Structure

```
Capstone/
├── launcher.py          # Main entry point
├── config.toml          # Unified configuration
├── brain_os.py          # Python Brain OS (FastAPI)
├── brain_bridge.py      # Python↔Rust bridge
├── pipeline.py          # Full processing pipeline
├── ai_connectors.py     # AI provider clients
├── ekosystem.py         # Build orchestrator
├── glyph_core.py        # Token compression
├── test_integration.py  # Integration tests
│
└── 0rb-aether/          # Core system
    ├── core/
    │   ├── brain/       # Rust brain orchestrator
    │   └── security/    # AppArmor, seccomp, RAM wipe
    ├── ui/
    │   └── compositor/  # Wayland compositor
    ├── tools/
    │   └── asr/         # Voice authentication
    ├── build/           # ISO build scripts
    ├── ci/              # CI/CD pipeline
    └── docs/            # Documentation
```

## Components

### Brain Orchestrator (Rust)

High-performance intent parsing and routing:

```rust
// Intent parsing with confidence scoring
let intent = parse_intent("Build enterprise solution");
// category: BUILD, confidence: 0.85, provider_hint: claude
```

### Brain OS (Python)

7-layer security fortress:

1. Gate + Auth (HMAC tokens)
2. Audit Log (encrypted)
3. Cost Tracking
4. Rate Limiting
5. Encryption (Fernet)
6. Pattern Validation
7. Auto-Backup

### Pipeline

Complete flow: Voice → Auth → Parse → Route → AI → Response

```python
from pipeline import OrbPipeline

pipeline = OrbPipeline(config)
await pipeline.initialize()
result = await pipeline.process(text_input="Build an app")
```

### AI Routing

Smart routing based on task complexity:

| Task Type | Provider | Reason |
|-----------|----------|--------|
| Strategy/Code | Claude | Quality-focused |
| Research/Analysis | Gemini | Long context |
| Simple/Bulk | GPT | Cost-efficient |

## Security

### Encryption Stack

- **Disk**: LUKS2 + AES-256-XTS
- **KDF**: Argon2id (memory-hard)
- **Database**: SQLCipher
- **API Data**: Fernet

### Access Control

- AppArmor mandatory access control
- seccomp syscall filtering
- Unix socket with 0600 permissions

### Anti-Forensics

- 3-pass RAM wipe on shutdown
- Swap disabled
- In-memory logging default

See [Security Checklist](0rb-aether/docs/security-checklist.md) and [Threat Model](0rb-aether/docs/threat-model.md).

## Building USB Image

```bash
# Build the ISO
cd 0rb-aether/build
./make_iso.sh

# Write to USB (replace /dev/sdX)
sudo dd if=0rb-aether.iso of=/dev/sdX bs=4M status=progress
```

## Testing

```bash
# Run integration tests
python test_integration.py

# Expected output: 26 tests, 100% pass rate
```

## Business Model

### Two Channels

1. **eKo.vision (B2B)**: Enterprise AI solutions - "Extract from Elite"
2. **0r8.ai (B2C)**: Consumer AI tools - "Empower Humanity"

### Revenue Distribution

- B2B: 40% to community pool
- B2C: 25% to community pool
- Hybrid: 33% to community pool

*"The Builder Builds Builders. Everybody Eats."*

## API Reference

### Brain OS Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System status |
| `/register` | POST | Register agent |
| `/compress` | POST | Compress pattern |
| `/stats` | GET | Get statistics |
| `/costs` | GET | Budget status |
| `/audit` | GET | Audit logs |

### Pipeline Stages

1. `VOICE_INPUT` - Receive input
2. `VOICE_AUTH` - Authenticate speaker
3. `INTENT_PARSE` - Parse intent
4. `CONFIDENCE_CHECK` - Verify confidence
5. `AI_ROUTING` - Select provider
6. `AI_PROCESSING` - Get AI response
7. `RESPONSE` - Return result

## Contributing

1. Fork the repository
2. Create feature branch
3. Run tests: `python test_integration.py`
4. Submit pull request

## License

MIT License - See LICENSE file

## Acknowledgments

Built with:
- Anthropic Claude
- Google Gemini
- OpenAI GPT
- Rust + Tokio
- Python + FastAPI
- Smithay + wgpu

---

**Love - Loyalty - Honor - Everybody Eats**

*0RB_AETHER Capstone Project - 2025*
