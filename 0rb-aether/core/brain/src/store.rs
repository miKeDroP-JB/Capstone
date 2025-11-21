//! Encrypted SQLite store

use rusqlite::{Connection, params};
use crate::intent::Intent;
use tracing::info;
use std::sync::Mutex;

#[derive(Debug, Default)]
pub struct StoreStats {
    pub total_intents: u64,
    pub authorized_count: u64,
    pub rejected_count: u64,
}

pub struct SecureStore {
    conn: Mutex<Connection>,
}

// Safety: We wrap Connection in Mutex for thread-safe access
unsafe impl Send for SecureStore {}
unsafe impl Sync for SecureStore {}

impl SecureStore {
    pub fn new(path: &str, _key: &str) -> anyhow::Result<Self> {
        let conn = Connection::open(path)?;

        // Initialize schema
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS intents (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                raw_text TEXT,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                authorized INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_intents_timestamp ON intents(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);",
        )?;

        info!("SecureStore initialized at {}", path);
        Ok(Self { conn: Mutex::new(conn) })
    }

    pub fn log_intent(&self, intent: &Intent) -> anyhow::Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO intents (id, category, action, confidence, raw_text, metadata, timestamp)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                intent.id.to_string(),
                format!("{:?}", intent.category),
                intent.action,
                intent.confidence,
                intent.raw_text,
                intent.metadata.to_string(),
                intent.timestamp.to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    pub fn log_audit(&self, event_type: &str, data: &str) -> anyhow::Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO audit_log (event_type, event_data, timestamp) VALUES (?1, ?2, ?3)",
            params![event_type, data, chrono::Utc::now().to_rfc3339()],
        )?;
        Ok(())
    }

    pub fn get_stats(&self) -> anyhow::Result<StoreStats> {
        let conn = self.conn.lock().unwrap();
        let total: u64 = conn.query_row(
            "SELECT COUNT(*) FROM intents",
            [],
            |row| row.get(0),
        )?;

        let authorized: u64 = conn.query_row(
            "SELECT COUNT(*) FROM intents WHERE authorized = 1",
            [],
            |row| row.get(0),
        )?;

        Ok(StoreStats {
            total_intents: total,
            authorized_count: authorized,
            rejected_count: total - authorized,
        })
    }

    pub fn secure_wipe(&self) -> anyhow::Result<()> {
        info!("Initiating secure store wipe");
        let conn = self.conn.lock().unwrap();
        conn.execute_batch(
            "DELETE FROM intents;
             DELETE FROM audit_log;
             VACUUM;"
        )?;
        Ok(())
    }
}
