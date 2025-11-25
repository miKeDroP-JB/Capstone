/**
 * FlowSync Economy API
 * Tokenomics, staking, and marketplace
 */

import {
    EconomyAPI,
    Wallet,
    Transaction,
    Stake,
    TokenType,
} from './flowsync.js';

// =============================================================================
// TOKEN ECONOMICS
// =============================================================================

/**
 * Token economic parameters
 */
const Tokenomics = {
    // Total supply
    TOTAL_SUPPLY: 1_000_000_000, // 1 billion ORB

    // Distribution
    DISTRIBUTION: {
        ecosystem: 0.40,      // 40% - ecosystem growth
        team: 0.15,           // 15% - team (4-year vest)
        investors: 0.15,      // 15% - investors (2-year vest)
        treasury: 0.20,       // 20% - treasury
        community: 0.10,      // 10% - community rewards
    },

    // Emission schedule (annual)
    EMISSION: {
        year1: 0.10,  // 10% of remaining supply
        year2: 0.08,
        year3: 0.06,
        year4: 0.04,
        year5_plus: 0.02,
    },

    // Fee structure
    FEES: {
        transfer: 0.001,        // 0.1%
        stake: 0.0,             // Free to stake
        unstake: 0.005,         // 0.5% early unstake penalty
        marketplace: 0.025,     // 2.5% marketplace fee
        apiCall: 0.0001,        // Per API call
        agentExecution: 0.001,  // Per agent task
        workflowRun: 0.005,     // Per workflow execution
    },

    // Staking rewards (APY)
    STAKING: {
        compute: { apy: 0.12, minStake: 100, lockPeriod: 30 },
        storage: { apy: 0.08, minStake: 50, lockPeriod: 14 },
        validator: { apy: 0.15, minStake: 10000, lockPeriod: 90 },
        governance: { apy: 0.05, minStake: 1000, lockPeriod: 180 },
    },

    // Burn mechanism
    BURN: {
        feePercentToBurn: 0.50,  // 50% of fees are burned
    },
};

// =============================================================================
// WALLET MANAGER
// =============================================================================

/**
 * Extended wallet management
 */
class WalletManager {
    constructor(economy) {
        this._economy = economy;
        this._watchers = new Map();
    }

    /**
     * Create wallet with initial funding
     */
    async createFunded(owner, initialOrb = 0) {
        const wallet = await this._economy.createWallet(owner);
        if (initialOrb > 0) {
            // Would normally come from faucet or purchase
            wallet.balances[TokenType.ORB] = initialOrb;
        }
        return wallet;
    }

    /**
     * Get wallet portfolio value
     */
    async getPortfolioValue(walletId) {
        const wallet = await this._economy.getWallet(walletId);
        if (!wallet) return null;

        let totalValue = 0;
        for (const [token, balance] of Object.entries(wallet.balances)) {
            const price = await this._economy.getPrice(token);
            totalValue += balance * price;
        }

        return {
            wallet: walletId,
            balances: wallet.balances,
            totalValue,
            valueCurrency: 'USD',
        };
    }

    /**
     * Watch wallet for changes
     */
    watch(walletId, callback) {
        this._watchers.set(walletId, callback);
        return () => this._watchers.delete(walletId);
    }

    /**
     * Notify watchers of balance change
     */
    _notifyChange(walletId, change) {
        const callback = this._watchers.get(walletId);
        if (callback) {
            callback(change);
        }
    }

    /**
     * Get transaction history
     */
    async getHistory(walletId, options = {}) {
        const { limit = 50, offset = 0, type = null } = options;
        // Would fetch from transaction store
        return [];
    }

    /**
     * Export wallet data
     */
    async export(walletId) {
        const wallet = await this._economy.getWallet(walletId);
        if (!wallet) return null;

        return {
            id: wallet.id,
            owner: wallet.owner,
            balances: wallet.balances,
            createdAt: wallet.createdAt,
            exportedAt: new Date().toISOString(),
        };
    }
}

// =============================================================================
// STAKING MANAGER
// =============================================================================

/**
 * Advanced staking management
 */
class StakingManager {
    constructor(economy) {
        this._economy = economy;
        this._pools = new Map();
    }

    /**
     * Get staking pool info
     */
    getPoolInfo(nodeType) {
        const config = Tokenomics.STAKING[nodeType];
        if (!config) return null;

        return {
            nodeType,
            apy: config.apy,
            minStake: config.minStake,
            lockPeriod: config.lockPeriod,
            totalStaked: this._getPoolTotal(nodeType),
        };
    }

    _getPoolTotal(nodeType) {
        return this._pools.get(nodeType)?.totalStaked || 0;
    }

    /**
     * Calculate potential rewards
     */
    calculateRewards(amount, nodeType, days) {
        const config = Tokenomics.STAKING[nodeType];
        if (!config) return 0;

        const dailyRate = config.apy / 365;
        return amount * dailyRate * days;
    }

    /**
     * Compound stake rewards
     */
    async compound(stakeId) {
        const rewards = await this._economy.calculateRewards(stakeId);
        // Would re-stake rewards
        return rewards;
    }

    /**
     * Get all stakes for a wallet
     */
    async getStakes(walletId) {
        // Would fetch from stake store
        return [];
    }

    /**
     * Get staking summary
     */
    async getSummary(walletId) {
        const stakes = await this.getStakes(walletId);

        let totalStaked = 0;
        let totalRewards = 0;
        const byType = {};

        for (const stake of stakes) {
            totalStaked += stake.amount;
            totalRewards += stake.rewardsEarned;
            byType[stake.nodeType] = (byType[stake.nodeType] || 0) + stake.amount;
        }

        return {
            totalStaked,
            totalRewards,
            stakesByType: byType,
            activeStakes: stakes.length,
        };
    }
}

// =============================================================================
// MARKETPLACE
// =============================================================================

/**
 * Node marketplace for buying/selling compute, storage, etc.
 */
class Marketplace {
    constructor(economy) {
        this._economy = economy;
        this._listings = [];
        this._orders = [];
    }

    /**
     * List a node for sale/rent
     */
    async createListing(options = {}) {
        const {
            seller,
            nodeType,
            capacity,
            price,
            priceUnit = 'hour',
            minDuration = 1,
            maxDuration = 720, // 30 days
        } = options;

        const listingId = `listing_${Date.now()}`;

        const listing = {
            id: listingId,
            seller,
            nodeType,
            capacity,
            price,
            priceUnit,
            minDuration,
            maxDuration,
            status: 'active',
            createdAt: new Date(),
        };

        this._listings.push(listing);
        return listing;
    }

    /**
     * Search listings
     */
    async search(query = {}) {
        let results = [...this._listings];

        if (query.nodeType) {
            results = results.filter(l => l.nodeType === query.nodeType);
        }

        if (query.maxPrice) {
            results = results.filter(l => l.price <= query.maxPrice);
        }

        if (query.minCapacity) {
            results = results.filter(l => l.capacity >= query.minCapacity);
        }

        if (query.status) {
            results = results.filter(l => l.status === query.status);
        }

        // Sort
        if (query.sortBy === 'price') {
            results.sort((a, b) => a.price - b.price);
        } else if (query.sortBy === 'capacity') {
            results.sort((a, b) => b.capacity - a.capacity);
        }

        return results;
    }

    /**
     * Purchase/rent a listing
     */
    async purchase(buyerWalletId, listingId, duration) {
        const listing = this._listings.find(l => l.id === listingId);
        if (!listing) throw new Error('Listing not found');
        if (listing.status !== 'active') throw new Error('Listing not available');

        const buyer = await this._economy.getWallet(buyerWalletId);
        if (!buyer) throw new Error('Buyer wallet not found');

        const totalCost = listing.price * duration;
        const fee = totalCost * Tokenomics.FEES.marketplace;
        const totalWithFee = totalCost + fee;

        if (buyer.balance(TokenType.ORB) < totalWithFee) {
            throw new Error('Insufficient balance');
        }

        // Execute purchase
        buyer.balances[TokenType.ORB] -= totalWithFee;

        const orderId = `order_${Date.now()}`;
        const order = {
            id: orderId,
            listingId,
            buyer: buyerWalletId,
            seller: listing.seller,
            nodeType: listing.nodeType,
            capacity: listing.capacity,
            duration,
            totalCost,
            fee,
            status: 'completed',
            createdAt: new Date(),
            expiresAt: new Date(Date.now() + duration * 3600000),
        };

        this._orders.push(order);

        // Credit seller (minus fee)
        const seller = await this._economy.getWallet(listing.seller);
        if (seller) {
            seller.balances[TokenType.ORB] =
                (seller.balances[TokenType.ORB] || 0) + totalCost;
        }

        return order;
    }

    /**
     * Cancel a listing
     */
    async cancelListing(listingId, sellerWalletId) {
        const listing = this._listings.find(l => l.id === listingId);
        if (!listing) throw new Error('Listing not found');
        if (listing.seller !== sellerWalletId) throw new Error('Not authorized');

        listing.status = 'cancelled';
        return listing;
    }

    /**
     * Get buyer's orders
     */
    async getOrders(walletId) {
        return this._orders.filter(o => o.buyer === walletId);
    }

    /**
     * Get seller's listings
     */
    async getListings(walletId) {
        return this._listings.filter(l => l.seller === walletId);
    }

    /**
     * Marketplace statistics
     */
    stats() {
        const activeListings = this._listings.filter(l => l.status === 'active');
        const totalVolume = this._orders.reduce((sum, o) => sum + o.totalCost, 0);
        const totalFees = this._orders.reduce((sum, o) => sum + o.fee, 0);

        const byType = {};
        for (const listing of activeListings) {
            byType[listing.nodeType] = (byType[listing.nodeType] || 0) + 1;
        }

        return {
            totalListings: this._listings.length,
            activeListings: activeListings.length,
            totalOrders: this._orders.length,
            totalVolume,
            totalFees,
            listingsByType: byType,
        };
    }
}

// =============================================================================
// REWARDS ENGINE
// =============================================================================

/**
 * Manage rewards distribution
 */
class RewardsEngine {
    constructor(economy) {
        this._economy = economy;
        this._rewardPools = {
            staking: 0,
            referral: 0,
            community: 0,
            developer: 0,
        };
        this._distributions = [];
    }

    /**
     * Fund a reward pool
     */
    fundPool(pool, amount) {
        if (pool in this._rewardPools) {
            this._rewardPools[pool] += amount;
        }
    }

    /**
     * Distribute rewards to wallet
     */
    async distribute(walletId, amount, pool, reason) {
        if (this._rewardPools[pool] < amount) {
            throw new Error('Insufficient pool balance');
        }

        const wallet = await this._economy.getWallet(walletId);
        if (!wallet) throw new Error('Wallet not found');

        this._rewardPools[pool] -= amount;
        wallet.balances[TokenType.ORB] =
            (wallet.balances[TokenType.ORB] || 0) + amount;

        const distribution = {
            id: `dist_${Date.now()}`,
            wallet: walletId,
            amount,
            pool,
            reason,
            timestamp: new Date(),
        };

        this._distributions.push(distribution);
        return distribution;
    }

    /**
     * Claim referral rewards
     */
    async claimReferral(walletId, referredWalletId) {
        // Referral bonus: 5% of referred user's first stake
        const REFERRAL_BONUS_PERCENT = 0.05;
        // Would calculate based on referred user's activity
        const bonus = 10; // Placeholder

        return await this.distribute(walletId, bonus, 'referral', `Referral: ${referredWalletId}`);
    }

    /**
     * Distribute developer rewards
     */
    async developerReward(walletId, contribution) {
        // Reward developers for contributions
        const rewardTable = {
            'bug_fix': 50,
            'feature': 200,
            'documentation': 25,
            'security': 500,
        };

        const amount = rewardTable[contribution] || 10;
        return await this.distribute(walletId, amount, 'developer', contribution);
    }

    /**
     * Get pool balances
     */
    getPoolBalances() {
        return { ...this._rewardPools };
    }

    /**
     * Get distribution history
     */
    getHistory(walletId = null) {
        if (walletId) {
            return this._distributions.filter(d => d.wallet === walletId);
        }
        return [...this._distributions];
    }
}

// =============================================================================
// GOVERNANCE
// =============================================================================

/**
 * Token-based governance
 */
class Governance {
    constructor(economy) {
        this._economy = economy;
        this._proposals = [];
        this._votes = [];
    }

    /**
     * Create a governance proposal
     */
    async createProposal(options = {}) {
        const {
            creator,
            title,
            description,
            type = 'general', // general, parameter, upgrade, treasury
            votingPeriod = 7 * 24 * 3600000, // 7 days
            quorum = 0.10, // 10% of staked tokens
            threshold = 0.50, // 50% approval
        } = options;

        const proposalId = `prop_${Date.now()}`;

        const proposal = {
            id: proposalId,
            creator,
            title,
            description,
            type,
            votingStart: new Date(),
            votingEnd: new Date(Date.now() + votingPeriod),
            quorum,
            threshold,
            status: 'active',
            votesFor: 0,
            votesAgainst: 0,
            voters: [],
        };

        this._proposals.push(proposal);
        return proposal;
    }

    /**
     * Vote on a proposal
     */
    async vote(proposalId, walletId, support, weight = null) {
        const proposal = this._proposals.find(p => p.id === proposalId);
        if (!proposal) throw new Error('Proposal not found');
        if (proposal.status !== 'active') throw new Error('Voting closed');
        if (new Date() > proposal.votingEnd) throw new Error('Voting period ended');
        if (proposal.voters.includes(walletId)) throw new Error('Already voted');

        // Weight based on staked tokens (or provided weight)
        const voteWeight = weight || 1;

        if (support) {
            proposal.votesFor += voteWeight;
        } else {
            proposal.votesAgainst += voteWeight;
        }

        proposal.voters.push(walletId);

        const voteRecord = {
            id: `vote_${Date.now()}`,
            proposalId,
            voter: walletId,
            support,
            weight: voteWeight,
            timestamp: new Date(),
        };

        this._votes.push(voteRecord);
        return voteRecord;
    }

    /**
     * Finalize a proposal
     */
    async finalize(proposalId) {
        const proposal = this._proposals.find(p => p.id === proposalId);
        if (!proposal) throw new Error('Proposal not found');
        if (proposal.status !== 'active') throw new Error('Already finalized');
        if (new Date() < proposal.votingEnd) throw new Error('Voting still active');

        const totalVotes = proposal.votesFor + proposal.votesAgainst;
        const approvalRate = totalVotes > 0 ? proposal.votesFor / totalVotes : 0;

        // Check quorum and threshold
        const passed = approvalRate >= proposal.threshold;
        // Would also check quorum against total staked

        proposal.status = passed ? 'passed' : 'rejected';
        proposal.finalizedAt = new Date();
        proposal.result = {
            totalVotes,
            votesFor: proposal.votesFor,
            votesAgainst: proposal.votesAgainst,
            approvalRate,
            passed,
        };

        return proposal;
    }

    /**
     * Get active proposals
     */
    getActive() {
        return this._proposals.filter(p => p.status === 'active');
    }

    /**
     * Get proposal by ID
     */
    getProposal(proposalId) {
        return this._proposals.find(p => p.id === proposalId);
    }

    /**
     * Get voter's voting history
     */
    getVotingHistory(walletId) {
        return this._votes.filter(v => v.voter === walletId);
    }
}

// =============================================================================
// FACTORY FUNCTIONS
// =============================================================================

function createWalletManager(economy) {
    return new WalletManager(economy);
}

function createStakingManager(economy) {
    return new StakingManager(economy);
}

function createMarketplace(economy) {
    return new Marketplace(economy);
}

function createRewardsEngine(economy) {
    return new RewardsEngine(economy);
}

function createGovernance(economy) {
    return new Governance(economy);
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
    Tokenomics,
    WalletManager,
    StakingManager,
    Marketplace,
    RewardsEngine,
    Governance,
    createWalletManager,
    createStakingManager,
    createMarketplace,
    createRewardsEngine,
    createGovernance,
    EconomyAPI,
    Wallet,
    Transaction,
    Stake,
    TokenType,
};

export default {
    Tokenomics,
    WalletManager,
    StakingManager,
    Marketplace,
    RewardsEngine,
    Governance,
    createWalletManager,
    createStakingManager,
    createMarketplace,
    createRewardsEngine,
    createGovernance,
};
