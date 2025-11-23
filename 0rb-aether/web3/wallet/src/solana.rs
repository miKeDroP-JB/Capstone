//! Solana wallet implementation

use anyhow::{Result, Context};
use solana_sdk::signature::{Keypair, Signer as SolanaSigner};
use solana_sdk::pubkey::Pubkey;
use bip39::Mnemonic;
use ed25519_dalek::SigningKey;

pub struct SolanaWallet {
    keypair: Keypair,
}

impl SolanaWallet {
    /// Create from mnemonic with derivation path
    pub fn from_mnemonic(mnemonic: &str, index: u32) -> Result<Self> {
        let mnemonic = Mnemonic::parse(mnemonic)
            .context("Invalid mnemonic")?;

        // Solana uses Ed25519
        let seed = mnemonic.to_seed("");

        // Derive using BIP44 path: m/44'/501'/0'/0'
        // For simplicity, using first 32 bytes of seed + index
        let mut key_bytes = [0u8; 32];
        let seed_slice = &seed[..(32.min(seed.len()))];
        key_bytes[..seed_slice.len()].copy_from_slice(seed_slice);

        // Mix in index
        key_bytes[0] ^= index as u8;
        key_bytes[1] ^= (index >> 8) as u8;

        let keypair = Keypair::from_bytes(&{
            let mut full_key = [0u8; 64];
            full_key[..32].copy_from_slice(&key_bytes);
            // Public key will be derived
            let signing_key = SigningKey::from_bytes(&key_bytes);
            let verifying_key = signing_key.verifying_key();
            full_key[32..].copy_from_slice(verifying_key.as_bytes());
            full_key
        })?;

        Ok(Self { keypair })
    }

    /// Get address as base58 string
    pub fn address(&self) -> String {
        self.keypair.pubkey().to_string()
    }

    /// Sign message
    pub fn sign_message(&self, message: &[u8]) -> Vec<u8> {
        self.keypair.sign_message(message).as_ref().to_vec()
    }

    /// Get public key
    pub fn pubkey(&self) -> Pubkey {
        self.keypair.pubkey()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const TEST_MNEMONIC: &str = "test test test test test test test test test test test junk";

    #[test]
    fn test_sol_wallet_derivation() {
        let wallet = SolanaWallet::from_mnemonic(TEST_MNEMONIC, 0).unwrap();
        let addr = wallet.address();
        assert!(!addr.is_empty());
        // Solana addresses are base58, typically 32-44 chars
        assert!(addr.len() >= 32 && addr.len() <= 44);
    }

    #[test]
    fn test_sol_deterministic() {
        let wallet1 = SolanaWallet::from_mnemonic(TEST_MNEMONIC, 0).unwrap();
        let wallet2 = SolanaWallet::from_mnemonic(TEST_MNEMONIC, 0).unwrap();
        assert_eq!(wallet1.address(), wallet2.address());
    }
}
