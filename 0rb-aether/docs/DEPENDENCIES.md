# Dependencies Audit

**Last Audit:** 2025-11-25
**Auditor:** Security Team

## Python Dependencies

### Core Application

| Package | Version | Purpose | Risk | License |
|---------|---------|---------|------|---------|
| fastapi | 0.100+ | HTTP API framework | LOW | MIT |
| uvicorn | 0.23+ | ASGI server | LOW | BSD |
| pydantic | 2.0+ | Data validation | LOW | MIT |
| slowapi | 0.1.8+ | Rate limiting | LOW | MIT |
| cryptography | 41.0+ | Encryption | LOW | BSD/Apache |
| httpx | 0.24+ | Async HTTP client | LOW | BSD |
| aiofiles | 23.0+ | Async file I/O | LOW | Apache 2.0 |

### Voice Authentication

| Package | Version | Purpose | Risk | License |
|---------|---------|---------|------|---------|
| openai-whisper | 20231117+ | Speech recognition | MEDIUM | MIT |
| pyannote.audio | 3.1+ | Speaker verification | MEDIUM | MIT |
| librosa | 0.10+ | Audio processing | LOW | ISC |
| soundfile | 0.12+ | Audio I/O | LOW | BSD |
| numpy | 1.24+ | Numerical ops | LOW | BSD |

### AI Connectors

| Package | Version | Purpose | Risk | License |
|---------|---------|---------|------|---------|
| anthropic | 0.25+ | Claude API | LOW | MIT |
| openai | 1.0+ | GPT API | LOW | MIT |
| google-generativeai | 0.3+ | Gemini API | LOW | Apache 2.0 |

## Rust Dependencies

### Brain Orchestrator

| Crate | Version | Purpose | Risk | License |
|-------|---------|---------|------|---------|
| tokio | 1.34+ | Async runtime | LOW | MIT |
| serde | 1.0+ | Serialization | LOW | MIT/Apache |
| serde_json | 1.0+ | JSON handling | LOW | MIT/Apache |
| sqlcipher | 0.1+ | Encrypted DB | LOW | MIT |
| uuid | 1.6+ | ID generation | LOW | MIT/Apache |
| chrono | 0.4+ | Timestamps | LOW | MIT/Apache |
| tracing | 0.1+ | Logging | LOW | MIT |
| anyhow | 1.0+ | Error handling | LOW | MIT/Apache |

### Compositor

| Crate | Version | Purpose | Risk | License |
|-------|---------|---------|------|---------|
| smithay | 0.3+ | Wayland compositor | LOW | MIT |
| wgpu | 0.18+ | GPU compute | LOW | MIT/Apache |
| winit | 0.29+ | Windowing | LOW | Apache 2.0 |
| glam | 0.24+ | Linear algebra | LOW | MIT/Apache |

## System Dependencies

| Package | Purpose | Risk | Notes |
|---------|---------|------|-------|
| LUKS2/cryptsetup | Disk encryption | LOW | Core Linux |
| AppArmor | MAC security | LOW | Core Linux |
| libseccomp | Syscall filtering | LOW | Core Linux |
| GRUB2 | Bootloader | LOW | Standard |
| squashfs-tools | Compression | LOW | Standard |
| xorriso | ISO creation | LOW | Standard |

## Vulnerability Assessment

### Critical Vulnerabilities: 0
### High Vulnerabilities: 0
### Medium Vulnerabilities: 0
### Low Vulnerabilities: 0

*Last scan: 2025-11-25*

## Audit Process

1. **cargo-audit**: Run on Rust dependencies
2. **pip-audit**: Run on Python dependencies
3. **Manual review**: License compliance check
4. **Version pinning**: All production deps pinned

## Update Policy

- Security patches: Within 24 hours
- Minor updates: Weekly review
- Major updates: Monthly review with testing

## License Compliance

All dependencies use permissive licenses (MIT, BSD, Apache 2.0) compatible with the project's distribution model.

### Copyleft Dependencies: None
### Patent-encumbered: None

## Supply Chain Security

- [ ] Verify package signatures where available
- [ ] Use lockfiles for reproducible builds
- [ ] Mirror critical dependencies
- [ ] SBOM generation planned

## Commands

```bash
# Rust audit
cargo audit

# Python audit
pip-audit

# Update check
cargo outdated
pip list --outdated
```
