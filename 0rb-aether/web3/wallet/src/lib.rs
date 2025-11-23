//! 0RB_AETHER Multi-Chain Wallet
//! Supports Ethereum, Polygon, Solana, and other EVM chains

pub mod ethereum;
pub mod solana;
pub mod keystore;
pub mod types;

use anyhow::Result;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Chain {
    Ethereum,
    Polygon,
    Arbitrum,
    Base,
    Optimism,
    Solana,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Wallet {
    pub name: String,
    pub addresses: std::collections::HashMap<Chain, String>,
    encrypted_keys: Vec<u8>,
}

impl Wallet {
    /// Create new wallet from mnemonic
    pub fn from_mnemonic(name: String, mnemonic: &str, password: &str) -> Result<Self> {
        let mut addresses = std::collections::HashMap::new();

        // Derive Ethereum address
        let eth_wallet = ethereum::EthereumWallet::from_mnemonic(mnemonic, 0)?;
        addresses.insert(Chain::Ethereum, eth_wallet.address());
        addresses.insert(Chain::Polygon, eth_wallet.address());
        addresses.insert(Chain::Arbitrum, eth_wallet.address());
        addresses.insert(Chain::Base, eth_wallet.address());
        addresses.insert(Chain::Optimism, eth_wallet.address());

        // Derive Solana address
        let sol_wallet = solana::SolanaWallet::from_mnemonic(mnemonic, 0)?;
        addresses.insert(Chain::Solana, sol_wallet.address());

        // Encrypt keys
        let encrypted_keys = keystore::encrypt_mnemonic(mnemonic, password)?;

        Ok(Self {
            name,
            addresses,
            encrypted_keys,
        })
    }

    /// Generate new random wallet
    pub fn generate(name: String, password: &str) -> Result<(Self, String)> {
        use bip39::{Mnemonic, Language};

        let mnemonic = Mnemonic::generate(24)?;
        let phrase = mnemonic.to_string();
        let wallet = Self::from_mnemonic(name, &phrase, password)?;

        Ok((wallet, phrase))
    }

    /// Get address for specific chain
    pub fn get_address(&self, chain: &Chain) -> Option<&String> {
        self.addresses.get(chain)
    }

    /// Unlock wallet with password
    pub fn unlock(&self, password: &str) -> Result<String> {
        keystore::decrypt_mnemonic(&self.encrypted_keys, password)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wallet_generation() {
        let (wallet, mnemonic) = Wallet::generate("test".to_string(), "password123").unwrap();
        assert_eq!(wallet.name, "test");
        assert!(wallet.addresses.contains_key(&Chain::Ethereum));
        assert!(wallet.addresses.contains_key(&Chain::Solana));
        assert!(mnemonic.split_whitespace().count() == 24);
    }

    #[test]
    fn test_wallet_unlock() {
        let (wallet, mnemonic) = Wallet::generate("test".to_string(), "password123").unwrap();
        let unlocked = wallet.unlock("password123").unwrap();
        assert_eq!(unlocked, mnemonic);
    }
}
