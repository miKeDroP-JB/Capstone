//! Web3 integration module for Brain orchestrator
//! Routes crypto/NFT/gaming intents to appropriate handlers

use serde::{Deserialize, Serialize};
use anyhow::Result;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Web3Intent {
    // Wallet operations
    CreateWallet { password: String },
    GetBalance { chain: String },
    SendPayment { to: String, amount: String, chain: String },

    // NFT operations
    MintNFT { uri: String, nft_type: String, royalty_fee: u32 },
    TransferNFT { token_id: u64, to: String },
    GetMyNFTs,

    // Payment operations
    CreateSplit { recipients: Vec<String>, shares: Vec<u32> },
    SendToSplit { split_id: u64, amount: String },
    CreateStream { to: String, amount: String, duration: u64 },
    CreateEscrow { to: String, amount: String, release_time: u64 },

    // Gaming operations
    PlayDice { bet: String, target: u32 },
    PlayCoinFlip { bet: String, prediction: bool },
    PlaySlots { bet: String },

    // Creator tokens
    LaunchCreatorToken { name: String, symbol: String },
    BuyCreatorTokens { token_address: String, eth_amount: String },
    SellCreatorTokens { token_address: String, token_amount: String },
    Subscribe { token_address: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Web3Response {
    pub success: bool,
    pub message: String,
    pub data: Option<serde_json::Value>,
    pub tx_hash: Option<String>,
}

/// Parse Web3-related intents from user input
pub fn parse_web3_intent(text: &str) -> Option<Web3Intent> {
    let text = text.to_lowercase();

    // Wallet operations
    if text.contains("create wallet") || text.contains("new wallet") {
        return Some(Web3Intent::CreateWallet {
            password: "".to_string(), // Will be prompted
        });
    }

    if text.contains("balance") || text.contains("how much") {
        let chain = extract_chain(&text).unwrap_or("ethereum".to_string());
        return Some(Web3Intent::GetBalance { chain });
    }

    if text.contains("send") && (text.contains("eth") || text.contains("matic")) {
        // Extract to address and amount (simplified)
        return Some(Web3Intent::SendPayment {
            to: "".to_string(),
            amount: "".to_string(),
            chain: extract_chain(&text).unwrap_or("ethereum".to_string()),
        });
    }

    // NFT operations
    if text.contains("mint nft") || text.contains("create nft") {
        let nft_type = if text.contains("music") {
            "music"
        } else if text.contains("art") {
            "art"
        } else {
            "content"
        };

        return Some(Web3Intent::MintNFT {
            uri: "".to_string(),
            nft_type: nft_type.to_string(),
            royalty_fee: 500, // 5% default
        });
    }

    if text.contains("my nfts") || text.contains("show nfts") {
        return Some(Web3Intent::GetMyNFTs);
    }

    // Gaming
    if text.contains("play dice") || text.contains("roll dice") {
        return Some(Web3Intent::PlayDice {
            bet: "0.01".to_string(),
            target: 50,
        });
    }

    if text.contains("flip coin") || text.contains("coin flip") {
        return Some(Web3Intent::PlayCoinFlip {
            bet: "0.01".to_string(),
            prediction: text.contains("heads"),
        });
    }

    if text.contains("play slots") || text.contains("slot machine") {
        return Some(Web3Intent::PlaySlots {
            bet: "0.01".to_string(),
        });
    }

    // Creator tokens
    if text.contains("launch token") || text.contains("create token") {
        return Some(Web3Intent::LaunchCreatorToken {
            name: "".to_string(),
            symbol: "".to_string(),
        });
    }

    if text.contains("buy") && text.contains("token") {
        return Some(Web3Intent::BuyCreatorTokens {
            token_address: "".to_string(),
            eth_amount: "0.1".to_string(),
        });
    }

    None
}

fn extract_chain(text: &str) -> Option<String> {
    if text.contains("polygon") || text.contains("matic") {
        Some("polygon".to_string())
    } else if text.contains("arbitrum") {
        Some("arbitrum".to_string())
    } else if text.contains("base") {
        Some("base".to_string())
    } else if text.contains("solana") || text.contains("sol") {
        Some("solana".to_string())
    } else if text.contains("ethereum") || text.contains("eth") {
        Some("ethereum".to_string())
    } else {
        None
    }
}

/// Execute Web3 intent (stub - integrate with actual wallet/contracts)
pub async fn execute_web3_intent(intent: Web3Intent) -> Result<Web3Response> {
    match intent {
        Web3Intent::CreateWallet { password } => {
            // Integrate with orb-wallet crate
            Ok(Web3Response {
                success: true,
                message: "Wallet created successfully".to_string(),
                data: Some(serde_json::json!({
                    "address": "0x1234...5678",
                    "mnemonic": "[ENCRYPTED]"
                })),
                tx_hash: None,
            })
        }

        Web3Intent::GetBalance { chain } => {
            Ok(Web3Response {
                success: true,
                message: format!("Balance on {}", chain),
                data: Some(serde_json::json!({
                    "native": "1.5 ETH",
                    "tokens": []
                })),
                tx_hash: None,
            })
        }

        Web3Intent::PlayDice { bet, target } => {
            Ok(Web3Response {
                success: true,
                message: format!("Dice game started: bet {} ETH, target {}", bet, target),
                data: Some(serde_json::json!({
                    "game_id": 123,
                    "status": "pending"
                })),
                tx_hash: Some("0xabcd...".to_string()),
            })
        }

        Web3Intent::MintNFT { uri, nft_type, royalty_fee } => {
            Ok(Web3Response {
                success: true,
                message: format!("NFT minted: {}", nft_type),
                data: Some(serde_json::json!({
                    "token_id": 1,
                    "contract": "0x...",
                    "uri": uri,
                    "royalty": royalty_fee
                })),
                tx_hash: Some("0x1234...".to_string()),
            })
        }

        _ => {
            Ok(Web3Response {
                success: false,
                message: "Not implemented yet".to_string(),
                data: None,
                tx_hash: None,
            })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_wallet_intent() {
        let intent = parse_web3_intent("create wallet");
        assert!(matches!(intent, Some(Web3Intent::CreateWallet { .. })));
    }

    #[test]
    fn test_parse_nft_intent() {
        let intent = parse_web3_intent("mint music nft");
        assert!(matches!(intent, Some(Web3Intent::MintNFT { .. })));
    }

    #[test]
    fn test_parse_gaming_intent() {
        let intent = parse_web3_intent("play dice");
        assert!(matches!(intent, Some(Web3Intent::PlayDice { .. })));
    }

    #[test]
    fn test_chain_extraction() {
        assert_eq!(extract_chain("send on polygon"), Some("polygon".to_string()));
        assert_eq!(extract_chain("solana balance"), Some("solana".to_string()));
    }
}
