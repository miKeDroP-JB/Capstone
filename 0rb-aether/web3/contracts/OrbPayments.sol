// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title OrbPayments
 * @dev Advanced payment system for 0RB_AETHER
 * Supports: instant payments, streaming payments, escrow, milestone-based releases
 */
contract OrbPayments is ReentrancyGuard, Ownable {

    struct PaymentSplit {
        address[] recipients;
        uint256[] shares; // In basis points (10000 = 100%)
    }

    struct StreamingPayment {
        address sender;
        address recipient;
        uint256 totalAmount;
        uint256 startTime;
        uint256 duration;
        uint256 withdrawn;
        bool active;
    }

    struct EscrowPayment {
        address payer;
        address payee;
        uint256 amount;
        uint256 releaseTime;
        bool released;
        bool refunded;
    }

    struct MilestonePayment {
        address payer;
        address payee;
        uint256 totalAmount;
        uint256[] milestoneAmounts;
        bool[] milestoneReleased;
        uint256 currentMilestone;
    }

    mapping(uint256 => PaymentSplit) public paymentSplits;
    mapping(uint256 => StreamingPayment) public streams;
    mapping(uint256 => EscrowPayment) public escrows;
    mapping(uint256 => MilestonePayment) public milestones;

    uint256 public nextSplitId;
    uint256 public nextStreamId;
    uint256 public nextEscrowId;
    uint256 public nextMilestoneId;

    event SplitCreated(uint256 indexed splitId, address[] recipients, uint256[] shares);
    event PaymentSent(uint256 indexed splitId, uint256 amount);
    event StreamCreated(uint256 indexed streamId, address indexed sender, address indexed recipient, uint256 amount);
    event StreamWithdrawn(uint256 indexed streamId, uint256 amount);
    event EscrowCreated(uint256 indexed escrowId, address indexed payer, address indexed payee, uint256 amount);
    event EscrowReleased(uint256 indexed escrowId);
    event MilestoneCreated(uint256 indexed milestoneId, uint256 totalAmount, uint256 numMilestones);
    event MilestoneReleased(uint256 indexed milestoneId, uint256 milestone, uint256 amount);

    constructor() Ownable(msg.sender) {}

    /**
     * @dev Create payment split configuration
     */
    function createSplit(address[] memory recipients, uint256[] memory shares)
        public
        returns (uint256)
    {
        require(recipients.length == shares.length, "Length mismatch");

        uint256 totalShares = 0;
        for (uint256 i = 0; i < shares.length; i++) {
            totalShares += shares[i];
        }
        require(totalShares == 10000, "Shares must sum to 10000");

        uint256 splitId = nextSplitId++;
        paymentSplits[splitId] = PaymentSplit({
            recipients: recipients,
            shares: shares
        });

        emit SplitCreated(splitId, recipients, shares);
        return splitId;
    }

    /**
     * @dev Send payment to split
     */
    function sendToSplit(uint256 splitId) public payable nonReentrant {
        PaymentSplit storage split = paymentSplits[splitId];
        require(split.recipients.length > 0, "Split not found");

        for (uint256 i = 0; i < split.recipients.length; i++) {
            uint256 amount = (msg.value * split.shares[i]) / 10000;
            (bool success, ) = split.recipients[i].call{value: amount}("");
            require(success, "Transfer failed");
        }

        emit PaymentSent(splitId, msg.value);
    }

    /**
     * @dev Create streaming payment (per-second micropayments)
     */
    function createStream(address recipient, uint256 duration)
        public
        payable
        returns (uint256)
    {
        require(msg.value > 0, "Amount must be > 0");
        require(duration > 0, "Duration must be > 0");

        uint256 streamId = nextStreamId++;
        streams[streamId] = StreamingPayment({
            sender: msg.sender,
            recipient: recipient,
            totalAmount: msg.value,
            startTime: block.timestamp,
            duration: duration,
            withdrawn: 0,
            active: true
        });

        emit StreamCreated(streamId, msg.sender, recipient, msg.value);
        return streamId;
    }

    /**
     * @dev Withdraw from stream
     */
    function withdrawStream(uint256 streamId) public nonReentrant {
        StreamingPayment storage stream = streams[streamId];
        require(stream.active, "Stream not active");
        require(msg.sender == stream.recipient, "Not recipient");

        uint256 elapsed = block.timestamp - stream.startTime;
        uint256 vested = elapsed >= stream.duration
            ? stream.totalAmount
            : (stream.totalAmount * elapsed) / stream.duration;

        uint256 withdrawable = vested - stream.withdrawn;
        require(withdrawable > 0, "Nothing to withdraw");

        stream.withdrawn += withdrawable;
        if (stream.withdrawn >= stream.totalAmount) {
            stream.active = false;
        }

        (bool success, ) = stream.recipient.call{value: withdrawable}("");
        require(success, "Transfer failed");

        emit StreamWithdrawn(streamId, withdrawable);
    }

    /**
     * @dev Create escrow payment with time lock
     */
    function createEscrow(address payee, uint256 releaseTime)
        public
        payable
        returns (uint256)
    {
        require(msg.value > 0, "Amount must be > 0");
        require(releaseTime > block.timestamp, "Release time must be future");

        uint256 escrowId = nextEscrowId++;
        escrows[escrowId] = EscrowPayment({
            payer: msg.sender,
            payee: payee,
            amount: msg.value,
            releaseTime: releaseTime,
            released: false,
            refunded: false
        });

        emit EscrowCreated(escrowId, msg.sender, payee, msg.value);
        return escrowId;
    }

    /**
     * @dev Release escrow
     */
    function releaseEscrow(uint256 escrowId) public nonReentrant {
        EscrowPayment storage escrow = escrows[escrowId];
        require(!escrow.released && !escrow.refunded, "Already processed");
        require(block.timestamp >= escrow.releaseTime, "Not yet releasable");
        require(msg.sender == escrow.payer || msg.sender == escrow.payee, "Not authorized");

        escrow.released = true;
        (bool success, ) = escrow.payee.call{value: escrow.amount}("");
        require(success, "Transfer failed");

        emit EscrowReleased(escrowId);
    }

    /**
     * @dev Create milestone-based payment
     */
    function createMilestone(address payee, uint256[] memory milestoneAmounts)
        public
        payable
        returns (uint256)
    {
        uint256 total = 0;
        for (uint256 i = 0; i < milestoneAmounts.length; i++) {
            total += milestoneAmounts[i];
        }
        require(msg.value == total, "Amount mismatch");

        uint256 milestoneId = nextMilestoneId++;
        bool[] memory released = new bool[](milestoneAmounts.length);

        milestones[milestoneId] = MilestonePayment({
            payer: msg.sender,
            payee: payee,
            totalAmount: msg.value,
            milestoneAmounts: milestoneAmounts,
            milestoneReleased: released,
            currentMilestone: 0
        });

        emit MilestoneCreated(milestoneId, msg.value, milestoneAmounts.length);
        return milestoneId;
    }

    /**
     * @dev Release next milestone
     */
    function releaseMilestone(uint256 milestoneId) public nonReentrant {
        MilestonePayment storage milestone = milestones[milestoneId];
        require(msg.sender == milestone.payer, "Only payer can release");
        require(milestone.currentMilestone < milestone.milestoneAmounts.length, "All released");

        uint256 amount = milestone.milestoneAmounts[milestone.currentMilestone];
        milestone.milestoneReleased[milestone.currentMilestone] = true;

        (bool success, ) = milestone.payee.call{value: amount}("");
        require(success, "Transfer failed");

        emit MilestoneReleased(milestoneId, milestone.currentMilestone, amount);
        milestone.currentMilestone++;
    }
}
