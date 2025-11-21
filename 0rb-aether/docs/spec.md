# 0RB_AETHER Engine Specification

## Overview

USB-bootable, RAM-only, encrypted, air-gap capable Meta-OS with local AI orchestration.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    0RB_AETHER System                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Voice     │  │   Brain     │  │    Compositor       │ │
│  │   Auth      │──│ Orchestrator│──│   (Aether UI)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │               │                    │              │
│  ┌──────┴───────────────┴────────────────────┴──────────┐  │
│  │              Security Layer (LUKS2, AppArmor)        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           RAM Filesystem (tmpfs + overlayfs)         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Boot Flow

1. BIOS/UEFI loads bootloader from USB
2. Initramfs prompts for LUKS passphrase (voice or PIN)
3. LUKS container unlocked
4. Rootfs copied to tmpfs (RAM)
5. LUKS closed (no disk access needed)
6. System runs entirely from RAM
7. On shutdown: secure RAM wipe

## Components

### Brain Orchestrator
- Intent parsing via local LLM
- Confidence scoring (95%+ for autonomous actions)
- Security gating
- Audit logging
- JSON-RPC API on Unix socket

### Voice Authentication
- VAD → ASR (whisper.cpp) → Speaker Verification
- Fallback: 8-digit PIN + passphrase
- Emergency: triple-tap kill switch

### Compositor
- Wayland-based (Smithay)
- GPU-accelerated Aether visuals
- WebAssembly UI layer

## Security

- LUKS2 + Argon2id + AES-256-XTS
- AppArmor mandatory access control
- seccomp syscall filtering
- No network by default
- Anti-forensic RAM wipe
