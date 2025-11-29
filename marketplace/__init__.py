#!/usr/bin/env python3
"""
NODE MARKETPLACE - 0RB_AETHER Economy
The decentralized marketplace for compute, storage, and AI resources.

This is where the economy comes alive.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import json
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_DOWN
import heapq

__version__ = "0.1.0"


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class NodeType(Enum):
    """Types of nodes in the marketplace"""
    COMPUTE = "compute"      # CPU/GPU compute
    STORAGE = "storage"      # Data storage
    VALIDATOR = "validator"  # Network validators
    AI_INFERENCE = "ai"      # AI model inference
    BANDWIDTH = "bandwidth"  # Network bandwidth
    ORACLE = "oracle"        # Data oracles


class OrderType(Enum):
    """Order types"""
    BUY = "buy"    # Demand (looking to buy resources)
    SELL = "sell"  # Supply (offering resources)


class OrderStatus(Enum):
    """Order statuses"""
    PENDING = "pending"
    ACTIVE = "active"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TransactionStatus(Enum):
    """Transaction statuses"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    DISPUTED = "disputed"
    RESOLVED = "resolved"


# =============================================================================
# NODE REGISTRY
# =============================================================================

@dataclass
class NodeSpec:
    """Specification for a node"""
    node_type: NodeType
    capacity: float          # Units of capacity (vCPUs, GB, TFLOPs, etc.)
    location: str            # Geographic region
    availability: float      # Uptime SLA (0-1)
    latency_ms: int          # Max latency in ms
    certifications: List[str] = field(default_factory=list)  # SOC2, HIPAA, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Node:
    """A registered node in the marketplace"""
    id: str
    owner_id: str
    spec: NodeSpec
    status: str = "offline"  # offline, online, busy, maintenance
    reputation: float = 0.0  # 0-5 star rating
    total_jobs: int = 0
    successful_jobs: int = 0
    total_earnings: Decimal = Decimal("0")
    registered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    stake_amount: Decimal = Decimal("0")  # Collateral staked


class NodeRegistry:
    """Registry of all nodes in the marketplace"""

    # Minimum stake requirements by node type
    MIN_STAKE = {
        NodeType.COMPUTE: Decimal("100"),
        NodeType.STORAGE: Decimal("50"),
        NodeType.VALIDATOR: Decimal("10000"),
        NodeType.AI_INFERENCE: Decimal("500"),
        NodeType.BANDWIDTH: Decimal("25"),
        NodeType.ORACLE: Decimal("1000"),
    }

    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._by_type: Dict[NodeType, List[str]] = {t: [] for t in NodeType}
        self._by_owner: Dict[str, List[str]] = {}

    def register(
        self,
        owner_id: str,
        spec: NodeSpec,
        stake: Decimal
    ) -> Node:
        """Register a new node"""
        min_stake = self.MIN_STAKE.get(spec.node_type, Decimal("100"))
        if stake < min_stake:
            raise ValueError(f"Minimum stake for {spec.node_type.value}: {min_stake} ORB")

        node_id = hashlib.sha256(
            f"{owner_id}-{spec.node_type.value}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        node = Node(
            id=node_id,
            owner_id=owner_id,
            spec=spec,
            stake_amount=stake,
        )

        self._nodes[node_id] = node
        self._by_type[spec.node_type].append(node_id)

        if owner_id not in self._by_owner:
            self._by_owner[owner_id] = []
        self._by_owner[owner_id].append(node_id)

        return node

    def unregister(self, node_id: str) -> Optional[Decimal]:
        """Unregister a node and return stake"""
        node = self._nodes.get(node_id)
        if not node:
            return None

        if node.status == "busy":
            raise ValueError("Cannot unregister busy node")

        # Remove from indices
        self._by_type[node.spec.node_type].remove(node_id)
        self._by_owner[node.owner_id].remove(node_id)
        del self._nodes[node_id]

        return node.stake_amount

    def get(self, node_id: str) -> Optional[Node]:
        """Get node by ID"""
        return self._nodes.get(node_id)

    def find(
        self,
        node_type: NodeType = None,
        min_capacity: float = 0,
        location: str = None,
        min_availability: float = 0,
        certifications: List[str] = None,
        status: str = "online"
    ) -> List[Node]:
        """Find nodes matching criteria"""
        if node_type:
            candidates = [self._nodes[nid] for nid in self._by_type.get(node_type, [])]
        else:
            candidates = list(self._nodes.values())

        results = []
        for node in candidates:
            if status and node.status != status:
                continue
            if min_capacity and node.spec.capacity < min_capacity:
                continue
            if location and node.spec.location != location:
                continue
            if min_availability and node.spec.availability < min_availability:
                continue
            if certifications:
                if not all(c in node.spec.certifications for c in certifications):
                    continue
            results.append(node)

        # Sort by reputation
        results.sort(key=lambda n: n.reputation, reverse=True)
        return results

    def by_owner(self, owner_id: str) -> List[Node]:
        """Get all nodes owned by a user"""
        return [self._nodes[nid] for nid in self._by_owner.get(owner_id, [])]

    def update_status(self, node_id: str, status: str):
        """Update node status"""
        if node_id in self._nodes:
            self._nodes[node_id].status = status
            self._nodes[node_id].last_seen = datetime.now()

    def update_reputation(self, node_id: str, rating: float):
        """Update node reputation (rolling average)"""
        node = self._nodes.get(node_id)
        if node:
            # Weighted average favoring recent ratings
            old_weight = min(node.total_jobs, 100) / 100
            node.reputation = (node.reputation * old_weight + rating * (1 - old_weight))

    def stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        by_type = {t.value: len(ids) for t, ids in self._by_type.items()}
        online = len([n for n in self._nodes.values() if n.status == "online"])
        total_capacity = {
            t.value: sum(
                self._nodes[nid].spec.capacity
                for nid in ids
                if self._nodes[nid].status == "online"
            )
            for t, ids in self._by_type.items()
        }

        return {
            "total_nodes": len(self._nodes),
            "online_nodes": online,
            "by_type": by_type,
            "total_capacity": total_capacity,
            "unique_owners": len(self._by_owner),
        }


# =============================================================================
# ORDER BOOK
# =============================================================================

@dataclass
class Order:
    """A marketplace order"""
    id: str
    order_type: OrderType
    node_type: NodeType
    owner_id: str
    quantity: float          # Amount of resource
    price: Decimal           # Price per unit per hour
    duration_hours: int      # Duration needed
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = None
    requirements: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """For heap comparison - buys highest first, sells lowest first"""
        if self.order_type == OrderType.BUY:
            return self.price > other.price  # Higher price = higher priority
        return self.price < other.price  # Lower price = higher priority


class OrderBook:
    """Order book with matching engine"""

    def __init__(self):
        self._orders: Dict[str, Order] = {}
        # Separate heaps for each node type
        self._buy_heaps: Dict[NodeType, List[Order]] = {t: [] for t in NodeType}
        self._sell_heaps: Dict[NodeType, List[Order]] = {t: [] for t in NodeType}
        self._order_counter = 0

    def place_order(
        self,
        order_type: OrderType,
        node_type: NodeType,
        owner_id: str,
        quantity: float,
        price: Decimal,
        duration_hours: int = 1,
        requirements: Dict[str, Any] = None,
        expires_in_hours: int = 24
    ) -> Order:
        """Place a new order"""
        self._order_counter += 1
        order_id = f"ord_{self._order_counter:08d}"

        order = Order(
            id=order_id,
            order_type=order_type,
            node_type=node_type,
            owner_id=owner_id,
            quantity=quantity,
            price=price,
            duration_hours=duration_hours,
            status=OrderStatus.ACTIVE,
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            requirements=requirements or {},
        )

        self._orders[order_id] = order

        # Add to appropriate heap
        if order_type == OrderType.BUY:
            heapq.heappush(self._buy_heaps[node_type], order)
        else:
            heapq.heappush(self._sell_heaps[node_type], order)

        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        order = self._orders.get(order_id)
        if not order or order.status not in [OrderStatus.ACTIVE, OrderStatus.PENDING]:
            return False

        order.status = OrderStatus.CANCELLED
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self._orders.get(order_id)

    def get_orders(
        self,
        owner_id: str = None,
        node_type: NodeType = None,
        status: OrderStatus = None
    ) -> List[Order]:
        """Get orders matching criteria"""
        results = []
        for order in self._orders.values():
            if owner_id and order.owner_id != owner_id:
                continue
            if node_type and order.node_type != node_type:
                continue
            if status and order.status != status:
                continue
            results.append(order)
        return results

    def match_orders(self, node_type: NodeType) -> List[Tuple[Order, Order, float, Decimal]]:
        """
        Match buy and sell orders.
        Returns list of (buy_order, sell_order, quantity, price) tuples.
        """
        matches = []

        buy_heap = self._buy_heaps[node_type]
        sell_heap = self._sell_heaps[node_type]

        while buy_heap and sell_heap:
            # Get best buy and sell
            best_buy = buy_heap[0]
            best_sell = sell_heap[0]

            # Skip cancelled/filled orders
            if best_buy.status not in [OrderStatus.ACTIVE, OrderStatus.PARTIAL]:
                heapq.heappop(buy_heap)
                continue
            if best_sell.status not in [OrderStatus.ACTIVE, OrderStatus.PARTIAL]:
                heapq.heappop(sell_heap)
                continue

            # Check if prices cross
            if best_buy.price < best_sell.price:
                break  # No match possible

            # Calculate match quantity
            buy_remaining = best_buy.quantity - best_buy.filled_quantity
            sell_remaining = best_sell.quantity - best_sell.filled_quantity
            match_quantity = min(buy_remaining, sell_remaining)

            # Execution price is midpoint
            exec_price = (best_buy.price + best_sell.price) / 2

            matches.append((best_buy, best_sell, match_quantity, exec_price))

            # Update fill quantities
            best_buy.filled_quantity += match_quantity
            best_sell.filled_quantity += match_quantity

            # Update statuses
            if best_buy.filled_quantity >= best_buy.quantity:
                best_buy.status = OrderStatus.FILLED
                heapq.heappop(buy_heap)
            else:
                best_buy.status = OrderStatus.PARTIAL

            if best_sell.filled_quantity >= best_sell.quantity:
                best_sell.status = OrderStatus.FILLED
                heapq.heappop(sell_heap)
            else:
                best_sell.status = OrderStatus.PARTIAL

        return matches

    def get_spread(self, node_type: NodeType) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Get best bid/ask spread"""
        buy_heap = self._buy_heaps[node_type]
        sell_heap = self._sell_heaps[node_type]

        best_bid = None
        best_ask = None

        # Find best active bid
        for order in buy_heap:
            if order.status in [OrderStatus.ACTIVE, OrderStatus.PARTIAL]:
                best_bid = order.price
                break

        # Find best active ask
        for order in sell_heap:
            if order.status in [OrderStatus.ACTIVE, OrderStatus.PARTIAL]:
                best_ask = order.price
                break

        return (best_bid, best_ask)

    def get_depth(self, node_type: NodeType, levels: int = 10) -> Dict[str, List]:
        """Get order book depth"""
        bids = []
        asks = []

        # Aggregate bids
        bid_prices = {}
        for order in self._buy_heaps[node_type]:
            if order.status in [OrderStatus.ACTIVE, OrderStatus.PARTIAL]:
                remaining = order.quantity - order.filled_quantity
                bid_prices[order.price] = bid_prices.get(order.price, 0) + remaining

        # Aggregate asks
        ask_prices = {}
        for order in self._sell_heaps[node_type]:
            if order.status in [OrderStatus.ACTIVE, OrderStatus.PARTIAL]:
                remaining = order.quantity - order.filled_quantity
                ask_prices[order.price] = ask_prices.get(order.price, 0) + remaining

        # Sort and take top levels
        bids = sorted(
            [(p, q) for p, q in bid_prices.items()],
            key=lambda x: x[0],
            reverse=True
        )[:levels]

        asks = sorted(
            [(p, q) for p, q in ask_prices.items()],
            key=lambda x: x[0]
        )[:levels]

        return {"bids": bids, "asks": asks}

    def expire_orders(self):
        """Expire old orders"""
        now = datetime.now()
        for order in self._orders.values():
            if order.status == OrderStatus.ACTIVE and order.expires_at < now:
                order.status = OrderStatus.EXPIRED


# =============================================================================
# TRANSACTIONS
# =============================================================================

@dataclass
class Transaction:
    """A completed transaction"""
    id: str
    buy_order_id: str
    sell_order_id: str
    buyer_id: str
    seller_id: str
    node_id: str
    node_type: NodeType
    quantity: float
    price: Decimal
    duration_hours: int
    total_cost: Decimal
    fee: Decimal
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime = None
    ended_at: datetime = None
    rating_buyer: float = None
    rating_seller: float = None


class TransactionEngine:
    """Manages transactions and settlements"""

    # Fee structure
    FEE_RATE = Decimal("0.025")  # 2.5% platform fee

    def __init__(self, registry: NodeRegistry):
        self._registry = registry
        self._transactions: Dict[str, Transaction] = {}
        self._by_buyer: Dict[str, List[str]] = {}
        self._by_seller: Dict[str, List[str]] = {}
        self._tx_counter = 0

    def create_transaction(
        self,
        buy_order: Order,
        sell_order: Order,
        node_id: str,
        quantity: float,
        price: Decimal
    ) -> Transaction:
        """Create a transaction from matched orders"""
        self._tx_counter += 1
        tx_id = f"tx_{self._tx_counter:08d}"

        total_cost = price * Decimal(str(quantity)) * Decimal(str(buy_order.duration_hours))
        fee = (total_cost * self.FEE_RATE).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)

        tx = Transaction(
            id=tx_id,
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            buyer_id=buy_order.owner_id,
            seller_id=sell_order.owner_id,
            node_id=node_id,
            node_type=buy_order.node_type,
            quantity=quantity,
            price=price,
            duration_hours=buy_order.duration_hours,
            total_cost=total_cost,
            fee=fee,
        )

        self._transactions[tx_id] = tx

        # Index by participants
        if tx.buyer_id not in self._by_buyer:
            self._by_buyer[tx.buyer_id] = []
        self._by_buyer[tx.buyer_id].append(tx_id)

        if tx.seller_id not in self._by_seller:
            self._by_seller[tx.seller_id] = []
        self._by_seller[tx.seller_id].append(tx_id)

        return tx

    def start_transaction(self, tx_id: str) -> bool:
        """Start a transaction (begin resource usage)"""
        tx = self._transactions.get(tx_id)
        if not tx or tx.status != TransactionStatus.PENDING:
            return False

        # Mark node as busy
        self._registry.update_status(tx.node_id, "busy")

        tx.status = TransactionStatus.CONFIRMED
        tx.started_at = datetime.now()
        return True

    def complete_transaction(self, tx_id: str) -> bool:
        """Complete a transaction"""
        tx = self._transactions.get(tx_id)
        if not tx or tx.status != TransactionStatus.CONFIRMED:
            return False

        # Mark node as available
        self._registry.update_status(tx.node_id, "online")

        # Update node stats
        node = self._registry.get(tx.node_id)
        if node:
            node.total_jobs += 1
            node.successful_jobs += 1
            node.total_earnings += tx.total_cost - tx.fee

        tx.ended_at = datetime.now()
        return True

    def dispute_transaction(self, tx_id: str, reason: str) -> bool:
        """Open a dispute on a transaction"""
        tx = self._transactions.get(tx_id)
        if not tx or tx.status != TransactionStatus.CONFIRMED:
            return False

        tx.status = TransactionStatus.DISPUTED
        return True

    def rate_transaction(
        self,
        tx_id: str,
        rater_id: str,
        rating: float
    ) -> bool:
        """Rate a completed transaction"""
        tx = self._transactions.get(tx_id)
        if not tx:
            return False

        rating = max(0, min(5, rating))  # Clamp to 0-5

        if rater_id == tx.buyer_id:
            tx.rating_buyer = rating
            # Update seller's node reputation
            self._registry.update_reputation(tx.node_id, rating)
        elif rater_id == tx.seller_id:
            tx.rating_seller = rating
        else:
            return False

        return True

    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self._transactions.get(tx_id)

    def get_history(
        self,
        user_id: str,
        role: str = "both",  # buyer, seller, both
        limit: int = 50
    ) -> List[Transaction]:
        """Get transaction history for a user"""
        tx_ids = set()

        if role in ["buyer", "both"]:
            tx_ids.update(self._by_buyer.get(user_id, []))
        if role in ["seller", "both"]:
            tx_ids.update(self._by_seller.get(user_id, []))

        transactions = [self._transactions[tid] for tid in tx_ids]
        transactions.sort(key=lambda t: t.created_at, reverse=True)
        return transactions[:limit]

    def stats(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        total = len(self._transactions)
        completed = len([t for t in self._transactions.values()
                        if t.status == TransactionStatus.CONFIRMED])
        disputed = len([t for t in self._transactions.values()
                       if t.status == TransactionStatus.DISPUTED])

        total_volume = sum(t.total_cost for t in self._transactions.values())
        total_fees = sum(t.fee for t in self._transactions.values())

        return {
            "total_transactions": total,
            "completed": completed,
            "disputed": disputed,
            "total_volume": float(total_volume),
            "total_fees": float(total_fees),
        }


# =============================================================================
# PRICING ENGINE
# =============================================================================

class PricingEngine:
    """Dynamic pricing for marketplace resources"""

    # Base prices per hour
    BASE_PRICES = {
        NodeType.COMPUTE: Decimal("0.10"),      # $0.10/vCPU-hour
        NodeType.STORAGE: Decimal("0.05"),      # $0.05/GB-hour
        NodeType.VALIDATOR: Decimal("1.00"),    # $1.00/validator-hour
        NodeType.AI_INFERENCE: Decimal("0.50"), # $0.50/TFLOP-hour
        NodeType.BANDWIDTH: Decimal("0.01"),    # $0.01/GB-hour
        NodeType.ORACLE: Decimal("0.25"),       # $0.25/query-hour
    }

    def __init__(self, order_book: OrderBook):
        self._order_book = order_book
        self._price_history: Dict[NodeType, List[Tuple[datetime, Decimal]]] = {
            t: [] for t in NodeType
        }

    def get_spot_price(self, node_type: NodeType) -> Decimal:
        """Get current spot price"""
        bid, ask = self._order_book.get_spread(node_type)

        if bid and ask:
            # Midpoint of spread
            return (bid + ask) / 2
        elif bid:
            return bid
        elif ask:
            return ask
        else:
            # Fall back to base price
            return self.BASE_PRICES.get(node_type, Decimal("0.10"))

    def get_price_for_quantity(
        self,
        node_type: NodeType,
        quantity: float,
        order_type: OrderType
    ) -> Decimal:
        """Get price to fill a given quantity (slippage-aware)"""
        depth = self._order_book.get_depth(node_type, levels=50)

        if order_type == OrderType.BUY:
            orders = depth["asks"]
        else:
            orders = depth["bids"]

        if not orders:
            return self.BASE_PRICES.get(node_type, Decimal("0.10"))

        # Walk the book
        remaining = quantity
        total_cost = Decimal("0")

        for price, qty in orders:
            fill_qty = min(remaining, qty)
            total_cost += price * Decimal(str(fill_qty))
            remaining -= fill_qty

            if remaining <= 0:
                break

        if remaining > 0:
            # Not enough liquidity - use last price for remainder
            last_price = orders[-1][0] if orders else self.BASE_PRICES[node_type]
            total_cost += last_price * Decimal(str(remaining))

        return total_cost / Decimal(str(quantity))

    def record_price(self, node_type: NodeType, price: Decimal):
        """Record a price point for history"""
        self._price_history[node_type].append((datetime.now(), price))
        # Keep last 1000 points
        if len(self._price_history[node_type]) > 1000:
            self._price_history[node_type] = self._price_history[node_type][-1000:]

    def get_price_history(
        self,
        node_type: NodeType,
        hours: int = 24
    ) -> List[Tuple[datetime, Decimal]]:
        """Get price history"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            (ts, p) for ts, p in self._price_history[node_type]
            if ts > cutoff
        ]

    def calculate_vwap(self, node_type: NodeType, hours: int = 1) -> Decimal:
        """Calculate Volume-Weighted Average Price"""
        # Simplified - would need volume data
        history = self.get_price_history(node_type, hours)
        if not history:
            return self.BASE_PRICES.get(node_type, Decimal("0.10"))

        prices = [p for _, p in history]
        return sum(prices) / len(prices)


# =============================================================================
# MARKETPLACE ENGINE
# =============================================================================

class Marketplace:
    """
    Main marketplace engine - orchestrates all components.

    Usage:
        marketplace = Marketplace()

        # Register a node
        node = marketplace.register_node(
            owner_id="user1",
            spec=NodeSpec(
                node_type=NodeType.COMPUTE,
                capacity=8,
                location="us-east",
                availability=0.99,
                latency_ms=50,
            ),
            stake=Decimal("500"),
        )

        # Place orders
        buy = marketplace.buy(
            owner_id="user2",
            node_type=NodeType.COMPUTE,
            quantity=4,
            price=Decimal("0.15"),
            duration_hours=24,
        )

        sell = marketplace.sell(
            owner_id="user1",
            node_type=NodeType.COMPUTE,
            quantity=8,
            price=Decimal("0.10"),
        )

        # Match and execute
        matches = marketplace.match_all()
    """

    BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗       ║
║   ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝       ║
║   ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║          ║
║   ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║          ║
║   ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║          ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝          ║
║                                                               ║
║              Node Marketplace - 0RB_AETHER Economy            ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
"""

    def __init__(self):
        self.registry = NodeRegistry()
        self.order_book = OrderBook()
        self.tx_engine = TransactionEngine(self.registry)
        self.pricing = PricingEngine(self.order_book)

    # -------------------------------------------------------------------------
    # Node Operations
    # -------------------------------------------------------------------------

    def register_node(
        self,
        owner_id: str,
        spec: NodeSpec,
        stake: Decimal
    ) -> Node:
        """Register a new node"""
        return self.registry.register(owner_id, spec, stake)

    def unregister_node(self, node_id: str) -> Optional[Decimal]:
        """Unregister a node and return stake"""
        return self.registry.unregister(node_id)

    def find_nodes(self, **kwargs) -> List[Node]:
        """Find nodes matching criteria"""
        return self.registry.find(**kwargs)

    def update_node_status(self, node_id: str, status: str):
        """Update node status"""
        self.registry.update_status(node_id, status)

    # -------------------------------------------------------------------------
    # Order Operations
    # -------------------------------------------------------------------------

    def buy(
        self,
        owner_id: str,
        node_type: NodeType,
        quantity: float,
        price: Decimal = None,
        duration_hours: int = 1,
        requirements: Dict[str, Any] = None
    ) -> Order:
        """Place a buy order"""
        if price is None:
            price = self.pricing.get_spot_price(node_type)

        return self.order_book.place_order(
            order_type=OrderType.BUY,
            node_type=node_type,
            owner_id=owner_id,
            quantity=quantity,
            price=price,
            duration_hours=duration_hours,
            requirements=requirements,
        )

    def sell(
        self,
        owner_id: str,
        node_type: NodeType,
        quantity: float,
        price: Decimal = None,
        requirements: Dict[str, Any] = None
    ) -> Order:
        """Place a sell order"""
        if price is None:
            price = self.pricing.get_spot_price(node_type)

        return self.order_book.place_order(
            order_type=OrderType.SELL,
            node_type=node_type,
            owner_id=owner_id,
            quantity=quantity,
            price=price,
            requirements=requirements,
        )

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        return self.order_book.cancel_order(order_id)

    def get_spread(self, node_type: NodeType) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Get best bid/ask spread"""
        return self.order_book.get_spread(node_type)

    def get_depth(self, node_type: NodeType, levels: int = 10) -> Dict[str, List]:
        """Get order book depth"""
        return self.order_book.get_depth(node_type, levels)

    # -------------------------------------------------------------------------
    # Matching & Settlement
    # -------------------------------------------------------------------------

    def match_all(self) -> List[Transaction]:
        """Match orders for all node types"""
        all_transactions = []

        for node_type in NodeType:
            matches = self.order_book.match_orders(node_type)

            for buy_order, sell_order, quantity, price in matches:
                # Find a suitable node
                nodes = self.registry.find(
                    node_type=node_type,
                    min_capacity=quantity,
                    status="online",
                )

                if not nodes:
                    continue

                # Use best rated node
                node = nodes[0]

                # Create and start transaction
                tx = self.tx_engine.create_transaction(
                    buy_order=buy_order,
                    sell_order=sell_order,
                    node_id=node.id,
                    quantity=quantity,
                    price=price,
                )

                self.tx_engine.start_transaction(tx.id)

                # Record price
                self.pricing.record_price(node_type, price)

                all_transactions.append(tx)

        return all_transactions

    # -------------------------------------------------------------------------
    # Market Data
    # -------------------------------------------------------------------------

    def get_price(self, node_type: NodeType) -> Decimal:
        """Get current spot price"""
        return self.pricing.get_spot_price(node_type)

    def get_price_for_quantity(
        self,
        node_type: NodeType,
        quantity: float,
        side: str = "buy"
    ) -> Decimal:
        """Get execution price for a quantity"""
        order_type = OrderType.BUY if side == "buy" else OrderType.SELL
        return self.pricing.get_price_for_quantity(node_type, quantity, order_type)

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        return {
            "nodes": self.registry.stats(),
            "transactions": self.tx_engine.stats(),
            "prices": {
                t.value: float(self.pricing.get_spot_price(t))
                for t in NodeType
            },
        }


# =============================================================================
# CLI
# =============================================================================

async def demo():
    """Run marketplace demo"""
    print(Marketplace.BANNER)

    marketplace = Marketplace()

    print("\n[1] Registering Nodes...")

    # Register some nodes
    node1 = marketplace.register_node(
        owner_id="provider1",
        spec=NodeSpec(
            node_type=NodeType.COMPUTE,
            capacity=16,
            location="us-east",
            availability=0.99,
            latency_ms=25,
            certifications=["SOC2"],
        ),
        stake=Decimal("500"),
    )
    print(f"    Registered compute node: {node1.id}")

    node2 = marketplace.register_node(
        owner_id="provider2",
        spec=NodeSpec(
            node_type=NodeType.STORAGE,
            capacity=1000,
            location="eu-west",
            availability=0.999,
            latency_ms=50,
        ),
        stake=Decimal("200"),
    )
    print(f"    Registered storage node: {node2.id}")

    # Set nodes online
    marketplace.update_node_status(node1.id, "online")
    marketplace.update_node_status(node2.id, "online")

    print("\n[2] Placing Orders...")

    # Place orders
    buy1 = marketplace.buy(
        owner_id="user1",
        node_type=NodeType.COMPUTE,
        quantity=4,
        price=Decimal("0.15"),
        duration_hours=2,
    )
    print(f"    Buy order: {buy1.id} - {buy1.quantity} compute @ {buy1.price}")

    sell1 = marketplace.sell(
        owner_id="provider1",
        node_type=NodeType.COMPUTE,
        quantity=8,
        price=Decimal("0.12"),
    )
    print(f"    Sell order: {sell1.id} - {sell1.quantity} compute @ {sell1.price}")

    print("\n[3] Order Book Depth...")
    depth = marketplace.get_depth(NodeType.COMPUTE)
    print(f"    Bids: {depth['bids']}")
    print(f"    Asks: {depth['asks']}")

    print("\n[4] Matching Orders...")
    transactions = marketplace.match_all()
    for tx in transactions:
        print(f"    Transaction: {tx.id}")
        print(f"      Buyer: {tx.buyer_id} -> Seller: {tx.seller_id}")
        print(f"      Quantity: {tx.quantity} @ {tx.price}/hr")
        print(f"      Total: {tx.total_cost} (fee: {tx.fee})")

    print("\n[5] Market Statistics...")
    stats = marketplace.stats()
    print(f"    Nodes: {stats['nodes']['total_nodes']} total, {stats['nodes']['online_nodes']} online")
    print(f"    Transactions: {stats['transactions']['total_transactions']}")
    print(f"    Compute price: ${stats['prices']['compute']:.4f}/hr")

    print("\n" + "=" * 50)
    print("MARKETPLACE DEMO COMPLETE")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
