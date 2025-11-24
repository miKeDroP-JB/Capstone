//! Sequence State Machine
//! Manages lifecycle of cinematic sequences: Idle -> Playing -> Complete

use std::time::Duration;

/// Types of cinematic sequences available
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SequenceType {
    /// "The Descent Into the Atlas" - Onboarding journey (10s)
    Descent,
    /// "The Ignition" - AGI birth sequence (6s)
    Ignition,
    /// "The Folding World" - 3iAtlas navigation (looping)
    FoldingWorld,
    /// "The Celestial Nerve Network" - Agent swarm (looping)
    NerveNetwork,
    /// "The Ascension Sequence" - OS reveal (12s)
    Ascension,
}

impl SequenceType {
    /// Duration of the sequence (None = loops infinitely)
    pub fn duration(&self) -> Option<Duration> {
        match self {
            SequenceType::Descent => Some(Duration::from_secs(10)),
            SequenceType::Ignition => Some(Duration::from_secs(6)),
            SequenceType::FoldingWorld => None, // Loops
            SequenceType::NerveNetwork => None, // Loops
            SequenceType::Ascension => Some(Duration::from_secs(12)),
        }
    }

    /// Whether this sequence loops continuously
    pub fn loops(&self) -> bool {
        self.duration().is_none()
    }

    /// Sequence index for shader dispatch
    pub fn index(&self) -> u32 {
        match self {
            SequenceType::Descent => 1,
            SequenceType::Ignition => 2,
            SequenceType::FoldingWorld => 3,
            SequenceType::NerveNetwork => 4,
            SequenceType::Ascension => 5,
        }
    }
}

/// Current state of a sequence
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SequenceState {
    /// No sequence active - show ambient aether
    Idle,
    /// Sequence is playing
    Playing {
        sequence: SequenceType,
        /// Progress from 0.0 to 1.0 (for timed sequences)
        progress: f32,
        /// Elapsed time in seconds
        elapsed: f32,
    },
    /// Sequence is paused
    Paused {
        sequence: SequenceType,
        progress: f32,
        elapsed: f32,
    },
    /// Sequence has completed
    Complete {
        sequence: SequenceType,
    },
}

impl Default for SequenceState {
    fn default() -> Self {
        SequenceState::Idle
    }
}

/// Interactive parameters for sequences that support them
#[derive(Debug, Clone, Copy)]
pub struct SequenceParameters {
    /// Zoom level (0.5 - 2.0) for FoldingWorld
    pub zoom: f32,
    /// Fold intensity (0.0 - 1.0) for FoldingWorld
    pub fold_intensity: f32,
    /// Focus point X (-1.0 - 1.0)
    pub focus_x: f32,
    /// Focus point Y (-1.0 - 1.0)
    pub focus_y: f32,
    /// Flow speed (0.0 - 2.0) for insight rivers
    pub flow_speed: f32,
    /// Aurora intensity (0.0 - 1.0)
    pub aurora_intensity: f32,
    /// Agent count (10-100) for NerveNetwork
    pub agent_count: u32,
    /// Activity level (0.0 - 1.0) for NerveNetwork
    pub activity_level: f32,
    /// Learning spike intensity (0.0 - 1.0)
    pub learning_spikes: f32,
    /// "We Hear You" unified state (0.0 - 1.0)
    pub command_state: f32,
}

impl Default for SequenceParameters {
    fn default() -> Self {
        Self {
            zoom: 1.0,
            fold_intensity: 0.0,
            focus_x: 0.0,
            focus_y: 0.0,
            flow_speed: 1.0,
            aurora_intensity: 0.5,
            agent_count: 40,
            activity_level: 0.5,
            learning_spikes: 0.0,
            command_state: 0.0,
        }
    }
}

/// State machine for managing sequence playback
pub struct SequenceStateMachine {
    state: SequenceState,
    parameters: SequenceParameters,
}

impl SequenceStateMachine {
    pub fn new() -> Self {
        Self {
            state: SequenceState::Idle,
            parameters: SequenceParameters::default(),
        }
    }

    /// Get current state
    pub fn state(&self) -> &SequenceState {
        &self.state
    }

    /// Get current parameters
    pub fn parameters(&self) -> &SequenceParameters {
        &self.parameters
    }

    /// Get mutable parameters for interactive control
    pub fn parameters_mut(&mut self) -> &mut SequenceParameters {
        &mut self.parameters
    }

    /// Start playing a sequence
    pub fn play(&mut self, sequence: SequenceType) {
        self.state = SequenceState::Playing {
            sequence,
            progress: 0.0,
            elapsed: 0.0,
        };
    }

    /// Pause current sequence
    pub fn pause(&mut self) {
        if let SequenceState::Playing { sequence, progress, elapsed } = self.state {
            self.state = SequenceState::Paused { sequence, progress, elapsed };
        }
    }

    /// Resume paused sequence
    pub fn resume(&mut self) {
        if let SequenceState::Paused { sequence, progress, elapsed } = self.state {
            self.state = SequenceState::Playing { sequence, progress, elapsed };
        }
    }

    /// Stop current sequence and return to idle
    pub fn stop(&mut self) {
        self.state = SequenceState::Idle;
    }

    /// Update state with delta time, returns true if sequence completed
    pub fn update(&mut self, dt: f32) -> bool {
        match &mut self.state {
            SequenceState::Playing { sequence, progress, elapsed } => {
                *elapsed += dt;

                if let Some(duration) = sequence.duration() {
                    let duration_secs = duration.as_secs_f32();
                    *progress = (*elapsed / duration_secs).min(1.0);

                    if *progress >= 1.0 {
                        let seq = *sequence;
                        self.state = SequenceState::Complete { sequence: seq };
                        return true;
                    }
                } else {
                    // Looping sequence - progress is used for animation phase
                    *progress = (*elapsed % 10.0) / 10.0;
                }
            }
            _ => {}
        }
        false
    }

    /// Check if currently playing
    pub fn is_playing(&self) -> bool {
        matches!(self.state, SequenceState::Playing { .. })
    }

    /// Check if idle
    pub fn is_idle(&self) -> bool {
        matches!(self.state, SequenceState::Idle)
    }

    /// Get current sequence type if any
    pub fn current_sequence(&self) -> Option<SequenceType> {
        match self.state {
            SequenceState::Playing { sequence, .. } => Some(sequence),
            SequenceState::Paused { sequence, .. } => Some(sequence),
            SequenceState::Complete { sequence } => Some(sequence),
            SequenceState::Idle => None,
        }
    }

    /// Get current progress (0.0-1.0)
    pub fn progress(&self) -> f32 {
        match self.state {
            SequenceState::Playing { progress, .. } => progress,
            SequenceState::Paused { progress, .. } => progress,
            SequenceState::Complete { .. } => 1.0,
            SequenceState::Idle => 0.0,
        }
    }

    /// Get elapsed time in seconds
    pub fn elapsed(&self) -> f32 {
        match self.state {
            SequenceState::Playing { elapsed, .. } => elapsed,
            SequenceState::Paused { elapsed, .. } => elapsed,
            _ => 0.0,
        }
    }
}

impl Default for SequenceStateMachine {
    fn default() -> Self {
        Self::new()
    }
}
