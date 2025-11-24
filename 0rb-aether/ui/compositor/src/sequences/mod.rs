//! Cinematic Sequences Module
//!
//! Five dimensional gateways that transform 0RB_AETHER from software into experience:
//!
//! 1. **The Descent Into the Atlas** - Onboarding journey where the system learns you
//! 2. **The Ignition** - AGI birth sequence with shattering core and geometric halo
//! 3. **The Folding World** - Non-Euclidean 3iAtlas navigation
//! 4. **The Celestial Nerve Network** - Galaxy of agent minds
//! 5. **The Ascension Sequence** - The Impossible becomes Operational
//!
//! # Architecture
//!
//! ```text
//! sequences/
//! ├── mod.rs          # This file - module exports
//! ├── state.rs        # State machine (Idle, Playing, Paused, Complete)
//! ├── player.rs       # GPU sequence renderer
//! └── shaders/
//!     ├── descent.wgsl         # Sequence 1: Onboarding
//!     ├── ignition.wgsl        # Sequence 2: AGI Birth
//!     ├── folding.wgsl         # Sequence 3: Atlas Navigation
//!     ├── nerve_network.wgsl   # Sequence 4: Agent Swarm
//!     └── ascension.wgsl       # Sequence 5: OS Reveal
//! ```
//!
//! # Usage
//!
//! ```rust,ignore
//! use sequences::{SequenceStateMachine, SequencePlayer, SequenceType};
//!
//! // Initialize
//! let mut state_machine = SequenceStateMachine::new();
//! let player = SequencePlayer::new(&device, &config)?;
//!
//! // Start a sequence
//! state_machine.play(SequenceType::Descent);
//!
//! // In render loop
//! state_machine.update(delta_time);
//! if !state_machine.is_idle() {
//!     player.render(&mut encoder, &view, &queue, &state_machine, time);
//! }
//! ```
//!
//! # Controls
//!
//! - `1` - Start Descent Into the Atlas
//! - `2` - Start The Ignition
//! - `3` - Start The Folding World
//! - `4` - Start Celestial Nerve Network
//! - `5` - Start The Ascension Sequence
//! - `ESC` - Stop current sequence, return to ambient aether

pub mod state;
pub mod player;

pub use state::{SequenceState, SequenceStateMachine, SequenceType, SequenceParameters};
pub use player::{SequencePlayer, SequenceUniforms};
