//! Intent parsing and classification

use serde::{Deserialize, Serialize};
use uuid::Uuid;
use regex::Regex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IntentCategory {
    System,      // OS-level operations
    Network,     // Network access requests
    Agent,       // AI agent invocation
    Developer,   // Dev tool operations
    Security,    // Security-related
    Query,       // Information queries
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Intent {
    pub id: Uuid,
    pub category: IntentCategory,
    pub action: String,
    pub confidence: f64,
    pub raw_text: String,
    pub metadata: serde_json::Value,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

pub struct IntentParser {
    patterns: Vec<(Regex, IntentCategory, &'static str, f64)>,
}

impl IntentParser {
    pub fn new() -> Self {
        let patterns = vec![
            // System operations
            (Regex::new(r"(?i)(shutdown|reboot|restart|power off)").unwrap(),
             IntentCategory::System, "system_power", 0.9),
            (Regex::new(r"(?i)(mount|unmount|disk|storage)").unwrap(),
             IntentCategory::System, "storage_op", 0.85),

            // Network operations
            (Regex::new(r"(?i)(connect|network|internet|online|fetch|download)").unwrap(),
             IntentCategory::Network, "network_access", 0.85),
            (Regex::new(r"(?i)(api|request|http|https|web)").unwrap(),
             IntentCategory::Network, "web_request", 0.8),

            // Agent operations
            (Regex::new(r"(?i)(ask|tell|chat|converse|claude|gpt|opus)").unwrap(),
             IntentCategory::Agent, "agent_invoke", 0.9),
            (Regex::new(r"(?i)(generate|create|write|compose|draft)").unwrap(),
             IntentCategory::Agent, "content_gen", 0.85),

            // Developer operations
            (Regex::new(r"(?i)(code|compile|build|test|debug|run)").unwrap(),
             IntentCategory::Developer, "dev_action", 0.9),
            (Regex::new(r"(?i)(git|commit|push|pull|branch)").unwrap(),
             IntentCategory::Developer, "vcs_action", 0.95),

            // Security operations
            (Regex::new(r"(?i)(encrypt|decrypt|secure|lock|unlock)").unwrap(),
             IntentCategory::Security, "security_op", 0.9),
            (Regex::new(r"(?i)(wipe|clear|delete|destroy|erase)").unwrap(),
             IntentCategory::Security, "data_destruction", 0.95),

            // Queries
            (Regex::new(r"(?i)(what|where|when|how|why|who|which|show|display|list)").unwrap(),
             IntentCategory::Query, "information_query", 0.7),
        ];

        Self { patterns }
    }

    pub fn parse(&self, text: &str) -> Intent {
        let mut best_match: Option<(IntentCategory, &str, f64)> = None;

        for (regex, category, action, base_confidence) in &self.patterns {
            if regex.is_match(text) {
                let confidence = self.calculate_confidence(text, regex, *base_confidence);
                if best_match.is_none() || confidence > best_match.as_ref().unwrap().2 {
                    best_match = Some((category.clone(), *action, confidence));
                }
            }
        }

        let (category, action, confidence) = best_match.unwrap_or((
            IntentCategory::Unknown,
            "unknown",
            0.3,
        ));

        Intent {
            id: Uuid::new_v4(),
            category,
            action: action.to_string(),
            confidence,
            raw_text: text.to_string(),
            metadata: serde_json::json!({
                "word_count": text.split_whitespace().count(),
                "char_count": text.len(),
            }),
            timestamp: chrono::Utc::now(),
        }
    }

    fn calculate_confidence(&self, text: &str, regex: &Regex, base: f64) -> f64 {
        // Adjust confidence based on text quality
        let word_count = text.split_whitespace().count();
        let match_count = regex.find_iter(text).count();

        let length_factor = if word_count > 3 { 1.0 } else { 0.9 };
        let match_factor = 1.0 + (match_count as f64 - 1.0) * 0.05;

        (base * length_factor * match_factor).min(0.99)
    }
}

impl Default for IntentParser {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_network_intent() {
        let parser = IntentParser::new();
        let intent = parser.parse("connect to the internet");
        assert!(matches!(intent.category, IntentCategory::Network));
        assert!(intent.confidence > 0.8);
    }

    #[test]
    fn test_parse_security_intent() {
        let parser = IntentParser::new();
        let intent = parser.parse("wipe all data immediately");
        assert!(matches!(intent.category, IntentCategory::Security));
        assert_eq!(intent.action, "data_destruction");
    }

    #[test]
    fn test_parse_unknown() {
        let parser = IntentParser::new();
        let intent = parser.parse("xyz abc 123");
        assert!(matches!(intent.category, IntentCategory::Unknown));
    }
}
