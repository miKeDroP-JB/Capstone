# 0RB_AETHER Web3 Integration Guide

## Quick Start

### 1. Create Wallet

```bash
# Via voice
"Create a new wallet"

# Via CLI
orb-cli wallet create --password "your-secure-password"
```

Your wallet supports:
- **Ethereum** (and all EVM chains: Polygon, Arbitrum, Base, Optimism)
- **Solana**

### 2. Fund Your Wallet

Transfer crypto from an exchange or another wallet to your 0RB wallet address.

```bash
# Get your addresses
orb-cli wallet address --chain ethereum
orb-cli wallet address --chain solana
```

### 3. Deploy Contracts

```bash
cd web3/contracts
npm install
npm run compile

# Deploy to local testnet
npm run deploy:local

# Deploy to Polygon
npm run deploy:polygon
```

---

## NFT Operations

### Mint Music NFT

```bash
# Voice command
"Mint my album as NFT on Polygon"

# CLI
orb-cli nft mint \
  --uri ipfs://QmYourMetadata \
  --type music \
  --royalty 5 \
  --chain polygon
```

**Features:**
- Built-in royalties (5% default)
- Batch minting for albums/collections
- Music, art, and content types
- IPFS/Arweave metadata storage

### Batch Mint Collection

```javascript
// JavaScript example
const { mintBatch } = require('./web3/nft');

const uris = [
  'ipfs://track1',
  'ipfs://track2',
  'ipfs://track3',
];

const tokenIds = await mintBatch({
  uris,
  type: 'music',
  category: 'Album: My First Collection',
  royaltyFee: 500, // 5%
});
```

### View Your NFTs

```bash
# Voice
"Show my NFTs"

# CLI
orb-cli nft list --wallet 0xYourAddress
```

---

## Payment Systems

### 1. Payment Splits (Royalties)

Perfect for collaborations!

```bash
# Voice
"Create payment split: 50% Alice, 30% Bob, 20% Charlie"

# CLI
orb-cli payments create-split \
  --recipients 0xAlice,0xBob,0xCharlie \
  --shares 5000,3000,2000
```

Send to split:
```bash
orb-cli payments send-to-split --split-id 1 --amount 1.0
```

### 2. Streaming Payments

Per-second micropayments!

```bash
# Voice
"Stream 1 ETH to Alice over 30 days"

# CLI
orb-cli payments create-stream \
  --recipient 0xAlice \
  --amount 1.0 \
  --duration 2592000
```

Alice can withdraw vested amount anytime:
```bash
orb-cli payments withdraw-stream --stream-id 1
```

### 3. Escrow

Time-locked payments:

```bash
orb-cli payments create-escrow \
  --payee 0xContractor \
  --amount 5.0 \
  --release-time "2024-12-31 00:00:00"
```

### 4. Milestone Payments

Perfect for contracts!

```bash
orb-cli payments create-milestone \
  --payee 0xDeveloper \
  --milestones 2.0,3.0,5.0
```

Release each milestone:
```bash
orb-cli payments release-milestone --milestone-id 1
```

---

## Gaming & Gambling

### Dice Game

Roll under a target number (2-99):

```bash
# Voice
"Play dice, bet 0.1 ETH, target 50"

# CLI
orb-cli gaming dice --bet 0.1 --target 50
```

**Payout:** `bet * (100 - houseEdge) / target`

**Example:** Target 50 = 2x multiplier

### Coin Flip

```bash
# Voice
"Flip coin, bet 0.05 ETH, heads"

# CLI
orb-cli gaming coinflip --bet 0.05 --prediction heads
```

**Payout:** 2x (minus 2% house edge)

### Slots

3-reel slot machine:

```bash
# Voice
"Play slots, bet 0.1 ETH"

# CLI
orb-cli gaming slots --bet 0.1
```

**Payouts:**
- Triple 7s: 50x
- Any triple: 10x
- Any double: 2x

### Provably Fair

All games use:
1. **Seed commitment:** You provide a hash before the game
2. **Block hash randomness:** Uses future block hash
3. **Verifiable:** Anyone can verify fairness

```bash
# Generate seed
orb-cli gaming generate-seed

# Play with seed
orb-cli gaming dice --bet 0.1 --target 50 --seed-hash 0x...

# After block confirmation, resolve
orb-cli gaming resolve --game-id 123 --seed "your-secret-seed"
```

---

## Creator Tokens

Launch your personal economy!

### Launch Token

```bash
# Voice
"Launch my creator token called MikeCoin, symbol MIKE"

# CLI
orb-cli creator launch \
  --name "MikeCoin" \
  --symbol "MIKE" \
  --initial-supply 1000
```

### Bonding Curve

Automatic market making:
- **Buy price** increases with supply
- **Sell price** = buy price * 0.95 (5% fee)
- **No liquidity needed**

### Buy/Sell

```bash
# Buy tokens
orb-cli creator buy --token 0x... --eth 0.5

# Sell tokens
orb-cli creator sell --token 0x... --amount 100
```

### Subscriptions

Gate content with token holding:

```bash
# Creator sets up subscription
orb-cli creator setup-subscription \
  --token 0x... \
  --tokens-required 100 \
  --duration 2592000

# Fans subscribe
orb-cli creator subscribe --token 0x...
```

**Benefits:**
- No complex smart contracts
- Automatic price discovery
- Instant liquidity
- Creator earnings from trading fees

---

## Advanced Examples

### Music Industry Example

```bash
# 1. Mint album as NFT collection
orb-cli nft mint-batch \
  --uris track1.json,track2.json,track3.json \
  --type music \
  --category "Album: Electric Dreams"

# 2. Set up royalty split
orb-cli payments create-split \
  --recipients 0xArtist,0xProducer,0xLabel \
  --shares 5000,3000,2000

# 3. Launch creator token for fans
orb-cli creator launch --name "ArtistToken" --symbol "ART"

# 4. Gate exclusive content
orb-cli creator setup-subscription \
  --tokens-required 50 \
  --duration 2592000
```

### Gaming Tournament

```bash
# 1. Create prize pool (escrow)
orb-cli payments create-escrow \
  --payee 0xWinnerTBD \
  --amount 10.0 \
  --release-time "2024-12-01 00:00:00"

# 2. Players compete via dice
orb-cli gaming dice --bet 0.1 --target 75

# 3. Release to winner
orb-cli payments release-escrow --escrow-id 1 --new-payee 0xWinner
```

---

## Security Best Practices

### Wallet Security

1. **Backup mnemonic** securely (offline, encrypted)
2. **Use strong password** for encryption
3. **Enable 2FA** for high-value operations
4. **Test with small amounts** first

### Smart Contract Risks

1. **Audited contracts:** OpenZeppelin base contracts
2. **Test on testnets** before mainnet
3. **Start with small bets** in gaming
4. **Understand bonding curves** before launching tokens

### Recommended Limits

```bash
# Set personal limits
orb-cli config set --max-bet 0.5
orb-cli config set --daily-limit 2.0
orb-cli config set --require-confirmation true
```

---

## Voice Commands Reference

### Wallet
- "Create wallet"
- "Show my balance"
- "Send 0.5 ETH to [address]"

### NFT
- "Mint my album as NFT"
- "Mint art NFT with 10% royalty"
- "Show my NFTs"
- "Transfer NFT [id] to [address]"

### Payments
- "Send 1 ETH split between Alice and Bob 50-50"
- "Stream 2 ETH to [address] over 30 days"
- "Create escrow for [address], 5 ETH, release in 7 days"

### Gaming
- "Play dice, bet 0.1 ETH, target 60"
- "Flip coin, heads, bet 0.05 ETH"
- "Play slots, 0.1 ETH"
- "Show my game history"

### Creator Tokens
- "Launch my creator token"
- "Buy creator tokens for 0.5 ETH"
- "Sell 100 creator tokens"
- "Subscribe to [creator]"

---

## API Reference

### REST API

```bash
# Start API server
orb-api-server --port 3000
```

**Endpoints:**

```javascript
// Wallet
POST /api/wallet/create
GET  /api/wallet/balance/:address
POST /api/wallet/send

// NFT
POST /api/nft/mint
GET  /api/nft/list/:owner

// Payments
POST /api/payments/split
POST /api/payments/stream

// Gaming
POST /api/gaming/dice
GET  /api/gaming/results/:gameId

// Creator
POST /api/creator/launch
POST /api/creator/buy
```

### WebSocket

Real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:3000/ws');

ws.on('message', (data) => {
  const event = JSON.parse(data);

  if (event.type === 'game_resolved') {
    console.log('Game result:', event.data);
  }

  if (event.type === 'nft_minted') {
    console.log('NFT minted:', event.data.tokenId);
  }
});
```

---

## Troubleshooting

### "Insufficient balance"
- Check balance: `orb-cli wallet balance`
- Ensure correct chain selected
- Account for gas fees

### "Transaction reverted"
- Check gas limit
- Verify contract address
- Ensure approvals for tokens

### "Game resolution failed"
- Wait for next block after game creation
- Ensure seed matches seed hash
- Check block confirmation

### "NFT mint failed"
- Validate metadata URI (IPFS accessible)
- Check royalty fee (max 10%)
- Ensure wallet has ETH for gas

---

## Network Information

### Testnets (Free ETH/MATIC)

- **Polygon Mumbai:** https://faucet.polygon.technology
- **Base Goerli:** https://www.coinbase.com/faucets/base-ethereum-goerli-faucet
- **Arbitrum Goerli:** https://faucet.quicknode.com/arbitrum/goerli

### Mainnet Contract Addresses

*Deploy contracts first, then update here*

```
Ethereum Mainnet:
  OrbNFT: 0x...
  OrbPayments: 0x...
  OrbGaming: 0x...

Polygon:
  OrbNFT: 0x...
  OrbPayments: 0x...
  OrbGaming: 0x...
```

---

## Roadmap

- [ ] Layer 2 support (Optimism, zkSync)
- [ ] Cross-chain bridging
- [ ] NFT marketplace integration (OpenSea, Blur)
- [ ] DAO governance
- [ ] Chainlink VRF for gaming (production-grade randomness)
- [ ] Mobile wallet app
- [ ] Hardware wallet support (Ledger, Trezor)

---

## Support

- **Discord:** https://discord.gg/orbaether
- **GitHub:** https://github.com/miKeDroP-JB/Capstone
- **Docs:** https://docs.orbaether.io

**Report Bugs:** https://github.com/miKeDroP-JB/Capstone/issues
