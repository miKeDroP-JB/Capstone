//! Common types for wallet operations

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub from: String,
    pub to: String,
    pub amount: String,
    pub chain: super::Chain,
    pub status: TxStatus,
    pub hash: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TxStatus {
    Pending,
    Confirmed,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Balance {
    pub chain: super::Chain,
    pub native_balance: String,
    pub tokens: Vec<TokenBalance>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenBalance {
    pub symbol: String,
    pub contract_address: String,
    pub balance: String,
    pub decimals: u8,
}
