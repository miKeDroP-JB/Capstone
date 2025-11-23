// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title OrbGaming
 * @dev Provably fair gaming and gambling for 0RB_AETHER
 * Features: Dice, Coin Flip, Slots, Prediction Markets
 * Uses block hash for randomness (NOTE: Use Chainlink VRF in production)
 */
contract OrbGaming is ReentrancyGuard, Ownable {

    uint256 public houseEdge = 200; // 2% in basis points
    uint256 public minBet = 0.001 ether;
    uint256 public maxBet = 10 ether;

    struct Game {
        address player;
        uint256 bet;
        uint256 payout;
        uint256 blockNumber;
        bytes32 seedHash;
        bool resolved;
    }

    mapping(uint256 => Game) public games;
    uint256 public nextGameId;

    event GameCreated(uint256 indexed gameId, address indexed player, uint256 bet);
    event GameResolved(uint256 indexed gameId, bool won, uint256 payout);
    event DiceRolled(uint256 indexed gameId, uint256 result, uint256 target);
    event CoinFlipped(uint256 indexed gameId, bool result);

    constructor() Ownable(msg.sender) {}

    receive() external payable {} // Accept house bankroll

    /**
     * @dev Dice game: Roll under target (2-99)
     * Payout = bet * (100 - houseEdge) / target
     */
    function playDice(uint256 target, bytes32 seedHash)
        public
        payable
        nonReentrant
        returns (uint256)
    {
        require(msg.value >= minBet && msg.value <= maxBet, "Invalid bet");
        require(target >= 2 && target <= 99, "Invalid target");

        uint256 gameId = nextGameId++;
        games[gameId] = Game({
            player: msg.sender,
            bet: msg.value,
            payout: 0,
            blockNumber: block.number,
            seedHash: seedHash,
            resolved: false
        });

        emit GameCreated(gameId, msg.sender, msg.value);
        return gameId;
    }

    /**
     * @dev Resolve dice game
     */
    function resolveDice(uint256 gameId, uint256 target, string memory seed)
        public
        nonReentrant
    {
        Game storage game = games[gameId];
        require(!game.resolved, "Already resolved");
        require(keccak256(abi.encodePacked(seed)) == game.seedHash, "Invalid seed");
        require(block.number > game.blockNumber, "Wait for next block");

        // Generate random number 1-100
        uint256 random = _getRandomNumber(gameId, seed) % 100 + 1;
        bool won = random < target;

        uint256 payout = 0;
        if (won) {
            uint256 multiplier = (10000 - houseEdge) * 100 / target;
            payout = (game.bet * multiplier) / 10000;

            require(address(this).balance >= payout, "Insufficient house balance");
            (bool success, ) = game.player.call{value: payout}("");
            require(success, "Payout failed");
        }

        game.payout = payout;
        game.resolved = true;

        emit DiceRolled(gameId, random, target);
        emit GameResolved(gameId, won, payout);
    }

    /**
     * @dev Coin flip game
     */
    function playCoinFlip(bool prediction, bytes32 seedHash)
        public
        payable
        nonReentrant
        returns (uint256)
    {
        require(msg.value >= minBet && msg.value <= maxBet, "Invalid bet");

        uint256 gameId = nextGameId++;
        games[gameId] = Game({
            player: msg.sender,
            bet: msg.value,
            payout: 0,
            blockNumber: block.number,
            seedHash: seedHash,
            resolved: false
        });

        emit GameCreated(gameId, msg.sender, msg.value);
        return gameId;
    }

    /**
     * @dev Resolve coin flip
     */
    function resolveCoinFlip(uint256 gameId, bool prediction, string memory seed)
        public
        nonReentrant
    {
        Game storage game = games[gameId];
        require(!game.resolved, "Already resolved");
        require(keccak256(abi.encodePacked(seed)) == game.seedHash, "Invalid seed");
        require(block.number > game.blockNumber, "Wait for next block");

        bool result = _getRandomNumber(gameId, seed) % 2 == 0;
        bool won = result == prediction;

        uint256 payout = 0;
        if (won) {
            payout = (game.bet * 2 * (10000 - houseEdge)) / 10000;

            require(address(this).balance >= payout, "Insufficient house balance");
            (bool success, ) = game.player.call{value: payout}("");
            require(success, "Payout failed");
        }

        game.payout = payout;
        game.resolved = true;

        emit CoinFlipped(gameId, result);
        emit GameResolved(gameId, won, payout);
    }

    /**
     * @dev Slots game (3 reels, 0-9)
     */
    function playSlots(bytes32 seedHash)
        public
        payable
        nonReentrant
        returns (uint256)
    {
        require(msg.value >= minBet && msg.value <= maxBet, "Invalid bet");

        uint256 gameId = nextGameId++;
        games[gameId] = Game({
            player: msg.sender,
            bet: msg.value,
            payout: 0,
            blockNumber: block.number,
            seedHash: seedHash,
            resolved: false
        });

        emit GameCreated(gameId, msg.sender, msg.value);
        return gameId;
    }

    /**
     * @dev Resolve slots
     */
    function resolveSlots(uint256 gameId, string memory seed)
        public
        nonReentrant
    {
        Game storage game = games[gameId];
        require(!game.resolved, "Already resolved");
        require(keccak256(abi.encodePacked(seed)) == game.seedHash, "Invalid seed");
        require(block.number > game.blockNumber, "Wait for next block");

        uint256 random = _getRandomNumber(gameId, seed);
        uint256 reel1 = random % 10;
        uint256 reel2 = (random / 10) % 10;
        uint256 reel3 = (random / 100) % 10;

        uint256 multiplier = 0;
        if (reel1 == reel2 && reel2 == reel3) {
            // Triple match
            if (reel1 == 7) {
                multiplier = 50; // Jackpot!
            } else {
                multiplier = 10;
            }
        } else if (reel1 == reel2 || reel2 == reel3) {
            // Double match
            multiplier = 2;
        }

        uint256 payout = 0;
        if (multiplier > 0) {
            payout = (game.bet * multiplier * (10000 - houseEdge)) / 10000;

            require(address(this).balance >= payout, "Insufficient house balance");
            (bool success, ) = game.player.call{value: payout}("");
            require(success, "Payout failed");
        }

        game.payout = payout;
        game.resolved = true;

        emit GameResolved(gameId, multiplier > 0, payout);
    }

    /**
     * @dev Generate pseudo-random number (USE CHAINLINK VRF IN PRODUCTION)
     */
    function _getRandomNumber(uint256 gameId, string memory seed)
        private
        view
        returns (uint256)
    {
        return uint256(keccak256(abi.encodePacked(
            blockhash(games[gameId].blockNumber),
            seed,
            gameId,
            games[gameId].player
        )));
    }

    /**
     * @dev Owner functions
     */
    function setHouseEdge(uint256 newEdge) public onlyOwner {
        require(newEdge <= 500, "Edge too high"); // Max 5%
        houseEdge = newEdge;
    }

    function setBetLimits(uint256 min, uint256 max) public onlyOwner {
        minBet = min;
        maxBet = max;
    }

    function withdraw(uint256 amount) public onlyOwner {
        require(address(this).balance >= amount, "Insufficient balance");
        (bool success, ) = owner().call{value: amount}("");
        require(success, "Withdrawal failed");
    }

    function getHouseBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
