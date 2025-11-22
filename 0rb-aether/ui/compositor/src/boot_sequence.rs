//! 0RB Boot Sequence
//!
//! Manages the dramatic boot animation and container reveal

use std::time::Duration;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BootPhase {
    BlackVoid,           // Pure black screen
    SmokeEmergence,      // Metallic smoke swirls from edges
    OrbRising,           // 0RB image erupts
    Dialogue,            // Text dialogue with 0RB
    Explosion,           // Smoke/light explosion
    ContainerReveal,     // Containers appear
    Ready,               // System ready
}

#[derive(Debug, Clone)]
pub struct BootSequence {
    pub current_phase: BootPhase,
    pub phase_progress: f32,  // 0.0 to 1.0
    pub total_elapsed: f32,
    pub dialogue_state: DialogueState,
}

#[derive(Debug, Clone)]
pub struct DialogueState {
    pub orb_text: String,
    pub user_text: String,
    pub orb_shown: bool,
    pub user_shown: bool,
    pub awaiting_user_input: bool,
}

impl BootSequence {
    pub fn new() -> Self {
        Self {
            current_phase: BootPhase::BlackVoid,
            phase_progress: 0.0,
            total_elapsed: 0.0,
            dialogue_state: DialogueState {
                orb_text: "And so what do I owe this pleasure?".to_string(),
                user_text: String::new(),
                orb_shown: false,
                user_shown: false,
                awaiting_user_input: false,
            },
        }
    }

    pub fn update(&mut self, delta_time: f32) -> bool {
        self.total_elapsed += delta_time;
        self.phase_progress += delta_time / self.phase_duration();

        if self.phase_progress >= 1.0 {
            self.advance_phase();
        }

        self.current_phase == BootPhase::Ready
    }

    fn phase_duration(&self) -> f32 {
        match self.current_phase {
            BootPhase::BlackVoid => 1.5,        // 1.5s of pure black
            BootPhase::SmokeEmergence => 3.0,   // 3s smoke swirl
            BootPhase::OrbRising => 2.5,        // 2.5s orb eruption
            BootPhase::Dialogue => 999.0,       // Wait for user input
            BootPhase::Explosion => 2.0,        // 2s explosion
            BootPhase::ContainerReveal => 3.0,  // 3s container reveal
            BootPhase::Ready => 999.0,
        }
    }

    fn advance_phase(&mut self) {
        self.phase_progress = 0.0;

        self.current_phase = match self.current_phase {
            BootPhase::BlackVoid => {
                BootPhase::SmokeEmergence
            }
            BootPhase::SmokeEmergence => {
                BootPhase::OrbRising
            }
            BootPhase::OrbRising => {
                self.dialogue_state.orb_shown = true;
                self.dialogue_state.awaiting_user_input = true;
                BootPhase::Dialogue
            }
            BootPhase::Dialogue => {
                // Only advance if user provided correct response
                if self.dialogue_state.user_text.to_lowercase().contains("pleasure is all mine") {
                    BootPhase::Explosion
                } else {
                    BootPhase::Dialogue  // Stay in dialogue
                }
            }
            BootPhase::Explosion => {
                BootPhase::ContainerReveal
            }
            BootPhase::ContainerReveal => {
                BootPhase::Ready
            }
            BootPhase::Ready => BootPhase::Ready,
        };
    }

    pub fn handle_user_input(&mut self, text: String) {
        if self.current_phase == BootPhase::Dialogue {
            self.dialogue_state.user_text = text;
            self.dialogue_state.user_shown = true;
            self.dialogue_state.awaiting_user_input = false;

            // Check if response is correct
            if self.dialogue_state.user_text.to_lowercase().contains("pleasure is all mine") {
                self.phase_progress = 1.0;  // Trigger phase advance
            }
        }
    }

    /// Get shader uniforms for current boot phase
    pub fn get_uniforms(&self) -> BootUniforms {
        BootUniforms {
            phase: self.current_phase as u32,
            progress: self.phase_progress,
            total_time: self.total_elapsed,
            smoke_intensity: self.smoke_intensity(),
            orb_brightness: self.orb_brightness(),
            explosion_power: self.explosion_power(),
        }
    }

    fn smoke_intensity(&self) -> f32 {
        match self.current_phase {
            BootPhase::BlackVoid => 0.0,
            BootPhase::SmokeEmergence => self.phase_progress,
            BootPhase::OrbRising => 1.0,
            BootPhase::Dialogue => 0.8,
            BootPhase::Explosion => 1.0 - self.phase_progress * 0.5,
            BootPhase::ContainerReveal => 0.3,
            BootPhase::Ready => 0.2,
        }
    }

    fn orb_brightness(&self) -> f32 {
        match self.current_phase {
            BootPhase::BlackVoid | BootPhase::SmokeEmergence => 0.0,
            BootPhase::OrbRising => self.phase_progress,
            BootPhase::Dialogue => 1.0,
            BootPhase::Explosion => 1.5,  // Over-bright during explosion
            BootPhase::ContainerReveal => 1.0 - self.phase_progress * 0.7,
            BootPhase::Ready => 0.3,
        }
    }

    fn explosion_power(&self) -> f32 {
        match self.current_phase {
            BootPhase::Explosion => {
                // Exponential explosion curve
                let t = self.phase_progress;
                if t < 0.3 {
                    t / 0.3  // Rise
                } else {
                    1.0 - ((t - 0.3) / 0.7).powi(2)  // Fall off
                }
            }
            _ => 0.0,
        }
    }
}

#[repr(C)]
#[derive(Debug, Copy, Clone, bytemuck::Pod, bytemuck::Zeroable)]
pub struct BootUniforms {
    pub phase: u32,
    pub progress: f32,
    pub total_time: f32,
    pub smoke_intensity: f32,
    pub orb_brightness: f32,
    pub explosion_power: f32,
    _padding: [u32; 2],  // Align to 32 bytes
}

impl Default for BootSequence {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_boot_sequence_phases() {
        let mut boot = BootSequence::new();
        assert_eq!(boot.current_phase, BootPhase::BlackVoid);

        // Advance through black void
        boot.update(1.6);
        assert_eq!(boot.current_phase, BootPhase::SmokeEmergence);

        // Advance through smoke
        boot.update(3.1);
        assert_eq!(boot.current_phase, BootPhase::OrbRising);
    }

    #[test]
    fn test_dialogue_correct_response() {
        let mut boot = BootSequence::new();

        // Fast forward to dialogue
        boot.current_phase = BootPhase::Dialogue;
        boot.dialogue_state.awaiting_user_input = true;

        boot.handle_user_input("The pleasure is all mine.".to_string());
        boot.update(0.01);

        assert_eq!(boot.current_phase, BootPhase::Explosion);
    }

    #[test]
    fn test_dialogue_incorrect_response() {
        let mut boot = BootSequence::new();
        boot.current_phase = BootPhase::Dialogue;

        boot.handle_user_input("Hello there".to_string());
        boot.update(0.01);

        // Should stay in dialogue
        assert_eq!(boot.current_phase, BootPhase::Dialogue);
    }
}
