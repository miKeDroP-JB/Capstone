# 🚀 0RB LIMITLESS OS - Quick Start Guide

## 30-Second Overview

**What is this?** A USB-bootable, AI-powered operating system with:
- Stunning 3D visual effects (metallic smoke, plasma, particles)
- AI agent swarm for collaborative problem-solving
- Voice-native control
- Ultra-secure (RAM-only, encrypted, anti-forensic)
- VAPI agent training system for sales automation

**Who is it for?**
- Developers who want portable, secure workspace
- AI enthusiasts exploring multi-agent systems
- Sales teams training voice AI agents
- Anyone who wants a jaw-dropping OS experience

---

## ⚡ 5-Minute Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/miKeDroP-JB/Capstone.git
cd Capstone
```

### Step 2: Install Dependencies

**For OS Build** (Linux/macOS):
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install build tools
sudo apt-get install build-essential pkg-config libssl-dev  # Ubuntu/Debian
# or
brew install pkg-config openssl  # macOS
```

**For VAPI Sparring System**:
```bash
cd vapi_sparring
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Step 3: Choose Your Path

**Path A: Build the OS** (requires 16GB+ USB drive)
```bash
cd 0rb-aether/build
./make_iso.sh
sudo dd if=0rb-aether.iso of=/dev/sdX bs=4M status=progress
```

**Path B: Test VAPI Sparring** (no USB needed)
```bash
cd vapi_sparring
python sparring_orchestrator.py single
```

**Path C: Run Visual Demo** (GPU required)
```bash
cd 0rb-aether/ui/compositor
cargo run --release
```

---

## 🎨 Visual System Demo (No OS Build Required)

Want to see the visuals without building the full OS?

```bash
cd 0rb-aether/ui/compositor
cargo build --release
cargo run --release
```

**What you'll see:**
- Metallic smoke storms
- Plasma effects
- 3D particle systems
- 60+ FPS GPU-accelerated rendering

**Controls:**
- Mouse: Move around to create particle trails
- ESC: Exit demo

---

## 🤖 VAPI Sparring System Quick Test

Test the AI agent training system without VAPI account:

```bash
cd vapi_sparring

# Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run a single test cycle (uses mock call data)
python sparring_orchestrator.py single
```

**What happens:**
1. Mock sales call generated
2. Claude Sonnet analyzes the call
3. Scores across 5 categories (0-50 total)
4. Extracts winning/losing patterns
5. Stores learnings in meta-brain

**Expected output:**
```
📊 RESULTS:
   Score: 42/50
   Would Convert: True (85% confidence)

✅ Winning Patterns:
   - Led with curiosity about prospect's business
   - Offered demo before asking for commitment
   - Handled objection smoothly

❌ Losing Patterns:
   - Took too long to get to value prop
   - Didn't emphasize risk reversal enough
```

---

## 🧠 AI Agent Swarm Demo

Test the tournament-based agent system:

```rust
// Add this to 0rb-aether/core/brain/examples/tournament_demo.rs

use orb_brain::agent_swarm::*;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let mut swarm = AgentSwarm::new();

    // Register agents
    swarm.register_agent(AgentNode::new(
        "Claude Opus".to_string(),
        "anthropic".to_string(),
        "claude-opus-4".to_string(),
        vec![AgentCapability::Reasoning, AgentCapability::CodeGeneration],
    ));

    swarm.register_agent(AgentNode::new(
        "GPT-4".to_string(),
        "openai".to_string(),
        "gpt-4-turbo".to_string(),
        vec![AgentCapability::NaturalLanguage, AgentCapability::CodeGeneration],
    ));

    // Run tournament
    let result = swarm.tournament(
        "Write a function to find prime numbers",
        "code"
    ).await?;

    println!("Winner: {}", result.winner.agent_name);
    println!("Consensus: {:.0}%", result.consensus_level * 100.0);

    Ok(())
}
```

```bash
cd 0rb-aether/core/brain
cargo run --example tournament_demo
```

---

## 🎤 Voice Control Test

Test voice command parsing without Whisper:

```rust
use orb_brain::voice_control::*;

fn main() {
    let vc = VoiceController::new("model.bin".to_string());

    // Simulate voice commands
    let commands = vec![
        "Open CREATE container",
        "Show dashboard",
        "Start tournament for: optimize this code",
        "Emergency shutdown",
    ];

    for cmd_text in commands {
        let cmd = vc.parse_command(cmd_text);
        println!("{} → {:?}", cmd_text, cmd);
    }
}
```

---

## 📊 Performance Benchmarks

Run benchmarks to verify your system meets requirements:

```bash
cd 0rb-aether/ui/compositor
cargo bench

# Expected results:
# - Frame rendering: <16ms (60+ FPS)
# - Particle system: 100k particles at 60 FPS
# - Shader compilation: <2s
```

---

## 🐛 Troubleshooting

### "Cargo not found"
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### "GPU not supported"
The compositor requires:
- Vulkan, Metal, or DX12 support
- Dedicated GPU recommended (integrated works but slower)

**Workaround**: Run with CPU fallback
```bash
WGPU_BACKEND=dx11 cargo run --release  # Windows
WGPU_BACKEND=gl cargo run --release     # Linux
```

### "ANTHROPIC_API_KEY not set"
```bash
# Get key from: https://console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-..."

# Or add to ~/.bashrc
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

### "dd: Permission denied"
```bash
# USB writing requires sudo
sudo dd if=0rb-aether.iso of=/dev/sdX bs=4M status=progress

# Find correct device:
lsblk  # Look for your USB drive (usually /dev/sdb or /dev/sdc)
```

---

## 🎯 Next Steps

### After Quick Start:

1. **Read Full Docs**: `README.md` for complete system overview
2. **Explore Components**:
   - `0rb-aether/core/brain/` - Brain orchestrator
   - `0rb-aether/ui/compositor/` - Visual system
   - `vapi_sparring/` - Agent training
3. **Join Community**: Discord, GitHub Discussions
4. **Contribute**: Submit PRs for improvements

### Common Workflows:

**Developer Workspace**:
```bash
# Build OS → Flash USB → Boot → Open CREATE → Voice: "Start IDE"
```

**AI Experimentation**:
```bash
# Run agent swarm demos → Test tournaments → Try discussions
```

**Sales Agent Training**:
```bash
# Configure VAPI → Run sparring → Monitor scores → Deploy when certified
```

---

## 💡 Pro Tips

1. **Faster Builds**: Use `cargo build --release -j8` (parallel compilation)
2. **Lower RAM**: Boot with `mem=2G` kernel parameter for 2GB systems
3. **Persistent Storage**: Mount encrypted USB partition for data persistence
4. **Multiple Containers**: Run multiple container instances simultaneously
5. **Voice Shortcuts**: Create custom voice macros for frequent tasks

---

## 📚 Learning Resources

- **Rust Book**: https://doc.rust-lang.org/book/
- **WebGPU**: https://gpuweb.github.io/gpuweb/
- **WGSL Shaders**: https://www.w3.org/TR/WGSL/
- **VAPI Docs**: https://vapi.ai/docs
- **Anthropic API**: https://docs.anthropic.com

---

## 🆘 Getting Help

**Before asking for help:**
1. Check `README.md` and this guide
2. Search existing GitHub Issues
3. Run with `RUST_LOG=debug` for detailed logs

**When asking for help, include:**
- OS and version (Ubuntu 22.04, macOS 14, etc.)
- Rust version (`rustc --version`)
- GPU info (`lspci | grep VGA`)
- Full error message
- Steps to reproduce

---

**Happy Building! 🚀**

*"The pleasure is all mine."* - 0RB
