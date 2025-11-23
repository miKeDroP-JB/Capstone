//! 0RB_AETHER Brain Orchestrator
//!
//! Core service providing intent parsing, routing, confidence scoring,
//! and security gating for the 0RB system.

mod intent;
mod store;
mod api;
mod web3;

use std::path::PathBuf;
use std::sync::Arc;
use tokio::net::UnixListener;
use tokio::sync::RwLock;
use tracing::{info, error, Level};
use tracing_subscriber::FmtSubscriber;

use crate::store::SecureStore;
use crate::api::handle_connection;

/// Brain state shared across connections
pub struct BrainState {
    pub store: SecureStore,
    pub confidence_threshold: f64,
    pub network_allowed: bool,
    pub emergency_triggered: bool,
}

impl BrainState {
    pub fn new(db_path: &str, db_key: &str) -> anyhow::Result<Self> {
        Ok(Self {
            store: SecureStore::new(db_path, db_key)?,
            confidence_threshold: 0.95,
            network_allowed: false,
            emergency_triggered: false,
        })
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize logging
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    info!("Starting 0RB Brain Orchestrator v{}", env!("CARGO_PKG_VERSION"));

    // Configuration
    let socket_path = std::env::var("ORB_SOCKET")
        .unwrap_or_else(|_| "/run/0rb/brain.sock".to_string());
    let db_path = std::env::var("ORB_DB")
        .unwrap_or_else(|_| "/run/0rb/brain.db".to_string());
    let db_key = std::env::var("ORB_DB_KEY")
        .unwrap_or_else(|_| "default-dev-key-change-in-production".to_string());

    // Ensure socket directory exists
    if let Some(parent) = PathBuf::from(&socket_path).parent() {
        std::fs::create_dir_all(parent)?;
    }

    // Remove stale socket
    let _ = std::fs::remove_file(&socket_path);

    // Initialize state
    let state = Arc::new(RwLock::new(BrainState::new(&db_path, &db_key)?));

    // Bind Unix socket
    let listener = UnixListener::bind(&socket_path)?;
    info!("Listening on {}", socket_path);

    // Set socket permissions
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&socket_path, std::fs::Permissions::from_mode(0o600))?;
    }

    // Signal handler for graceful shutdown
    let state_clone = state.clone();
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.ok();
        info!("Shutdown signal received");
        let mut s = state_clone.write().await;
        s.emergency_triggered = true;
    });

    // Accept connections
    loop {
        match listener.accept().await {
            Ok((stream, _addr)) => {
                let state = state.clone();
                tokio::spawn(async move {
                    if let Err(e) = handle_connection(stream, state).await {
                        error!("Connection error: {}", e);
                    }
                });
            }
            Err(e) => {
                error!("Accept error: {}", e);
            }
        }

        // Check for emergency
        if state.read().await.emergency_triggered {
            info!("Emergency shutdown initiated");
            break;
        }
    }

    info!("Brain shutdown complete");
    Ok(())
}
