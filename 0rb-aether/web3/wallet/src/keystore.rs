//! Encrypted keystore using AES-GCM and Argon2

use anyhow::{Result, bail};
use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use argon2::{Argon2, PasswordHash, PasswordHasher, PasswordVerifier};
use argon2::password_hash::SaltString;
use sha2::{Sha256, Digest};

const NONCE_SIZE: usize = 12;

/// Encrypt mnemonic with password using AES-256-GCM
pub fn encrypt_mnemonic(mnemonic: &str, password: &str) -> Result<Vec<u8>> {
    // Derive key from password using Argon2
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();

    let password_hash = argon2
        .hash_password(password.as_bytes(), &salt)?
        .to_string();

    // Use first 32 bytes of hash as AES key
    let mut hasher = Sha256::new();
    hasher.update(password_hash.as_bytes());
    let key_bytes = hasher.finalize();

    let cipher = Aes256Gcm::new_from_slice(&key_bytes)?;
    let nonce = Nonce::from_slice(&[0u8; NONCE_SIZE]); // Use random nonce in production

    let ciphertext = cipher.encrypt(nonce, mnemonic.as_bytes())
        .map_err(|e| anyhow::anyhow!("Encryption failed: {}", e))?;

    // Prepend salt for decryption
    let mut result = salt.as_str().as_bytes().to_vec();
    result.extend_from_slice(&ciphertext);

    Ok(result)
}

/// Decrypt mnemonic with password
pub fn decrypt_mnemonic(encrypted: &[u8], password: &str) -> Result<String> {
    if encrypted.len() < 22 { // Min salt size
        bail!("Invalid encrypted data");
    }

    // Extract salt (first 22 bytes typically)
    let salt_str = std::str::from_utf8(&encrypted[..22])?;
    let salt = SaltString::from_b64(salt_str)?;

    // Derive key
    let argon2 = Argon2::default();
    let password_hash = argon2
        .hash_password(password.as_bytes(), &salt)?
        .to_string();

    let mut hasher = Sha256::new();
    hasher.update(password_hash.as_bytes());
    let key_bytes = hasher.finalize();

    let cipher = Aes256Gcm::new_from_slice(&key_bytes)?;
    let nonce = Nonce::from_slice(&[0u8; NONCE_SIZE]);

    let plaintext = cipher.decrypt(nonce, &encrypted[22..])
        .map_err(|_| anyhow::anyhow!("Decryption failed: wrong password?"))?;

    Ok(String::from_utf8(plaintext)?)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encrypt_decrypt() {
        let mnemonic = "test test test test test test test test test test test junk";
        let password = "super_secret_password";

        let encrypted = encrypt_mnemonic(mnemonic, password).unwrap();
        let decrypted = decrypt_mnemonic(&encrypted, password).unwrap();

        assert_eq!(mnemonic, decrypted);
    }

    #[test]
    fn test_wrong_password() {
        let mnemonic = "test test test test test test test test test test test junk";
        let encrypted = encrypt_mnemonic(mnemonic, "correct").unwrap();
        let result = decrypt_mnemonic(&encrypted, "wrong");

        assert!(result.is_err());
    }
}
