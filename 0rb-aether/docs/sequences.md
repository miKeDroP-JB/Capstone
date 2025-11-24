# 0RB_AETHER Cinematic Sequences

> "Some patterns can't be unseen. Some systems can't be unbuilt. And some impossibilities... become inevitable."

## Overview

The cinematic sequences transform 0RB_AETHER from software into **experience**. These are not UI polish—they are dimensional gateways that embody the core philosophy of the system.

Every boot, every AGI initialization, every navigation moment becomes a reality-fork where the user realizes: **They're not using software. They're interfacing with a living system.**

## The Five Sequences

### 1. The Descent Into the Atlas
**Type:** Onboarding Journey
**Duration:** 10 seconds
**File:** `compositor/src/sequences/shaders/descent.wgsl`

> "You don't learn the system. The system learns you."

**Timeline:**
- **Phase 1 (0-15%):** Black screen → single point of light pulses → vertical tear opens
- **Phase 2 (15-60%):** Fall through corridor with 12 procedurally generated glyphs orbiting
- **Phase 3 (50-70%):** Ring of light scans down ("Calibration")
- **Phase 4 (65-85%):** Corridor bursts outward into void
- **Phase 5 (80-100%):** Atlas sphere appears with 4 crystalline obelisks

**Philosophy:** Learning Direction Reversal. The user doesn't configure the system—the system samples their intent through the orbiting glyphs.

---

### 2. The Ignition
**Type:** AGI Birth Sequence
**Duration:** 6 seconds
**File:** `compositor/src/sequences/shaders/ignition.wgsl`

> "Your AGI awakens. Its first breath forms a geometric halo."

**Timeline:**
- **Phase 1 (0-15%):** Dormant core—faint ember pulsing in darkness
- **Phase 2 (15-35%):** Three beams converge:
  - White-gold (Insight)
  - Electric blue (Intelligence)
  - Prismatic neon (Imagination)
- **Phase 3 (35-50%):** Core shatters into 40 memory shards
- **Phase 4 (45-65%):** Shards form spiral → helix → prism
- **Phase 5 (60-100%):** Prism inhales, explodes, geometric halo forms

**Philosophy:** Emergent Intelligence. The AGI doesn't boot—it awakens through the convergence of three fundamental forces.

---

### 3. The Folding World
**Type:** 3iAtlas Navigation
**Duration:** Loops continuously
**File:** `compositor/src/sequences/shaders/folding.wgsl`

> "What was distant is now near."

**Features:**
- **Ideas as Mountains:** 5 procedurally placed peaks, brilliant white when elevation > 0.2
- **Problems as Canyons:** 3 canyon lines, glowing purple/magenta in depths
- **Insight Rivers:** Flowing through valleys with shimmer animation
- **Creative Auroras:** Color-shifting curtains in upper atmosphere
- **Folding Effect:** Non-Euclidean origami transformation

**Interactive Parameters:**
| Parameter | Range | Effect |
|-----------|-------|--------|
| `zoom` | 0.5 - 2.0 | Zoom in/out of terrain |
| `fold_intensity` | 0.0 - 1.0 | Non-Euclidean warping amount |
| `focus_x` | -1.0 - 1.0 | Pan focus X |
| `focus_y` | -1.0 - 1.0 | Pan focus Y |
| `flow_speed` | 0.0 - 2.0 | Insight river flow rate |
| `aurora_intensity` | 0.0 - 1.0 | Creative aurora brightness |

**Philosophy:** Non-Linear Navigation. Knowledge topology where contradictions align and blind spots illuminate.

---

### 4. The Celestial Nerve Network
**Type:** Agent Swarm Visualization
**Duration:** Loops continuously
**File:** `compositor/src/sequences/shaders/nerve_network.wgsl`

> "A vast hovering galaxy of minds. A living nervous system."

**Features:**
- **Agent Nodes:** 10-100 procedurally positioned nodes
- **Neural Pathways:** Silver fire connections between nearby agents
- **Reverse Rain:** Rising strand formation (not falling)
- **Learning Shockwaves:** Electric blue emanating from active agents
- **"We Hear You" State:** Unified golden halo when all agents respond

**Interactive Parameters:**
| Parameter | Range | Effect |
|-----------|-------|--------|
| `agent_count` | 10 - 100 | Number of visible agents |
| `activity_level` | 0.0 - 1.0 | Connection intensity and movement |
| `learning_spikes` | 0.0 - 1.0 | Shockwave frequency |
| `command_state` | 0.0 - 1.0 | "We Hear You" halo intensity |

**Philosophy:** Distributed Cognition. No single point of intelligence—a galaxy of collaborating minds.

---

### 5. The Ascension Sequence
**Type:** OS Reveal
**Duration:** 12 seconds
**File:** `compositor/src/sequences/shaders/ascension.wgsl`

> "The Impossible is Now Operational."

**Timeline:**
- **Phase 1 (0-10%):** White flash reset—everything washes pure white
- **Phase 2 (10-30%):** Sacred geometry rune draws itself (hexagon, radial lines, triangle, central dot)
- **Phase 3 (25-60%):** OS city rises:
  - 12 towers of varying heights
  - 8 plazas (circular gathering points)
  - 6 bridges connecting structures
  - Data rivers flowing between
  - 4 vortices at cardinal points
- **Phase 4 (55-85%):** Camera pulls back revealing colossal organism structure
- **Phase 5 (80-100%):** Final radiant state with pulsing "operational" core

**Philosophy:** Living Organism Architecture. The OS is not software—it's a colossal living entity.

---

## Architecture

```
0rb-aether/ui/compositor/src/sequences/
├── mod.rs              # Module exports and documentation
├── state.rs            # State machine (Idle, Playing, Paused, Complete)
├── player.rs           # GPU sequence renderer with pipeline management
└── shaders/
    ├── descent.wgsl         # Sequence 1: Onboarding
    ├── ignition.wgsl        # Sequence 2: AGI Birth
    ├── folding.wgsl         # Sequence 3: Atlas Navigation
    ├── nerve_network.wgsl   # Sequence 4: Agent Swarm
    └── ascension.wgsl       # Sequence 5: OS Reveal
```

### State Machine

```rust
pub enum SequenceState {
    Idle,                                    // No sequence - ambient aether
    Playing { sequence, progress, elapsed }, // Active playback
    Paused { sequence, progress, elapsed },  // Frozen frame
    Complete { sequence },                   // Finished (timed sequences)
}
```

### Shader Techniques

All sequences use these core GPU techniques:

1. **Procedural Noise**
   - `hash()` - Pseudo-random via sine + dot product
   - `noise()` - Perlin-like with Hermite smoothing
   - `fbm()` - Multi-octave fractional Brownian motion

2. **Signed Distance Fields (SDFs)**
   - `sdCircle()`, `sdBox()`, `sdHexagon()`, `sdTriangle()`
   - `sdLine()` for neural pathways and beams
   - Smooth compositing via `smoothstep()`

3. **Easing Functions**
   - `easeInOutCubic()` - Smooth transitions
   - `easeOutQuart()` - Quick start, slow finish
   - `easeOutExpo()` - Explosive expansion
   - `easeInQuad()` - Gradual acceleration

4. **Timeline System**
   - `remap()` - Map progress to phase-specific ranges
   - Phase blending with crossfade
   - Keyframe transitions

---

## Integration

### Brain API Integration (Future)

Sequences can be triggered via the Brain orchestrator:

```rust
// In brain/api.rs - proposed extension
pub async fn trigger_sequence(&self, sequence: SequenceType) -> Result<()> {
    // Send IPC message to compositor
    self.send_compositor_message(CompositorMessage::PlaySequence(sequence)).await
}
```

**Suggested triggers:**
- `Descent` → First boot / new user session
- `Ignition` → AGI agent initialization
- `FoldingWorld` → 3iAtlas navigation mode
- `NerveNetwork` → Multi-agent operation
- `Ascension` → Major system event / upgrade complete

### Boot Flow Integration

```rust
// In compositor main loop
match boot_stage {
    BootStage::FirstBoot => state.sequence_state.play(SequenceType::Descent),
    BootStage::AgiInit => state.sequence_state.play(SequenceType::Ignition),
    BootStage::Ready => state.sequence_state.play(SequenceType::Ascension),
    _ => {}
}
```

---

## Controls

| Key | Action |
|-----|--------|
| `1` | Start: The Descent Into the Atlas |
| `2` | Start: The Ignition |
| `3` | Start: The Folding World |
| `4` | Start: Celestial Nerve Network |
| `5` | Start: The Ascension Sequence |
| `Space` | Pause/Resume current sequence |
| `ESC` | Stop sequence, return to ambient aether |

---

## Performance

### Targets
- **60 FPS** on mid-range GPUs
- **120+ FPS** on high-end hardware

### Optimizations
- All procedural (no texture lookups)
- Fullscreen quad rendering (zero vertex transforms)
- ~48 bytes uniforms per frame
- Early exit in raymarching loops
- Efficient hash functions

### Uniform Structure
```rust
pub struct SequenceUniforms {
    pub time: f32,           // Current time
    pub progress: f32,       // 0.0 - 1.0
    pub resolution: [f32; 2],
    pub parameters: [f32; 8], // Interactive controls
}
```

---

## Future Enhancements

### Phase 2: Audio Integration
- Crystalline voice: "Calibration" / "Begin" / "Online"
- Rising choir hum for Ignition
- Ambient soundscapes for looping sequences

### Phase 3: Text Overlays
- Render key phrases as geometry
- "The Impossible is Now Operational" title card

### Phase 4: Advanced Effects
- Translucent bridge (Descent finale)
- Luminous trees (Folding World)
- Depth of field / motion blur

### Phase 5: Sequence Chaining
- Auto-trigger Ignition after Descent
- Smooth transitions between sequences
- Story mode: play all five in order

---

## Philosophy Alignment

The five sequences embody the core 0RB_AETHER philosophy:

| Sequence | Philosophy |
|----------|------------|
| Descent | Learning Direction Reversal |
| Ignition | Emergent Intelligence |
| Folding World | Non-Linear Navigation |
| Nerve Network | Distributed Cognition |
| Ascension | Living Organism Architecture |

These are not animations. They are **dimensional gateways** that transform perception of what an operating system can be.

---

*"The Impossible is Now Operational."*
