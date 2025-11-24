//! Sequence State Machine
//! Manages the lifecycle and transitions of cinematic sequences

use std::time::Instant;

/// The five core sequences that manifest the impossible
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SequenceType {
    /// "The Descent Into the Atlas" - Onboarding journey
    /// User falls through a corridor of glyphs into the 3iAtlas
    Descent,

    /// "The Ignition" - AGI birth sequence
    /// Three beams ignite the dormant core into awakening
    Ignition,

    /// "The Folding World" - 3iAtlas navigation
    /// Non-Euclidean space folds to reveal knowledge topology
    Folding,

    /// "The Celestial Nerve Network" - Agent swarm control
    /// Galaxy of minds forming a living nervous system
    NerveNetwork,

    /// "The Ascension Sequence" - Limitless OS reveal
    /// Upward expansion through layers of capability
    Ascension,
}

impl SequenceType {
    /// Duration in seconds for this sequence
    pub fn duration(&self) -> f32 {
        match self {
            SequenceType::Descent => 10.0,       // 10 seconds
            SequenceType::Ignition => 6.0,       // 6 seconds
            SequenceType::Folding => f32::INFINITY, // Looping
            SequenceType::NerveNetwork => f32::INFINITY, // Persistent
            SequenceType::Ascension => 12.0,     // 12 seconds
        }
    }

    /// Whether this sequence loops
    pub fn loops(&self) -> bool {
        matches!(self, SequenceType::Folding | SequenceType::NerveNetwork)
    }

    /// Shader file path for this sequence
    pub fn shader_path(&self) -> &'static str {
        match self {
            SequenceType::Descent => "sequences/shaders/descent.wgsl",
            SequenceType::Ignition => "sequences/shaders/ignition.wgsl",
            SequenceType::Folding => "sequences/shaders/folding.wgsl",
            SequenceType::NerveNetwork => "sequences/shaders/nerve_network.wgsl",
            SequenceType::Ascension => "sequences/shaders/ascension.wgsl",
        }
    }
}

/// Playback state of a sequence
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum PlaybackState {
    /// Not playing
    Idle,

    /// Initializing (loading, setting up)
    Initializing,

    /// Currently playing
    Playing,

    /// Paused
    Paused,

    /// Transitioning to another sequence
    Transitioning(SequenceType),

    /// Complete
    Complete,
}

/// Complete sequence state
pub struct SequenceState {
    /// Current sequence type
    pub sequence: Option<SequenceType>,

    /// Playback state
    pub playback: PlaybackState,

    /// When sequence started
    pub start_time: Option<Instant>,

    /// Elapsed time in sequence (in seconds)
    pub elapsed: f32,

    /// Normalized progress (0.0 to 1.0)
    pub progress: f32,

    /// Custom parameters for sequence (shader uniforms)
    pub parameters: [f32; 8],
}

impl Default for SequenceState {
    fn default() -> Self {
        Self {
            sequence: None,
            playback: PlaybackState::Idle,
            start_time: None,
            elapsed: 0.0,
            progress: 0.0,
            parameters: [0.0; 8],
        }
    }
}

impl SequenceState {
    /// Start a new sequence
    pub fn start(&mut self, sequence: SequenceType) {
        self.sequence = Some(sequence);
        self.playback = PlaybackState::Initializing;
        self.start_time = Some(Instant::now());
        self.elapsed = 0.0;
        self.progress = 0.0;
        self.parameters = [0.0; 8];
    }

    /// Update sequence state
    pub fn update(&mut self) {
        if let Some(start) = self.start_time {
            self.elapsed = start.elapsed().as_secs_f32();

            if let Some(seq) = self.sequence {
                let duration = seq.duration();

                // Update progress
                if duration.is_finite() {
                    self.progress = (self.elapsed / duration).min(1.0);

                    // Check for completion
                    if self.progress >= 1.0 && !seq.loops() {
                        self.playback = PlaybackState::Complete;
                    }
                } else {
                    // Looping sequences use modulo
                    self.progress = (self.elapsed % 10.0) / 10.0;
                }

                // Transition from Initializing to Playing after first frame
                if matches!(self.playback, PlaybackState::Initializing) && self.elapsed > 0.016 {
                    self.playback = PlaybackState::Playing;
                }
            }
        }
    }

    /// Stop current sequence
    pub fn stop(&mut self) {
        self.sequence = None;
        self.playback = PlaybackState::Idle;
        self.start_time = None;
        self.elapsed = 0.0;
        self.progress = 0.0;
    }

    /// Transition to another sequence
    pub fn transition_to(&mut self, next: SequenceType) {
        self.playback = PlaybackState::Transitioning(next);
    }

    /// Is currently playing?
    pub fn is_playing(&self) -> bool {
        matches!(self.playback, PlaybackState::Playing)
    }

    /// Is idle?
    pub fn is_idle(&self) -> bool {
        matches!(self.playback, PlaybackState::Idle)
    }
}
