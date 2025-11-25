#!/usr/bin/env python3
"""
Marketplace Tests
"""
import pytest
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from marketplace import (
    Marketplace,
    NodeRegistry,
    NodeSpec,
    NodeType,
    Node,
    OrderBook,
    Order,
    OrderType,
    OrderStatus,
    TransactionEngine,
    TransactionStatus,
    PricingEngine,
)
from marketplace.reputation import (
    ReputationEngine,
    ReputationFactor,
    TrustScorer,
)


# =============================================================================
# NODE REGISTRY TESTS
# =============================================================================

class TestNodeRegistry:
    @pytest.fixture
    def registry(self):
        return NodeRegistry()

    @pytest.fixture
    def compute_spec(self):
        return NodeSpec(
            node_type=NodeType.COMPUTE,
            capacity=8,
            location="us-east",
            availability=0.99,
            latency_ms=25,
        )

    def test_register_node(self, registry, compute_spec):
        """Test node registration"""
        node = registry.register("owner1", compute_spec, Decimal("500"))
        assert node.id is not None
        assert node.owner_id == "owner1"
        assert node.spec.node_type == NodeType.COMPUTE
        assert node.stake_amount == Decimal("500")

    def test_register_insufficient_stake(self, registry, compute_spec):
        """Test registration with insufficient stake"""
        with pytest.raises(ValueError, match="Minimum stake"):
            registry.register("owner1", compute_spec, Decimal("10"))

    def test_find_nodes(self, registry, compute_spec):
        """Test finding nodes"""
        node = registry.register("owner1", compute_spec, Decimal("500"))
        registry.update_status(node.id, "online")

        found = registry.find(node_type=NodeType.COMPUTE, status="online")
        assert len(found) == 1
        assert found[0].id == node.id

    def test_find_with_capacity(self, registry, compute_spec):
        """Test finding nodes with capacity requirement"""
        node = registry.register("owner1", compute_spec, Decimal("500"))
        registry.update_status(node.id, "online")

        # Should find - capacity is 8
        found = registry.find(min_capacity=4)
        assert len(found) == 1

        # Should not find - needs more capacity
        found = registry.find(min_capacity=16)
        assert len(found) == 0

    def test_unregister_node(self, registry, compute_spec):
        """Test node unregistration"""
        node = registry.register("owner1", compute_spec, Decimal("500"))
        stake = registry.unregister(node.id)
        assert stake == Decimal("500")
        assert registry.get(node.id) is None

    def test_unregister_busy_node(self, registry, compute_spec):
        """Test cannot unregister busy node"""
        node = registry.register("owner1", compute_spec, Decimal("500"))
        registry.update_status(node.id, "busy")

        with pytest.raises(ValueError, match="busy"):
            registry.unregister(node.id)


# =============================================================================
# ORDER BOOK TESTS
# =============================================================================

class TestOrderBook:
    @pytest.fixture
    def order_book(self):
        return OrderBook()

    def test_place_buy_order(self, order_book):
        """Test placing buy order"""
        order = order_book.place_order(
            order_type=OrderType.BUY,
            node_type=NodeType.COMPUTE,
            owner_id="buyer1",
            quantity=4,
            price=Decimal("0.15"),
            duration_hours=2,
        )
        assert order.id is not None
        assert order.order_type == OrderType.BUY
        assert order.status == OrderStatus.ACTIVE

    def test_place_sell_order(self, order_book):
        """Test placing sell order"""
        order = order_book.place_order(
            order_type=OrderType.SELL,
            node_type=NodeType.COMPUTE,
            owner_id="seller1",
            quantity=8,
            price=Decimal("0.12"),
        )
        assert order.order_type == OrderType.SELL

    def test_cancel_order(self, order_book):
        """Test order cancellation"""
        order = order_book.place_order(
            order_type=OrderType.BUY,
            node_type=NodeType.COMPUTE,
            owner_id="buyer1",
            quantity=4,
            price=Decimal("0.15"),
        )
        result = order_book.cancel_order(order.id)
        assert result is True
        assert order.status == OrderStatus.CANCELLED

    def test_get_spread(self, order_book):
        """Test getting bid/ask spread"""
        order_book.place_order(
            order_type=OrderType.BUY,
            node_type=NodeType.COMPUTE,
            owner_id="buyer1",
            quantity=4,
            price=Decimal("0.12"),
        )
        order_book.place_order(
            order_type=OrderType.SELL,
            node_type=NodeType.COMPUTE,
            owner_id="seller1",
            quantity=4,
            price=Decimal("0.15"),
        )

        bid, ask = order_book.get_spread(NodeType.COMPUTE)
        assert bid == Decimal("0.12")
        assert ask == Decimal("0.15")

    def test_match_orders(self, order_book):
        """Test order matching"""
        # Buy at 0.15
        order_book.place_order(
            order_type=OrderType.BUY,
            node_type=NodeType.COMPUTE,
            owner_id="buyer1",
            quantity=4,
            price=Decimal("0.15"),
            duration_hours=1,
        )
        # Sell at 0.12 (crosses the buy)
        order_book.place_order(
            order_type=OrderType.SELL,
            node_type=NodeType.COMPUTE,
            owner_id="seller1",
            quantity=4,
            price=Decimal("0.12"),
        )

        matches = order_book.match_orders(NodeType.COMPUTE)
        assert len(matches) == 1

        buy_order, sell_order, quantity, price = matches[0]
        assert quantity == 4
        assert price == Decimal("0.135")  # Midpoint

    def test_partial_fill(self, order_book):
        """Test partial order fill"""
        # Large buy
        buy = order_book.place_order(
            order_type=OrderType.BUY,
            node_type=NodeType.COMPUTE,
            owner_id="buyer1",
            quantity=10,
            price=Decimal("0.15"),
            duration_hours=1,
        )
        # Smaller sell
        order_book.place_order(
            order_type=OrderType.SELL,
            node_type=NodeType.COMPUTE,
            owner_id="seller1",
            quantity=4,
            price=Decimal("0.12"),
        )

        matches = order_book.match_orders(NodeType.COMPUTE)
        assert len(matches) == 1

        assert buy.status == OrderStatus.PARTIAL
        assert buy.filled_quantity == 4


# =============================================================================
# TRANSACTION TESTS
# =============================================================================

class TestTransactions:
    @pytest.fixture
    def marketplace(self):
        return Marketplace()

    def test_create_transaction(self, marketplace):
        """Test transaction creation"""
        # Register node
        spec = NodeSpec(
            node_type=NodeType.COMPUTE,
            capacity=8,
            location="us-east",
            availability=0.99,
            latency_ms=25,
        )
        node = marketplace.register_node("seller1", spec, Decimal("500"))
        marketplace.update_node_status(node.id, "online")

        # Place orders
        buy = marketplace.buy(
            owner_id="buyer1",
            node_type=NodeType.COMPUTE,
            quantity=4,
            price=Decimal("0.15"),
            duration_hours=2,
        )
        marketplace.sell(
            owner_id="seller1",
            node_type=NodeType.COMPUTE,
            quantity=8,
            price=Decimal("0.12"),
        )

        # Match
        transactions = marketplace.match_all()
        assert len(transactions) == 1

        tx = transactions[0]
        assert tx.buyer_id == "buyer1"
        assert tx.seller_id == "seller1"
        assert tx.quantity == 4
        assert tx.fee > 0

    def test_transaction_fee_calculation(self, marketplace):
        """Test that fees are calculated correctly"""
        spec = NodeSpec(
            node_type=NodeType.COMPUTE,
            capacity=8,
            location="us-east",
            availability=0.99,
            latency_ms=25,
        )
        node = marketplace.register_node("seller1", spec, Decimal("500"))
        marketplace.update_node_status(node.id, "online")

        marketplace.buy("buyer1", NodeType.COMPUTE, 1, Decimal("1.00"), 1)
        marketplace.sell("seller1", NodeType.COMPUTE, 1, Decimal("1.00"))

        transactions = marketplace.match_all()
        tx = transactions[0]

        # 2.5% fee on total cost
        expected_fee = tx.total_cost * Decimal("0.025")
        assert tx.fee == expected_fee.quantize(Decimal("0.0001"))


# =============================================================================
# PRICING TESTS
# =============================================================================

class TestPricing:
    @pytest.fixture
    def marketplace(self):
        return Marketplace()

    def test_spot_price_with_no_orders(self, marketplace):
        """Test spot price falls back to base"""
        price = marketplace.get_price(NodeType.COMPUTE)
        assert price == Decimal("0.10")  # Base price

    def test_spot_price_with_orders(self, marketplace):
        """Test spot price from order book"""
        marketplace.order_book.place_order(
            order_type=OrderType.BUY,
            node_type=NodeType.COMPUTE,
            owner_id="buyer1",
            quantity=4,
            price=Decimal("0.12"),
        )
        marketplace.order_book.place_order(
            order_type=OrderType.SELL,
            node_type=NodeType.COMPUTE,
            owner_id="seller1",
            quantity=4,
            price=Decimal("0.14"),
        )

        price = marketplace.get_price(NodeType.COMPUTE)
        assert price == Decimal("0.13")  # Midpoint


# =============================================================================
# REPUTATION TESTS
# =============================================================================

class TestReputation:
    @pytest.fixture
    def engine(self):
        return ReputationEngine()

    def test_record_event(self, engine):
        """Test recording reputation event"""
        event = engine.record_event(
            "entity1",
            ReputationFactor.JOB_SUCCESS,
            1.0,
        )
        assert event.id is not None
        assert event.factor == ReputationFactor.JOB_SUCCESS

    def test_calculate_score(self, engine):
        """Test score calculation"""
        entity = "provider1"

        # Add some success events
        for _ in range(90):
            engine.record_event(entity, ReputationFactor.JOB_SUCCESS, 1.0)
        for _ in range(10):
            engine.record_event(entity, ReputationFactor.JOB_FAILURE, 1.0)

        # Add ratings
        for _ in range(20):
            engine.record_event(entity, ReputationFactor.RATING, 4.5)

        score = engine.calculate_score(entity)
        assert score.overall > 0
        assert score.tier in ["bronze", "silver", "gold", "platinum", "diamond"]
        assert score.components["success_rate"] == 90.0

    def test_badges(self, engine):
        """Test badge earning"""
        entity = "achiever"

        # First job badge
        engine.record_event(entity, ReputationFactor.JOB_SUCCESS, 1.0)
        score = engine.calculate_score(entity)
        assert "first_job" in score.badges

        # Add more for 100 jobs badge
        for _ in range(99):
            engine.record_event(entity, ReputationFactor.JOB_SUCCESS, 1.0)

        score = engine.calculate_score(entity, force_recalculate=True)
        assert "hundred_jobs" in score.badges


class TestTrust:
    @pytest.fixture
    def trust_scorer(self):
        engine = ReputationEngine()
        return TrustScorer(engine)

    def test_trust_calculation(self, trust_scorer):
        """Test trust score calculation"""
        # Build some reputation
        engine = trust_scorer._reputation
        engine.record_event("buyer", ReputationFactor.JOB_SUCCESS, 1.0)
        engine.record_event("seller", ReputationFactor.JOB_SUCCESS, 1.0)

        trust = trust_scorer.calculate_trust("buyer", "seller", 100)

        assert "trust_score" in trust
        assert trust["trust_score"] >= 0
        assert trust["recommendation"] in [
            "highly_trusted", "trusted", "neutral", "caution", "high_risk"
        ]


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestMarketplaceIntegration:
    def test_full_flow(self):
        """Test complete marketplace flow"""
        marketplace = Marketplace()

        # 1. Register provider node
        spec = NodeSpec(
            node_type=NodeType.COMPUTE,
            capacity=16,
            location="us-east",
            availability=0.99,
            latency_ms=25,
            certifications=["SOC2"],
        )
        node = marketplace.register_node("provider", spec, Decimal("1000"))
        marketplace.update_node_status(node.id, "online")

        # 2. Buyer places order
        buy_order = marketplace.buy(
            owner_id="buyer",
            node_type=NodeType.COMPUTE,
            quantity=8,
            price=Decimal("0.20"),
            duration_hours=4,
        )

        # 3. Provider places sell order
        sell_order = marketplace.sell(
            owner_id="provider",
            node_type=NodeType.COMPUTE,
            quantity=16,
            price=Decimal("0.15"),
        )

        # 4. Match and execute
        transactions = marketplace.match_all()
        assert len(transactions) == 1

        tx = transactions[0]
        assert tx.status == TransactionStatus.CONFIRMED
        assert tx.quantity == 8

        # 5. Complete transaction
        marketplace.tx_engine.complete_transaction(tx.id)

        # 6. Rate transaction
        marketplace.tx_engine.rate_transaction(tx.id, "buyer", 5.0)

        # 7. Check stats
        stats = marketplace.stats()
        assert stats["transactions"]["total_transactions"] == 1
        assert stats["nodes"]["total_nodes"] == 1


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
