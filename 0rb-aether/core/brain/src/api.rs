//! JSON-RPC API handler for Brain service

use std::sync::Arc;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::UnixStream;
use tokio::sync::RwLock;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use tracing::{info, warn};

use crate::BrainState;
use crate::intent::{Intent, IntentParser, IntentCategory};

#[derive(Debug, Deserialize)]
struct RpcRequest {
    jsonrpc: String,
    method: String,
    params: Option<serde_json::Value>,
    id: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct RpcResponse {
    jsonrpc: String,
    result: Option<serde_json::Value>,
    error: Option<RpcError>,
    id: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct RpcError {
    code: i32,
    message: String,
}

#[derive(Debug, Serialize)]
struct ParseIntentResult {
    intent_id: String,
    category: String,
    action: String,
    confidence: f64,
    requires_confirmation: bool,
    metadata: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct AuthorizeResult {
    authorized: bool,
    reason: String,
    audit_id: String,
}

#[derive(Debug, Serialize)]
struct RouteTaskResult {
    task_id: String,
    routed_to: String,
    status: String,
}

#[derive(Debug, Serialize)]
struct StatusResult {
    version: String,
    uptime_secs: u64,
    confidence_threshold: f64,
    network_allowed: bool,
    pending_tasks: u32,
}

pub async fn handle_connection(
    stream: UnixStream,
    state: Arc<RwLock<BrainState>>,
) -> anyhow::Result<()> {
    let (reader, mut writer) = stream.into_split();
    let mut reader = BufReader::new(reader);
    let mut line = String::new();

    while reader.read_line(&mut line).await? > 0 {
        let response = process_request(&line, &state).await;
        let response_json = serde_json::to_string(&response)? + "\n";
        writer.write_all(response_json.as_bytes()).await?;
        line.clear();
    }

    Ok(())
}

async fn process_request(
    request_str: &str,
    state: &Arc<RwLock<BrainState>>,
) -> RpcResponse {
    let request: RpcRequest = match serde_json::from_str(request_str) {
        Ok(r) => r,
        Err(e) => {
            return RpcResponse {
                jsonrpc: "2.0".to_string(),
                result: None,
                error: Some(RpcError {
                    code: -32700,
                    message: format!("Parse error: {}", e),
                }),
                id: serde_json::Value::Null,
            };
        }
    };

    let result = match request.method.as_str() {
        "parse_intent" => handle_parse_intent(request.params, state).await,
        "authorize" => handle_authorize(request.params, state).await,
        "route_task" => handle_route_task(request.params, state).await,
        "get_status" => handle_get_status(state).await,
        "set_threshold" => handle_set_threshold(request.params, state).await,
        "emergency_wipe" => handle_emergency_wipe(state).await,
        "get_analytics" => handle_get_analytics(state).await,
        _ => Err(RpcError {
            code: -32601,
            message: "Method not found".to_string(),
        }),
    };

    match result {
        Ok(value) => RpcResponse {
            jsonrpc: "2.0".to_string(),
            result: Some(value),
            error: None,
            id: request.id,
        },
        Err(error) => RpcResponse {
            jsonrpc: "2.0".to_string(),
            result: None,
            error: Some(error),
            id: request.id,
        },
    }
}

async fn handle_parse_intent(
    params: Option<serde_json::Value>,
    state: &Arc<RwLock<BrainState>>,
) -> Result<serde_json::Value, RpcError> {
    let params = params.ok_or(RpcError {
        code: -32602,
        message: "Missing params".to_string(),
    })?;

    let text = params.get("text")
        .and_then(|v| v.as_str())
        .ok_or(RpcError {
            code: -32602,
            message: "Missing 'text' parameter".to_string(),
        })?;

    let parser = IntentParser::new();
    let intent = parser.parse(text);
    let state = state.read().await;
    let requires_confirmation = intent.confidence < state.confidence_threshold;

    // Log to store
    if let Err(e) = state.store.log_intent(&intent) {
        warn!("Failed to log intent: {}", e);
    }

    let result = ParseIntentResult {
        intent_id: intent.id.to_string(),
        category: format!("{:?}", intent.category),
        action: intent.action,
        confidence: intent.confidence,
        requires_confirmation,
        metadata: intent.metadata,
    };

    Ok(serde_json::to_value(result).unwrap())
}

async fn handle_authorize(
    params: Option<serde_json::Value>,
    state: &Arc<RwLock<BrainState>>,
) -> Result<serde_json::Value, RpcError> {
    let params = params.ok_or(RpcError {
        code: -32602,
        message: "Missing params".to_string(),
    })?;

    let intent_id = params.get("intent_id")
        .and_then(|v| v.as_str())
        .ok_or(RpcError {
            code: -32602,
            message: "Missing 'intent_id' parameter".to_string(),
        })?;

    let user_confirmed = params.get("confirmed")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);

    let audit_id = Uuid::new_v4().to_string();
    let state = state.read().await;

    // Check if network is required and allowed
    let authorized = user_confirmed;
    let reason = if authorized {
        "User confirmed".to_string()
    } else {
        "Awaiting user confirmation".to_string()
    };

    info!("Authorization for {}: {} (audit: {})", intent_id, authorized, audit_id);

    let result = AuthorizeResult {
        authorized,
        reason,
        audit_id,
    };

    Ok(serde_json::to_value(result).unwrap())
}

async fn handle_route_task(
    params: Option<serde_json::Value>,
    state: &Arc<RwLock<BrainState>>,
) -> Result<serde_json::Value, RpcError> {
    let params = params.ok_or(RpcError {
        code: -32602,
        message: "Missing params".to_string(),
    })?;

    let intent_id = params.get("intent_id")
        .and_then(|v| v.as_str())
        .ok_or(RpcError {
            code: -32602,
            message: "Missing 'intent_id' parameter".to_string(),
        })?;

    let agent = params.get("agent")
        .and_then(|v| v.as_str())
        .unwrap_or("default");

    let task_id = Uuid::new_v4().to_string();
    info!("Routing task {} to agent: {}", task_id, agent);

    let result = RouteTaskResult {
        task_id,
        routed_to: agent.to_string(),
        status: "queued".to_string(),
    };

    Ok(serde_json::to_value(result).unwrap())
}

async fn handle_get_status(
    state: &Arc<RwLock<BrainState>>,
) -> Result<serde_json::Value, RpcError> {
    let state = state.read().await;

    let result = StatusResult {
        version: env!("CARGO_PKG_VERSION").to_string(),
        uptime_secs: 0, // TODO: track actual uptime
        confidence_threshold: state.confidence_threshold,
        network_allowed: state.network_allowed,
        pending_tasks: 0,
    };

    Ok(serde_json::to_value(result).unwrap())
}

async fn handle_set_threshold(
    params: Option<serde_json::Value>,
    state: &Arc<RwLock<BrainState>>,
) -> Result<serde_json::Value, RpcError> {
    let params = params.ok_or(RpcError {
        code: -32602,
        message: "Missing params".to_string(),
    })?;

    let threshold = params.get("threshold")
        .and_then(|v| v.as_f64())
        .ok_or(RpcError {
            code: -32602,
            message: "Missing 'threshold' parameter".to_string(),
        })?;

    if !(0.0..=1.0).contains(&threshold) {
        return Err(RpcError {
            code: -32602,
            message: "Threshold must be between 0.0 and 1.0".to_string(),
        });
    }

    let mut state = state.write().await;
    state.confidence_threshold = threshold;
    info!("Confidence threshold set to {}", threshold);

    Ok(serde_json::json!({"success": true, "threshold": threshold}))
}

async fn handle_emergency_wipe(
    state: &Arc<RwLock<BrainState>>,
) -> Result<serde_json::Value, RpcError> {
    warn!("EMERGENCY WIPE TRIGGERED");

    let mut state = state.write().await;
    state.emergency_triggered = true;

    // Clear sensitive data
    if let Err(e) = state.store.secure_wipe() {
        warn!("Store wipe error: {}", e);
    }

    Ok(serde_json::json!({"status": "wipe_initiated"}))
}

async fn handle_get_analytics(
    state: &Arc<RwLock<BrainState>>,
) -> Result<serde_json::Value, RpcError> {
    let state = state.read().await;

    let stats = state.store.get_stats().unwrap_or_default();

    Ok(serde_json::json!({
        "total_intents": stats.total_intents,
        "authorized_count": stats.authorized_count,
        "rejected_count": stats.rejected_count,
    }))
}
