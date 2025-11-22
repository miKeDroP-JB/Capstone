//! AI Agent Swarm Module
//!
//! Tournament-based AI agent orchestration with discussion engines,
//! confidence scoring, and dynamic routing optimization.

use serde::{Deserialize, Serialize};
use uuid::Uuid;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AgentCapability {
    CodeGeneration,
    NaturalLanguage,
    DataAnalysis,
    ImageGeneration,
    Reasoning,
    Planning,
    Critique,
    Synthesis,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentNode {
    pub id: Uuid,
    pub name: String,
    pub provider: String,  // "anthropic", "openai", "local", etc.
    pub model: String,
    pub capabilities: Vec<AgentCapability>,
    pub strengths: Vec<String>,
    pub weaknesses: Vec<String>,
    pub confidence_score: f64,  // Historical performance metric
    pub avg_response_time_ms: u64,
    pub success_rate: f64,
    pub cost_per_1k_tokens: f64,
}

impl AgentNode {
    pub fn new(
        name: String,
        provider: String,
        model: String,
        capabilities: Vec<AgentCapability>,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            name,
            provider,
            model,
            capabilities,
            strengths: Vec::new(),
            weaknesses: Vec::new(),
            confidence_score: 0.5,  // Neutral starting point
            avg_response_time_ms: 0,
            success_rate: 0.0,
            cost_per_1k_tokens: 0.0,
        }
    }

    pub fn update_performance(&mut self, success: bool, response_time_ms: u64) {
        // Exponential moving average for success rate
        let alpha = 0.1;
        self.success_rate = alpha * (if success { 1.0 } else { 0.0 })
            + (1.0 - alpha) * self.success_rate;

        // Update confidence based on success rate
        self.confidence_score = self.success_rate;

        // Update average response time
        if self.avg_response_time_ms == 0 {
            self.avg_response_time_ms = response_time_ms;
        } else {
            self.avg_response_time_ms =
                (self.avg_response_time_ms as f64 * 0.9 + response_time_ms as f64 * 0.1) as u64;
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentResponse {
    pub agent_id: Uuid,
    pub agent_name: String,
    pub response: String,
    pub confidence: f64,
    pub reasoning: String,
    pub response_time_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TournamentResult {
    pub winner: AgentResponse,
    pub all_responses: Vec<AgentResponse>,
    pub voting_scores: HashMap<Uuid, f64>,
    pub consensus_level: f64,
}

pub struct AgentSwarm {
    pub agents: HashMap<Uuid, AgentNode>,
    pub routing_cache: HashMap<String, Uuid>,  // Task type -> Best agent
    pub tournament_history: Vec<TournamentResult>,
}

impl AgentSwarm {
    pub fn new() -> Self {
        Self {
            agents: HashMap::new(),
            routing_cache: HashMap::new(),
            tournament_history: Vec::new(),
        }
    }

    pub fn register_agent(&mut self, agent: AgentNode) {
        self.agents.insert(agent.id, agent);
    }

    /// Tournament Engine: Multiple agents propose solutions, then critique each other
    pub async fn tournament(&mut self, task: &str, task_type: &str) -> anyhow::Result<TournamentResult> {
        // Find agents capable of handling this task
        let capable_agents: Vec<&mut AgentNode> = self.agents.values_mut()
            .filter(|a| self.is_capable(a, task_type))
            .collect();

        if capable_agents.is_empty() {
            anyhow::bail!("No capable agents found for task type: {}", task_type);
        }

        // Phase 1: Collect proposals
        let mut responses = Vec::new();
        for agent in capable_agents.iter() {
            let start = std::time::Instant::now();

            // Simulate agent response (in production, this would call actual APIs)
            let response = self.invoke_agent(agent, task).await?;
            let elapsed = start.elapsed().as_millis() as u64;

            responses.push(AgentResponse {
                agent_id: agent.id,
                agent_name: agent.name.clone(),
                response: response.clone(),
                confidence: agent.confidence_score,
                reasoning: format!("Agent {} proposal", agent.name),
                response_time_ms: elapsed,
            });
        }

        // Phase 2: Critique phase - each agent critiques other solutions
        let mut voting_scores: HashMap<Uuid, f64> = HashMap::new();
        for response in &responses {
            let mut score = 0.0;

            // Each other agent votes on this response
            for other in &responses {
                if other.agent_id != response.agent_id {
                    // Simulate critique (would use actual LLM critique in production)
                    let critique_score = self.critique_response(&other.response, &response.response).await?;
                    score += critique_score;
                }
            }

            // Normalize by number of voters
            if responses.len() > 1 {
                score /= (responses.len() - 1) as f64;
            }

            voting_scores.insert(response.agent_id, score);
        }

        // Phase 3: Select winner
        let winner = responses.iter()
            .max_by(|a, b| {
                let score_a = voting_scores.get(&a.agent_id).unwrap_or(&0.0);
                let score_b = voting_scores.get(&b.agent_id).unwrap_or(&0.0);
                score_a.partial_cmp(score_b).unwrap()
            })
            .ok_or_else(|| anyhow::anyhow!("No winner found"))?
            .clone();

        // Calculate consensus level (how much agreement there was)
        let scores: Vec<f64> = voting_scores.values().cloned().collect();
        let mean = scores.iter().sum::<f64>() / scores.len() as f64;
        let variance = scores.iter().map(|s| (s - mean).powi(2)).sum::<f64>() / scores.len() as f64;
        let consensus_level = 1.0 - variance.sqrt();

        let result = TournamentResult {
            winner: winner.clone(),
            all_responses: responses.clone(),
            voting_scores: voting_scores.clone(),
            consensus_level,
        };

        // Update routing cache if consensus is high
        if consensus_level > 0.7 {
            self.routing_cache.insert(task_type.to_string(), winner.agent_id);
        }

        // Update winning agent's performance
        if let Some(agent) = self.agents.get_mut(&winner.agent_id) {
            agent.update_performance(true, winner.response_time_ms);
        }

        self.tournament_history.push(result.clone());

        Ok(result)
    }

    /// Discussion Engine: Agents debate in real-time to refine solution
    pub async fn discussion(&mut self, task: &str, max_rounds: usize) -> antml::Result<String> {
        let mut current_solution = String::new();
        let mut discussion_log = Vec::new();

        for round in 0..max_rounds {
            // Rotate through agents for diverse perspectives
            for agent in self.agents.values() {
                let context = format!(
                    "Round {}/{}\nCurrent solution: {}\nPrevious discussion: {:?}\n\nYour input:",
                    round + 1, max_rounds, current_solution, discussion_log
                );

                let response = self.invoke_agent(agent, &context).await?;
                discussion_log.push(format!("{}: {}", agent.name, response));

                // Update solution if this is an improvement
                current_solution = response;
            }

            // Check for convergence
            if round > 0 && self.has_converged(&discussion_log) {
                break;
            }
        }

        Ok(current_solution)
    }

    /// Smart routing: Use historical performance to select best agent for task type
    pub fn route_task(&self, task_type: &str) -> Option<Uuid> {
        // Check cache first
        if let Some(agent_id) = self.routing_cache.get(task_type) {
            return Some(*agent_id);
        }

        // Find best agent by historical performance
        self.agents.values()
            .filter(|a| self.is_capable(a, task_type))
            .max_by(|a, b| {
                let score_a = a.confidence_score * (1.0 - a.avg_response_time_ms as f64 / 10000.0);
                let score_b = b.confidence_score * (1.0 - b.avg_response_time_ms as f64 / 10000.0);
                score_a.partial_cmp(&score_b).unwrap()
            })
            .map(|a| a.id)
    }

    /// Sandbox check: Validate agent output before execution
    pub fn sandbox_check(&self, output: &str) -> antml::Result<bool> {
        // Check for dangerous patterns
        let dangerous_patterns = [
            "rm -rf",
            "dd if=",
            "mkfs.",
            ":(){:|:&};:",  // Fork bomb
            "wget", "curl",  // Network access
        ];

        for pattern in &dangerous_patterns {
            if output.contains(pattern) {
                return Ok(false);
            }
        }

        Ok(true)
    }

    // Private helper methods

    fn is_capable(&self, agent: &AgentNode, task_type: &str) -> bool {
        // Match task type to agent capabilities
        match task_type {
            "code" => agent.capabilities.contains(&AgentCapability::CodeGeneration),
            "text" => agent.capabilities.contains(&AgentCapability::NaturalLanguage),
            "data" => agent.capabilities.contains(&AgentCapability::DataAnalysis),
            "image" => agent.capabilities.contains(&AgentCapability::ImageGeneration),
            "reasoning" => agent.capabilities.contains(&AgentCapability::Reasoning),
            "planning" => agent.capabilities.contains(&AgentCapability::Planning),
            _ => true,  // Generic tasks available to all
        }
    }

    async fn invoke_agent(&self, agent: &AgentNode, task: &str) -> antml::Result<String> {
        // In production, this would call actual LLM APIs
        // For now, return placeholder
        Ok(format!("[{}] Response to: {}", agent.name, task))
    }

    async fn critique_response(&self, critic_response: &str, target_response: &str) -> antml::Result<f64> {
        // Simulate critique scoring
        // In production, would use LLM to critique and score
        Ok(0.8)
    }

    fn has_converged(&self, discussion_log: &[String]) -> bool {
        // Check if recent responses are similar (convergence)
        if discussion_log.len() < 4 {
            return false;
        }

        let last_two: Vec<&String> = discussion_log.iter().rev().take(2).collect();

        // Simple similarity check (in production, use semantic similarity)
        last_two[0].len().abs_diff(last_two[1].len()) < 50
    }
}

impl Default for AgentSwarm {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_agent_creation() {
        let agent = AgentNode::new(
            "Claude Opus".to_string(),
            "anthropic".to_string(),
            "claude-opus-4-20250514".to_string(),
            vec![AgentCapability::Reasoning, AgentCapability::CodeGeneration],
        );

        assert_eq!(agent.name, "Claude Opus");
        assert_eq!(agent.confidence_score, 0.5);
    }

    #[test]
    fn test_performance_update() {
        let mut agent = AgentNode::new(
            "Test Agent".to_string(),
            "test".to_string(),
            "test-model".to_string(),
            vec![AgentCapability::NaturalLanguage],
        );

        agent.update_performance(true, 1000);
        assert!(agent.success_rate > 0.0);
        assert_eq!(agent.avg_response_time_ms, 1000);
    }

    #[tokio::test]
    async fn test_swarm_routing() {
        let mut swarm = AgentSwarm::new();

        let agent = AgentNode::new(
            "Code Agent".to_string(),
            "test".to_string(),
            "test-model".to_string(),
            vec![AgentCapability::CodeGeneration],
        );

        swarm.register_agent(agent);

        let routed = swarm.route_task("code");
        assert!(routed.is_some());
    }
}
