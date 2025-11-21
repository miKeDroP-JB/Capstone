# Security Checklist

## Must-Pass for Release

- [ ] LUKS2 full disk encryption implemented & verified
- [ ] Enforced sandboxing per module (AppArmor profiles)
- [ ] Seccomp filters for each external process
- [ ] No network opened until user consent
- [ ] Logging to in-memory encrypted store
- [ ] Persistent logs optional and encrypted
- [ ] Emergency wipe tested on hardware variants
- [ ] Audit of all third-party libs (SCA)
- [ ] Threat model documentation

## Encryption

- Algorithm: AES-256-XTS
- KDF: Argon2id (memory-hard)
- LUKS version: 2
- Key slots: Minimum 2 (primary + recovery)

## Network Policy

- Default: All network blocked
- Opt-in: Explicit user confirmation required
- Logging: All network requests audited

## Anti-Forensics

- RAM wipe: 3-pass urandom overwrite
- Swap: Disabled
- Cache: Cleared on shutdown
- Logs: In-memory only (default)
