// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title OrbCreatorToken
 * @dev Personal creator tokens with bonding curve pricing
 * Enables creators to launch their own economy with automatic market making
 */
contract OrbCreatorToken is ERC20, ReentrancyGuard {

    address public creator;
    uint256 public reserveBalance; // ETH in reserve
    uint256 public constant CURVE_SLOPE = 1000000; // Linear bonding curve parameter

    struct Subscription {
        uint256 tokensRequired;
        uint256 duration;
        mapping(address => uint256) expirations;
    }

    Subscription public subscription;

    event TokensPurchased(address indexed buyer, uint256 ethAmount, uint256 tokenAmount);
    event TokensSold(address indexed seller, uint256 tokenAmount, uint256 ethAmount);
    event SubscriptionActivated(address indexed subscriber, uint256 expiresAt);

    constructor(
        string memory name,
        string memory symbol,
        address _creator,
        uint256 initialSupply
    ) ERC20(name, symbol) {
        creator = _creator;

        if (initialSupply > 0) {
            _mint(_creator, initialSupply);
        }
    }

    receive() external payable {} // Accept ETH

    /**
     * @dev Buy tokens using bonding curve
     * Price = (supply / CURVE_SLOPE) * amount
     */
    function buyTokens() public payable nonReentrant {
        require(msg.value > 0, "Must send ETH");

        uint256 tokenAmount = _calculatePurchaseReturn(msg.value);
        require(tokenAmount > 0, "Token amount too small");

        reserveBalance += msg.value;
        _mint(msg.sender, tokenAmount);

        emit TokensPurchased(msg.sender, msg.value, tokenAmount);
    }

    /**
     * @dev Sell tokens back to bonding curve
     */
    function sellTokens(uint256 tokenAmount) public nonReentrant {
        require(balanceOf(msg.sender) >= tokenAmount, "Insufficient balance");

        uint256 ethAmount = _calculateSaleReturn(tokenAmount);
        require(ethAmount > 0, "ETH amount too small");
        require(reserveBalance >= ethAmount, "Insufficient reserve");

        _burn(msg.sender, tokenAmount);
        reserveBalance -= ethAmount;

        (bool success, ) = msg.sender.call{value: ethAmount}("");
        require(success, "ETH transfer failed");

        emit TokensSold(msg.sender, tokenAmount, ethAmount);
    }

    /**
     * @dev Calculate tokens received for ETH amount
     * Using linear bonding curve: price = supply / slope
     */
    function _calculatePurchaseReturn(uint256 ethAmount) private view returns (uint256) {
        uint256 currentSupply = totalSupply();

        // Simplified linear bonding curve
        // In production, use more sophisticated curve (sqrt, exponential, etc.)
        return (ethAmount * CURVE_SLOPE) / (currentSupply + 1 ether);
    }

    /**
     * @dev Calculate ETH returned for token amount
     */
    function _calculateSaleReturn(uint256 tokenAmount) private view returns (uint256) {
        uint256 currentSupply = totalSupply();
        return (tokenAmount * (currentSupply + 1 ether)) / CURVE_SLOPE;
    }

    /**
     * @dev Get current buy price per token
     */
    function getCurrentBuyPrice() public view returns (uint256) {
        uint256 currentSupply = totalSupply();
        return (currentSupply + 1 ether) / CURVE_SLOPE;
    }

    /**
     * @dev Get current sell price per token
     */
    function getCurrentSellPrice() public view returns (uint256) {
        return getCurrentBuyPrice() * 95 / 100; // 5% sell fee
    }

    /**
     * @dev Set up subscription tier
     */
    function setupSubscription(uint256 tokensRequired, uint256 duration) public {
        require(msg.sender == creator, "Only creator");
        subscription.tokensRequired = tokensRequired;
        subscription.duration = duration;
    }

    /**
     * @dev Subscribe by holding tokens
     */
    function subscribe() public {
        require(balanceOf(msg.sender) >= subscription.tokensRequired, "Insufficient tokens");

        subscription.expirations[msg.sender] = block.timestamp + subscription.duration;
        emit SubscriptionActivated(msg.sender, subscription.expirations[msg.sender]);
    }

    /**
     * @dev Check if address has active subscription
     */
    function hasActiveSubscription(address subscriber) public view returns (bool) {
        return subscription.expirations[subscriber] > block.timestamp;
    }

    /**
     * @dev Creator withdraw collected fees
     */
    function creatorWithdraw(uint256 amount) public {
        require(msg.sender == creator, "Only creator");
        uint256 available = address(this).balance - reserveBalance;
        require(available >= amount, "Insufficient available balance");

        (bool success, ) = creator.call{value: amount}("");
        require(success, "Transfer failed");
    }

    /**
     * @dev Get reserve ratio (for health monitoring)
     */
    function getReserveRatio() public view returns (uint256) {
        uint256 supply = totalSupply();
        if (supply == 0) return 0;
        return (reserveBalance * 10000) / supply;
    }
}
