//! Ethereum wallet implementation

use anyhow::{Result, Context};
use ethers::signers::{LocalWallet, Signer};
use ethers::core::k256::ecdsa::SigningKey;
use bip39::Mnemonic;
use hdpath::StandardHDPath;

pub struct EthereumWallet {
    wallet: LocalWallet,
}

impl EthereumWallet {
    /// Create from mnemonic with derivation path
    pub fn from_mnemonic(mnemonic: &str, index: u32) -> Result<Self> {
        let mnemonic = Mnemonic::parse(mnemonic)
            .context("Invalid mnemonic")?;

        // m/44'/60'/0'/0/{index} - Standard Ethereum derivation
        let path = format!("m/44'/60'/0'/0/{}", index);
        let wallet = LocalWallet::from_phrase(&mnemonic.to_string(), Some(&path))?;

        Ok(Self { wallet })
    }

    /// Get address as hex string
    pub fn address(&self) -> String {
        format!("{:?}", self.wallet.address())
    }

    /// Sign message
    pub async fn sign_message(&self, message: &[u8]) -> Result<Vec<u8>> {
        let signature = self.wallet.sign_message(message).await?;
        Ok(signature.to_vec())
    }

    /// Get private key (use carefully!)
    pub fn private_key(&self) -> String {
        hex::encode(self.wallet.signer().to_bytes())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const TEST_MNEMONIC: &str = "test test test test test test test test test test test junk";

    #[test]
    fn test_eth_wallet_derivation() {
        let wallet = EthereumWallet::from_mnemonic(TEST_MNEMONIC, 0).unwrap();
        let addr = wallet.address();
        assert!(addr.starts_with("0x"));
        assert_eq!(addr.len(), 42); // 0x + 40 hex chars
    }

    #[test]
    fn test_deterministic_derivation() {
        let wallet1 = EthereumWallet::from_mnemonic(TEST_MNEMONIC, 0).unwrap();
        let wallet2 = EthereumWallet::from_mnemonic(TEST_MNEMONIC, 0).unwrap();
        assert_eq!(wallet1.address(), wallet2.address());
    }

    #[test]
    fn test_different_indices() {
        let wallet0 = EthereumWallet::from_mnemonic(TEST_MNEMONIC, 0).unwrap();
        let wallet1 = EthereumWallet::from_mnemonic(TEST_MNEMONIC, 1).unwrap();
        assert_ne!(wallet0.address(), wallet1.address());
    }
}
