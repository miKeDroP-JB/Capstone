#!/usr/bin/env python3
"""
FlowSync SDK Tests
Comprehensive test suite for the SDK
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flowsync import (
    FlowSync,
    FlowSyncConfig,
    Agent,
    AgentAPI,
    AgentCapability,
    Workflow,
    WorkflowAPI,
    Step,
    StepType,
    ComplianceAPI,
    ComplianceFramework,
    EconomyAPI,
    TokenType,
    quick_start,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def config():
    """Test configuration"""
    return FlowSyncConfig(
        api_key="test-key",
        api_secret="test-secret",
        endpoint="http://localhost:8080",
        network="testnet",
        debug=False,
    )


@pytest.fixture
def client(config):
    """Test client"""
    return FlowSync(config=config)


# =============================================================================
# CONFIG TESTS
# =============================================================================

class TestConfig:
    def test_default_config(self):
        """Test default configuration"""
        config = FlowSyncConfig()
        assert config.endpoint == "http://localhost:8080"
        assert config.network == "testnet"
        assert config.timeout == 30
        assert config.retry_count == 3

    def test_custom_config(self):
        """Test custom configuration"""
        config = FlowSyncConfig(
            api_key="my-key",
            endpoint="https://api.flowsync.io",
            network="mainnet",
        )
        assert config.api_key == "my-key"
        assert config.endpoint == "https://api.flowsync.io"
        assert config.network == "mainnet"


# =============================================================================
# CLIENT TESTS
# =============================================================================

class TestClient:
    def test_client_init(self, config):
        """Test client initialization"""
        client = FlowSync(config=config)
        assert client.config == config
        assert client._session_id is not None
        assert not client._connected

    def test_client_with_api_key(self):
        """Test client with API key only"""
        client = FlowSync(api_key="simple-key")
        assert client.config.api_key == "simple-key"

    @pytest.mark.asyncio
    async def test_connect(self, client):
        """Test client connection"""
        result = await client.connect()
        assert result is True
        assert client._connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """Test client disconnection"""
        await client.connect()
        await client.disconnect()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_context_manager(self, config):
        """Test async context manager"""
        async with FlowSync(config=config) as client:
            assert client._connected is True
        assert client._connected is False

    def test_sign_request(self, client):
        """Test request signing"""
        data = {"action": "test", "value": 123}
        signature = client.sign_request(data)
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex


# =============================================================================
# AGENT TESTS
# =============================================================================

class TestAgents:
    @pytest.mark.asyncio
    async def test_create_agent(self, client):
        """Test agent creation"""
        agent = await client.agents.create(
            name="test-agent",
            capabilities=["nlp", "code-gen"],
        )
        assert agent.name == "test-agent"
        assert AgentCapability.NLP in agent.capabilities
        assert AgentCapability.CODE_GEN in agent.capabilities
        assert agent.id is not None

    @pytest.mark.asyncio
    async def test_agent_with_memory(self, client):
        """Test agent with memory"""
        agent = await client.agents.create(
            name="memory-agent",
            memory=True,
        )
        assert agent.memory_id is not None
        assert agent.memory_id.startswith("mem_")

    @pytest.mark.asyncio
    async def test_agent_without_memory(self, client):
        """Test agent without memory"""
        agent = await client.agents.create(
            name="no-memory-agent",
            memory=False,
        )
        assert agent.memory_id is None

    @pytest.mark.asyncio
    async def test_agent_execute(self, client):
        """Test agent task execution"""
        agent = await client.agents.create(
            name="exec-agent",
            capabilities=["nlp"],
        )
        result = await agent.execute("Process this text")
        assert result["success"] is True
        assert result["agent_id"] == agent.id
        assert result["execution_time"] >= 0

    @pytest.mark.asyncio
    async def test_list_agents(self, client):
        """Test listing agents"""
        await client.agents.create(name="agent-1")
        await client.agents.create(name="agent-2")
        agents = await client.agents.list()
        assert len(agents) >= 2

    @pytest.mark.asyncio
    async def test_get_agent(self, client):
        """Test getting agent by ID"""
        created = await client.agents.create(name="get-test")
        retrieved = await client.agents.get(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    @pytest.mark.asyncio
    async def test_delete_agent(self, client):
        """Test agent deletion"""
        agent = await client.agents.create(name="delete-me")
        result = await client.agents.delete(agent.id)
        assert result is True
        retrieved = await client.agents.get(agent.id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_clone_agent(self, client):
        """Test agent cloning"""
        original = await client.agents.create(
            name="original",
            capabilities=["nlp", "reasoning"],
            metadata={"key": "value"},
        )
        clone = await client.agents.clone(original.id, "cloned")
        assert clone.name == "cloned"
        assert clone.capabilities == original.capabilities
        assert clone.id != original.id


# =============================================================================
# WORKFLOW TESTS
# =============================================================================

class TestWorkflows:
    @pytest.mark.asyncio
    async def test_create_workflow(self, client):
        """Test workflow creation"""
        workflow = await client.workflows.create(
            name="test-workflow",
            description="A test workflow",
            steps=[
                {"name": "step1", "action": "action1", "output": "result1"},
                {"name": "step2", "action": "action2", "input": "$result1"},
            ],
        )
        assert workflow.name == "test-workflow"
        assert len(workflow.steps) == 2
        assert workflow.id is not None

    @pytest.mark.asyncio
    async def test_workflow_with_step_objects(self, client):
        """Test workflow with Step objects"""
        workflow = await client.workflows.create(
            name="step-object-workflow",
            steps=[
                Step(name="analyze", type=StepType.ACTION, action="analyze"),
                Step(name="generate", type=StepType.ACTION, action="generate"),
            ],
        )
        assert len(workflow.steps) == 2
        assert workflow.steps[0].name == "analyze"

    @pytest.mark.asyncio
    async def test_run_workflow(self, client):
        """Test workflow execution"""
        workflow = await client.workflows.create(
            name="run-test",
            steps=[
                {"name": "step1", "action": "test", "output": "out1"},
            ],
        )
        run = await workflow.run(input_data="test")
        assert run.status == "completed"
        assert run.workflow_id == workflow.id
        assert len(run.step_results) == 1

    @pytest.mark.asyncio
    async def test_workflow_condition(self, client):
        """Test workflow with condition"""
        workflow = await client.workflows.create(
            name="condition-test",
            steps=[
                {"name": "check", "type": "condition", "condition": "True"},
            ],
        )
        run = await workflow.run()
        assert run.status == "completed"

    @pytest.mark.asyncio
    async def test_list_workflows(self, client):
        """Test listing workflows"""
        await client.workflows.create(name="wf-1", steps=[])
        await client.workflows.create(name="wf-2", steps=[])
        workflows = await client.workflows.list()
        assert len(workflows) >= 2


# =============================================================================
# COMPLIANCE TESTS
# =============================================================================

class TestCompliance:
    @pytest.mark.asyncio
    async def test_compliance_check_gdpr(self, client):
        """Test GDPR compliance check"""
        report = await client.compliance.check(
            target="test-system",
            frameworks=[ComplianceFramework.GDPR],
            evidence={"gdpr-1": True, "gdpr-2": True},
        )
        assert report.target == "test-system"
        assert ComplianceFramework.GDPR in report.frameworks
        assert report.score >= 0
        assert report.overall_status in ["compliant", "partial", "non_compliant"]

    @pytest.mark.asyncio
    async def test_compliance_check_multiple_frameworks(self, client):
        """Test compliance check with multiple frameworks"""
        report = await client.compliance.check(
            target="multi-test",
            frameworks=[ComplianceFramework.GDPR, ComplianceFramework.HIPAA],
        )
        assert len(report.frameworks) == 2
        assert len(report.checks) > 0

    @pytest.mark.asyncio
    async def test_compliance_with_evidence(self, client):
        """Test compliance with full evidence"""
        report = await client.compliance.check(
            target="full-evidence",
            frameworks=[ComplianceFramework.GDPR],
            evidence={
                "gdpr-1": True,
                "gdpr-2": True,
                "gdpr-3": True,
                "gdpr-4": True,
            },
        )
        assert report.score == 100.0
        assert report.overall_status == "compliant"

    def test_get_requirements(self, client):
        """Test getting framework requirements"""
        reqs = client.compliance.get_requirements(ComplianceFramework.GDPR)
        assert len(reqs) > 0
        assert all("requirement" in r for r in reqs)


# =============================================================================
# ECONOMY TESTS
# =============================================================================

class TestEconomy:
    @pytest.mark.asyncio
    async def test_create_wallet(self, client):
        """Test wallet creation"""
        wallet = await client.economy.create_wallet("user1")
        assert wallet.owner == "user1"
        assert wallet.id is not None
        assert wallet.balance(TokenType.ORB) == 0

    @pytest.mark.asyncio
    async def test_wallet_balance(self, client):
        """Test wallet balance"""
        wallet = await client.economy.create_wallet("balance-test")
        wallet.balances[TokenType.ORB] = 1000
        assert wallet.balance(TokenType.ORB) == 1000
        assert wallet.balance(TokenType.COMPUTE) == 0

    @pytest.mark.asyncio
    async def test_transfer(self, client):
        """Test token transfer"""
        wallet1 = await client.economy.create_wallet("sender")
        wallet2 = await client.economy.create_wallet("receiver")

        wallet1.balances[TokenType.ORB] = 1000

        tx = await client.economy.transfer(
            wallet1.id, wallet2.id, TokenType.ORB, 100
        )

        assert tx.status == "confirmed"
        assert tx.amount == 100
        assert tx.fee > 0
        assert wallet2.balance(TokenType.ORB) == 100

    @pytest.mark.asyncio
    async def test_transfer_insufficient_balance(self, client):
        """Test transfer with insufficient balance"""
        wallet1 = await client.economy.create_wallet("poor")
        wallet2 = await client.economy.create_wallet("rich")

        with pytest.raises(ValueError, match="Insufficient balance"):
            await client.economy.transfer(
                wallet1.id, wallet2.id, TokenType.ORB, 1000
            )

    @pytest.mark.asyncio
    async def test_stake(self, client):
        """Test staking"""
        wallet = await client.economy.create_wallet("staker")
        wallet.balances[TokenType.ORB] = 5000

        stake = await client.economy.stake(wallet.id, 1000, "compute", 30)

        assert stake.amount == 1000
        assert stake.node_type == "compute"
        assert wallet.balance(TokenType.ORB) == 4000

    @pytest.mark.asyncio
    async def test_get_price(self, client):
        """Test token price"""
        price = await client.economy.get_price(TokenType.ORB)
        assert price > 0

    @pytest.mark.asyncio
    async def test_purchase_credits(self, client):
        """Test purchasing credits"""
        wallet = await client.economy.create_wallet("buyer")
        wallet.balances[TokenType.ORB] = 100

        tx = await client.economy.purchase_credits(
            wallet.id, TokenType.COMPUTE, 10
        )

        assert tx.status == "confirmed"
        assert wallet.balance(TokenType.COMPUTE) == 10

    def test_economy_stats(self, client):
        """Test economy statistics"""
        stats = client.economy.get_stats()
        assert "total_wallets" in stats
        assert "total_staked" in stats


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_workflow(self, client):
        """Test complete workflow with agent"""
        await client.connect()

        # Create agent
        agent = await client.agents.create(
            name="workflow-agent",
            capabilities=["nlp"],
        )

        # Create workflow using agent
        workflow = await client.workflows.create(
            name="agent-workflow",
            steps=[
                {"name": "process", "type": "agent_call", "agent_id": agent.id},
            ],
        )

        # Run workflow
        run = await workflow.run()
        assert run.status == "completed"

        await client.disconnect()

    @pytest.mark.asyncio
    async def test_compliance_and_economy(self, client):
        """Test compliance check with economic implications"""
        # Create wallet
        wallet = await client.economy.create_wallet("compliant-user")
        wallet.balances[TokenType.ORB] = 1000

        # Run compliance check
        report = await client.compliance.check(
            target=wallet.id,
            frameworks=[ComplianceFramework.GDPR],
            evidence={"gdpr-1": True, "gdpr-2": True},
        )

        assert report.score > 0
        # In a real system, compliance might affect staking eligibility


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
