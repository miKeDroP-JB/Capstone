//! Cinematic Sequence Engine
//! Experience architectures for the impossible

pub mod state;
pub mod player;
pub mod shaders;

pub use state::{SequenceState, SequenceType};
pub use player::SequencePlayer;
