# Security Checklist

**Last Updated:** 2025-11-25
**Status:** Pre-Release Review

## Must-Pass for Release

- [x] LUKS2 full disk encryption implemented & verified
  - Configured in `config.toml` and `make_iso.sh`
  - AES-256-XTS with Argon2id KDF
- [x] Enforced sandboxing per module (AppArmor profiles)
  - Profile: `core/security/apparmor/orb-brain`
- [x] Seccomp filters for each external process
  - Policy: `core/security/seccomp/brain.json`
- [x] No network opened until user consent
  - Default policy: DENY in `config.toml`
  - Requires explicit user confirmation
- [x] Logging to in-memory encrypted store
  - SQLCipher encrypted database
  - Fernet encryption layer in Python
- [x] Persistent logs optional and encrypted
  - Controlled via `config.toml`
- [ ] Emergency wipe tested on hardware variants
  - Script exists: `core/security/ram_wipe.sh`
  - **PENDING:** Hardware testing required
- [x] Audit of all third-party libs (SCA)
  - See `DEPENDENCIES.md` for full audit
- [x] Threat model documentation
  - See `threat-model.md`

## Encryption

| Component | Algorithm | Status |
|-----------|-----------|--------|
| Disk Encryption | AES-256-XTS | Implemented |
| KDF | Argon2id (memory-hard) | Implemented |
| LUKS version | 2 | Configured |
| Key slots | 2 (primary + recovery) | Configured |
| Database | SQLCipher | Implemented |
| API Data | Fernet (AES-128-CBC) | Implemented |

## Network Policy

| Rule | Status | Notes |
|------|--------|-------|
| Default policy | DENY | All network blocked |
| Opt-in | Required | Explicit user confirmation |
| Logging | Enabled | All network requests audited |
| Air-gap mode | Supported | Can run fully offline |

## Anti-Forensics

| Feature | Status | Implementation |
|---------|--------|----------------|
| RAM wipe | Implemented | 3-pass urandom via `ram_wipe.sh` |
| Swap | Disabled | Enforced at boot |
| Cache | Cleared | On shutdown |
| Logs | In-memory | Default; persistent optional |

## Authentication

| Method | Status | Fallback |
|--------|--------|----------|
| Voice Auth | Implemented | 8-digit PIN |
| Speaker Verification | Implemented | Passphrase |
| Emergency Kill | Implemented | Triple-tap |

## Code Security

- [x] Input validation (PatternValidator)
- [x] Injection protection (blocked phrases)
- [x] Rate limiting (slowapi)
- [x] HMAC token authentication
- [x] Secure random generation (secrets module)
- [x] No hardcoded credentials in production

## CI/CD Security

- [x] cargo-audit for Rust dependencies
- [x] Seccomp JSON validation
- [x] Build isolation in GitHub Actions
