//! Voice Control Module
//!
//! Voice-native command system for 0RB OS using Whisper for ASR

use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use std::io::Write;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VoiceCommand {
    // System commands
    Shutdown,
    Restart,
    LockScreen,
    Emergency,

    // Container navigation
    OpenContainer(String),  // e.g., "Open CREATE"
    CloseContainer,
    SwitchContainer(String),

    // Analytics
    ShowDashboard,
    ShowMetrics,
    ShowAgentPerformance,

    // Override commands
    Override(String),  // Raw command override
    Explain(String),   // Ask for explanation

    // Agent swarm
    InvokeAgent(String),
    StartTournament(String),
    StartDiscussion(String),

    Unknown,
}

pub struct VoiceController {
    whisper_model_path: String,
    listening: bool,
    last_command: Option<VoiceCommand>,
}

impl VoiceController {
    pub fn new(whisper_model_path: String) -> Self {
        Self {
            whisper_model_path,
            listening: false,
            last_command: None,
        }
    }

    /// Start listening for voice commands
    pub fn start_listening(&mut self) -> anyhow::Result<()> {
        self.listening = true;
        Ok(())
    }

    /// Stop listening
    pub fn stop_listening(&mut self) {
        self.listening = false;
    }

    /// Process audio input and return voice command
    pub fn process_audio(&mut self, audio_data: &[u8]) -> antml::Result<VoiceCommand> {
        // Save audio to temp file
        let temp_audio = "/tmp/orb_voice_input.wav";
        std::fs::write(temp_audio, audio_data)?;

        // Run Whisper ASR
        let transcript = self.run_whisper(temp_audio)?;

        // Parse transcript into command
        let command = self.parse_command(&transcript);

        self.last_command = Some(command.clone());

        Ok(command)
    }

    fn run_whisper(&self, audio_path: &str) -> antml::Result<String> {
        // Run whisper.cpp
        let output = Command::new("whisper")
            .arg("--model")
            .arg(&self.whisper_model_path)
            .arg("--file")
            .arg(audio_path)
            .arg("--output-txt")
            .output()?;

        if !output.status.success() {
            anyhow::bail!("Whisper failed: {}", String::from_utf8_lossy(&output.stderr));
        }

        let transcript = String::from_utf8(output.stdout)?;
        Ok(transcript.trim().to_string())
    }

    fn parse_command(&self, transcript: &str) -> VoiceCommand {
        let lower = transcript.to_lowercase();

        // System commands
        if lower.contains("shutdown") || lower.contains("power off") {
            return VoiceCommand::Shutdown;
        }
        if lower.contains("restart") || lower.contains("reboot") {
            return VoiceCommand::Restart;
        }
        if lower.contains("lock") {
            return VoiceCommand::LockScreen;
        }
        if lower.contains("emergency") || lower.contains("panic") {
            return VoiceCommand::Emergency;
        }

        // Container commands
        if lower.contains("open") {
            if lower.contains("work") {
                return VoiceCommand::OpenContainer("WORK".to_string());
            } else if lower.contains("play") {
                return VoiceCommand::OpenContainer("PLAY".to_string());
            } else if lower.contains("create") {
                return VoiceCommand::OpenContainer("CREATE".to_string());
            } else if lower.contains("home") {
                return VoiceCommand::OpenContainer("HOME".to_string());
            } else if lower.contains("family") {
                return VoiceCommand::OpenContainer("FAMILY".to_string());
            } else if lower.contains("health") {
                return VoiceCommand::OpenContainer("HEALTH".to_string());
            } else if lower.contains("spiritual") {
                return VoiceCommand::OpenContainer("SPIRITUAL".to_string());
            }
        }

        if lower.contains("close container") {
            return VoiceCommand::CloseContainer;
        }

        // Analytics
        if lower.contains("show dashboard") {
            return VoiceCommand::ShowDashboard;
        }
        if lower.contains("show metrics") {
            return VoiceCommand::ShowMetrics;
        }
        if lower.contains("agent performance") {
            return VoiceCommand::ShowAgentPerformance;
        }

        // Agent swarm commands
        if lower.contains("invoke") || lower.contains("ask") {
            // Extract the request
            let request = transcript.trim().to_string();
            return VoiceCommand::InvokeAgent(request);
        }

        if lower.contains("tournament") {
            let request = transcript.trim().to_string();
            return VoiceCommand::StartTournament(request);
        }

        if lower.contains("discuss") || lower.contains("discussion") {
            let request = transcript.trim().to_string();
            return VoiceCommand::StartDiscussion(request);
        }

        // Override
        if lower.contains("override") {
            let command = transcript.replace("override", "").trim().to_string();
            return VoiceCommand::Override(command);
        }

        // Explain
        if lower.contains("explain") || lower.contains("what is") {
            return VoiceCommand::Explain(transcript.to_string());
        }

        VoiceCommand::Unknown
    }

    /// Execute a voice command
    pub async fn execute_command(
        &self,
        command: VoiceCommand,
        brain_state: &crate::BrainState,
    ) -> anyhow::Result<String> {
        match command {
            VoiceCommand::Shutdown => {
                // Trigger graceful shutdown
                Ok("Initiating shutdown sequence...".to_string())
            }

            VoiceCommand::Restart => {
                Ok("Initiating restart...".to_string())
            }

            VoiceCommand::LockScreen => {
                Ok("Locking screen...".to_string())
            }

            VoiceCommand::Emergency => {
                // Trigger emergency protocols
                Ok("EMERGENCY MODE ACTIVATED - Initiating secure wipe...".to_string())
            }

            VoiceCommand::OpenContainer(name) => {
                Ok(format!("Opening {} container...", name))
            }

            VoiceCommand::CloseContainer => {
                Ok("Closing current container...".to_string())
            }

            VoiceCommand::SwitchContainer(name) => {
                Ok(format!("Switching to {} container...", name))
            }

            VoiceCommand::ShowDashboard => {
                Ok("Displaying analytics dashboard...".to_string())
            }

            VoiceCommand::ShowMetrics => {
                // Fetch metrics from brain state
                Ok(format!("System metrics: Confidence threshold: {}", brain_state.confidence_threshold))
            }

            VoiceCommand::ShowAgentPerformance => {
                Ok("Displaying agent performance data...".to_string())
            }

            VoiceCommand::InvokeAgent(request) => {
                Ok(format!("Invoking agent with request: {}", request))
            }

            VoiceCommand::StartTournament(task) => {
                Ok(format!("Starting agent tournament for: {}", task))
            }

            VoiceCommand::StartDiscussion(task) => {
                Ok(format!("Starting agent discussion for: {}", task))
            }

            VoiceCommand::Override(cmd) => {
                Ok(format!("Executing override command: {}", cmd))
            }

            VoiceCommand::Explain(query) => {
                Ok(format!("Explanation requested for: {}", query))
            }

            VoiceCommand::Unknown => {
                Ok("Command not recognized. Please try again.".to_string())
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_shutdown() {
        let vc = VoiceController::new("model.bin".to_string());
        let cmd = vc.parse_command("Please shutdown the system");
        assert!(matches!(cmd, VoiceCommand::Shutdown));
    }

    #[test]
    fn test_parse_open_container() {
        let vc = VoiceController::new("model.bin".to_string());
        let cmd = vc.parse_command("Open CREATE container");
        assert!(matches!(cmd, VoiceCommand::OpenContainer(ref name) if name == "CREATE"));
    }

    #[test]
    fn test_parse_emergency() {
        let vc = VoiceController::new("model.bin".to_string());
        let cmd = vc.parse_command("Emergency shutdown now");
        assert!(matches!(cmd, VoiceCommand::Emergency));
    }

    #[test]
    fn test_parse_unknown() {
        let vc = VoiceController::new("model.bin".to_string());
        let cmd = vc.parse_command("Random gibberish xyz 123");
        assert!(matches!(cmd, VoiceCommand::Unknown));
    }
}
