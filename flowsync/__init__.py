#!/usr/bin/env python3
"""
FLOWSYNC SDK - The Developer Moat
Your gateway to the 0RB_AETHER ecosystem.

This is the "iOS SDK" equivalent - the toolkit that makes
developers WANT to build on our platform.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac

# Version
__version__ = "0.1.0"
__author__ = "0RB_AETHER"


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class FlowSyncConfig:
    """SDK Configuration"""
    api_key: str = ""
    api_secret: str = ""
    endpoint: str = "http://localhost:8080"
    network: str = "testnet"  # testnet, mainnet
    timeout: int = 30
    retry_count: int = 3
    debug: bool = False

    @classmethod
    def from_env(cls) -> "FlowSyncConfig":
        """Load config from environment variables"""
        return cls(
            api_key=os.getenv("FLOWSYNC_API_KEY", ""),
            api_secret=os.getenv("FLOWSYNC_API_SECRET", ""),
            endpoint=os.getenv("FLOWSYNC_ENDPOINT", "http://localhost:8080"),
            network=os.getenv("FLOWSYNC_NETWORK", "testnet"),
            debug=os.getenv("FLOWSYNC_DEBUG", "").lower() == "true",
        )


# =============================================================================
# CORE CLIENT
# =============================================================================

class FlowSync:
    """
    Main FlowSync SDK Client

    The single entry point for all 0RB_AETHER functionality.

    Usage:
        client = FlowSync(api_key="your-key")

        # Create an agent
        agent = await client.agents.create(
            name="my-agent",
            capabilities=["nlp", "code-gen"]
        )

        # Define a workflow
        workflow = await client.workflows.create(
            name="my-workflow",
            steps=[
                Step(action="analyze", input="$user_query"),
                Step(action="generate", input="$analysis_result"),
            ]
        )

        # Run it
        result = await workflow.run(user_query="Build me a dashboard")
    """

    BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗██╗      ██████╗ ██╗    ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗ ║
║   ██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝ ║
║   █████╗  ██║     ██║   ██║██║ █╗ ██║███████╗ ╚████╔╝ ██╔██╗ ██║██║      ║
║   ██╔══╝  ██║     ██║   ██║██║███╗██║╚════██║  ╚██╔╝  ██║╚██╗██║██║      ║
║   ██║     ███████╗╚██████╔╝╚███╔███╔╝███████║   ██║   ██║ ╚████║╚██████╗ ║
║   ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ║
║                                                               ║
║                  SDK v{version} - Developer Moat                ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
"""

    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        config: FlowSyncConfig = None
    ):
        self.config = config or FlowSyncConfig.from_env()
        if api_key:
            self.config.api_key = api_key
        if api_secret:
            self.config.api_secret = api_secret

        # Initialize sub-modules
        self._agents = AgentAPI(self)
        self._workflows = WorkflowAPI(self)
        self._compliance = ComplianceAPI(self)
        self._economy = EconomyAPI(self)

        # Session tracking
        self._session_id = self._generate_session_id()
        self._connected = False

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        data = f"{datetime.now().isoformat()}-{self.config.api_key}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    @property
    def agents(self) -> "AgentAPI":
        """Access Agent API"""
        return self._agents

    @property
    def workflows(self) -> "WorkflowAPI":
        """Access Workflow API"""
        return self._workflows

    @property
    def compliance(self) -> "ComplianceAPI":
        """Access Compliance API"""
        return self._compliance

    @property
    def economy(self) -> "EconomyAPI":
        """Access Economy API"""
        return self._economy

    async def connect(self) -> bool:
        """Connect to FlowSync network"""
        if self.config.debug:
            print(self.BANNER.format(version=__version__))

        # Verify credentials
        if not self.config.api_key:
            raise ValueError("API key required. Set FLOWSYNC_API_KEY or pass api_key")

        # TODO: Real connection to network
        self._connected = True
        return True

    async def disconnect(self):
        """Disconnect from network"""
        self._connected = False

    def sign_request(self, data: Dict[str, Any]) -> str:
        """Sign API request for authentication"""
        payload = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            self.config.api_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


# =============================================================================
# AGENT API
# =============================================================================

class AgentCapability(Enum):
    """Agent capabilities"""
    NLP = "nlp"
    CODE_GEN = "code-gen"
    DATA_ANALYSIS = "data-analysis"
    WEB_SEARCH = "web-search"
    FILE_OPS = "file-ops"
    API_CALLS = "api-calls"
    REASONING = "reasoning"
    MEMORY = "memory"
    VISION = "vision"
    AUDIO = "audio"


@dataclass
class Agent:
    """An AI Agent instance"""
    id: str
    name: str
    capabilities: List[AgentCapability]
    status: str = "idle"
    memory_id: str = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Runtime state
    _client: "FlowSync" = field(default=None, repr=False)
    _task_count: int = field(default=0, repr=False)

    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task"""
        self._task_count += 1

        result = {
            "agent_id": self.id,
            "task": task,
            "context": context or {},
            "result": None,
            "success": False,
            "execution_time": 0,
        }

        start = datetime.now()

        try:
            # Route to capability-specific handlers
            if AgentCapability.CODE_GEN in self.capabilities:
                result["result"] = await self._handle_code_gen(task, context)
            elif AgentCapability.DATA_ANALYSIS in self.capabilities:
                result["result"] = await self._handle_data_analysis(task, context)
            else:
                result["result"] = await self._handle_generic(task, context)

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        result["execution_time"] = (datetime.now() - start).total_seconds()
        return result

    async def _handle_code_gen(self, task: str, context: Dict) -> str:
        """Handle code generation tasks"""
        # Would connect to AGI kernel
        return f"# Generated code for: {task}\npass"

    async def _handle_data_analysis(self, task: str, context: Dict) -> Dict:
        """Handle data analysis tasks"""
        return {"analysis": task, "insights": []}

    async def _handle_generic(self, task: str, context: Dict) -> str:
        """Handle generic tasks"""
        return f"Processed: {task}"

    async def remember(self, key: str, value: Any):
        """Store in agent memory"""
        if self.memory_id and self._client:
            # Would connect to memory system
            pass

    async def recall(self, key: str) -> Any:
        """Retrieve from agent memory"""
        if self.memory_id and self._client:
            # Would connect to memory system
            pass
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent"""
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "status": self.status,
            "memory_id": self.memory_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class AgentAPI:
    """
    Agent Management API

    Create, configure, and manage AI agents.
    """

    def __init__(self, client: FlowSync):
        self._client = client
        self._agents: Dict[str, Agent] = {}

    async def create(
        self,
        name: str,
        capabilities: List[Union[str, AgentCapability]] = None,
        memory: bool = True,
        metadata: Dict[str, Any] = None
    ) -> Agent:
        """
        Create a new agent

        Args:
            name: Agent name
            capabilities: List of capabilities (nlp, code-gen, etc.)
            memory: Enable persistent memory
            metadata: Additional metadata

        Returns:
            Agent instance
        """
        # Parse capabilities
        caps = []
        for cap in (capabilities or ["nlp"]):
            if isinstance(cap, str):
                caps.append(AgentCapability(cap))
            else:
                caps.append(cap)

        # Generate ID
        agent_id = hashlib.sha256(
            f"{name}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Create memory if requested
        memory_id = None
        if memory:
            memory_id = f"mem_{agent_id}"

        agent = Agent(
            id=agent_id,
            name=name,
            capabilities=caps,
            memory_id=memory_id,
            metadata=metadata or {},
            _client=self._client,
        )

        self._agents[agent_id] = agent
        return agent

    async def get(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self._agents.get(agent_id)

    async def list(self) -> List[Agent]:
        """List all agents"""
        return list(self._agents.values())

    async def delete(self, agent_id: str) -> bool:
        """Delete an agent"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    async def clone(self, agent_id: str, new_name: str) -> Optional[Agent]:
        """Clone an existing agent"""
        original = self._agents.get(agent_id)
        if not original:
            return None

        return await self.create(
            name=new_name,
            capabilities=[c.value for c in original.capabilities],
            memory=original.memory_id is not None,
            metadata=original.metadata.copy(),
        )


# =============================================================================
# WORKFLOW API
# =============================================================================

class StepType(Enum):
    """Workflow step types"""
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    AGENT_CALL = "agent_call"
    HUMAN_IN_LOOP = "human_in_loop"
    CHECKPOINT = "checkpoint"


@dataclass
class Step:
    """A workflow step"""
    name: str
    type: StepType = StepType.ACTION
    action: str = ""
    input: str = ""
    output: str = ""
    agent_id: str = None
    condition: str = None
    on_success: str = None
    on_failure: str = None
    timeout: int = 60
    retries: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowRun:
    """A workflow execution instance"""
    id: str
    workflow_id: str
    status: str  # pending, running, completed, failed
    current_step: int
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    started_at: datetime
    completed_at: datetime = None
    error: str = None
    step_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Workflow:
    """A workflow definition"""
    id: str
    name: str
    description: str
    steps: List[Step]
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Runtime
    _client: "FlowSync" = field(default=None, repr=False)
    _runs: List[WorkflowRun] = field(default_factory=list, repr=False)

    async def run(self, **inputs) -> WorkflowRun:
        """Execute the workflow"""
        run_id = hashlib.sha256(
            f"{self.id}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        run = WorkflowRun(
            id=run_id,
            workflow_id=self.id,
            status="running",
            current_step=0,
            inputs=inputs,
            outputs={},
            started_at=datetime.now(),
        )
        self._runs.append(run)

        context = inputs.copy()

        try:
            for i, step in enumerate(self.steps):
                run.current_step = i

                # Execute step
                step_result = await self._execute_step(step, context)
                run.step_results.append(step_result)

                # Update context with outputs
                if step.output:
                    context[step.output] = step_result.get("result")

                # Handle conditions
                if step.type == StepType.CONDITION:
                    if not step_result.get("passed"):
                        if step.on_failure:
                            # Jump to failure step
                            pass
                        else:
                            break

            run.status = "completed"
            run.outputs = context

        except Exception as e:
            run.status = "failed"
            run.error = str(e)

        run.completed_at = datetime.now()
        return run

    async def _execute_step(self, step: Step, context: Dict) -> Dict[str, Any]:
        """Execute a single step"""
        result = {
            "step": step.name,
            "type": step.type.value,
            "success": False,
            "result": None,
        }

        # Resolve input variables
        input_value = step.input
        if input_value.startswith("$"):
            var_name = input_value[1:]
            input_value = context.get(var_name, input_value)

        if step.type == StepType.ACTION:
            # Execute action
            result["result"] = f"Executed {step.action} with {input_value}"
            result["success"] = True

        elif step.type == StepType.AGENT_CALL:
            # Call agent
            if self._client and step.agent_id:
                agent = await self._client.agents.get(step.agent_id)
                if agent:
                    agent_result = await agent.execute(input_value, context)
                    result["result"] = agent_result.get("result")
                    result["success"] = agent_result.get("success", False)

        elif step.type == StepType.CONDITION:
            # Evaluate condition
            try:
                # Safe eval of simple conditions
                passed = eval(step.condition, {"__builtins__": {}}, context)
                result["passed"] = bool(passed)
                result["success"] = True
            except:
                result["passed"] = False

        elif step.type == StepType.PARALLEL:
            # Execute parallel steps (would need sub-steps)
            result["success"] = True

        elif step.type == StepType.CHECKPOINT:
            # Save checkpoint
            result["checkpoint_data"] = context.copy()
            result["success"] = True

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Serialize workflow"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [
                {
                    "name": s.name,
                    "type": s.type.value,
                    "action": s.action,
                    "input": s.input,
                    "output": s.output,
                }
                for s in self.steps
            ],
            "version": self.version,
            "created_at": self.created_at.isoformat(),
        }


class WorkflowAPI:
    """
    Workflow Management API

    Define, execute, and monitor workflows.
    """

    def __init__(self, client: FlowSync):
        self._client = client
        self._workflows: Dict[str, Workflow] = {}

    async def create(
        self,
        name: str,
        steps: List[Union[Step, Dict[str, Any]]],
        description: str = "",
        metadata: Dict[str, Any] = None
    ) -> Workflow:
        """
        Create a new workflow

        Args:
            name: Workflow name
            steps: List of workflow steps
            description: Workflow description
            metadata: Additional metadata

        Returns:
            Workflow instance
        """
        # Parse steps
        parsed_steps = []
        for step in steps:
            if isinstance(step, dict):
                step_type = StepType(step.get("type", "action"))
                parsed_steps.append(Step(
                    name=step.get("name", f"step_{len(parsed_steps)}"),
                    type=step_type,
                    action=step.get("action", ""),
                    input=step.get("input", ""),
                    output=step.get("output", ""),
                    agent_id=step.get("agent_id"),
                    condition=step.get("condition"),
                ))
            else:
                parsed_steps.append(step)

        # Generate ID
        workflow_id = hashlib.sha256(
            f"{name}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            steps=parsed_steps,
            metadata=metadata or {},
            _client=self._client,
        )

        self._workflows[workflow_id] = workflow
        return workflow

    async def get(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self._workflows.get(workflow_id)

    async def list(self) -> List[Workflow]:
        """List all workflows"""
        return list(self._workflows.values())

    async def delete(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            return True
        return False

    async def from_yaml(self, yaml_path: str) -> Workflow:
        """Load workflow from YAML file"""
        import yaml
        with open(yaml_path) as f:
            spec = yaml.safe_load(f)
        return await self.create(
            name=spec.get("name", "unnamed"),
            steps=spec.get("steps", []),
            description=spec.get("description", ""),
        )

    async def to_yaml(self, workflow_id: str, path: str):
        """Save workflow to YAML file"""
        import yaml
        workflow = self._workflows.get(workflow_id)
        if workflow:
            with open(path, 'w') as f:
                yaml.dump(workflow.to_dict(), f)


# =============================================================================
# COMPLIANCE API
# =============================================================================

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci-dss"
    EU_AI_ACT = "eu-ai-act"
    CCPA = "ccpa"
    ISO_27001 = "iso-27001"


@dataclass
class ComplianceCheck:
    """A compliance check result"""
    framework: ComplianceFramework
    requirement: str
    status: str  # passed, failed, warning, not_applicable
    details: str
    remediation: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """A compliance report"""
    id: str
    target: str  # What was checked
    frameworks: List[ComplianceFramework]
    checks: List[ComplianceCheck]
    overall_status: str  # compliant, non_compliant, partial
    score: float  # 0-100
    generated_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> Dict[str, Any]:
        """Get report summary"""
        by_status = {}
        for check in self.checks:
            by_status[check.status] = by_status.get(check.status, 0) + 1

        return {
            "target": self.target,
            "frameworks": [f.value for f in self.frameworks],
            "overall_status": self.overall_status,
            "score": self.score,
            "checks_by_status": by_status,
            "total_checks": len(self.checks),
        }


class ComplianceAPI:
    """
    Compliance Management API

    Verify compliance with regulatory frameworks.
    """

    # Compliance rules database
    RULES = {
        ComplianceFramework.GDPR: [
            {
                "id": "gdpr-1",
                "requirement": "Data minimization",
                "check": "Collect only necessary data",
            },
            {
                "id": "gdpr-2",
                "requirement": "Right to erasure",
                "check": "Provide data deletion mechanism",
            },
            {
                "id": "gdpr-3",
                "requirement": "Consent management",
                "check": "Obtain explicit consent for data processing",
            },
            {
                "id": "gdpr-4",
                "requirement": "Data portability",
                "check": "Allow data export in machine-readable format",
            },
        ],
        ComplianceFramework.HIPAA: [
            {
                "id": "hipaa-1",
                "requirement": "PHI encryption",
                "check": "Encrypt all protected health information",
            },
            {
                "id": "hipaa-2",
                "requirement": "Access controls",
                "check": "Implement role-based access to PHI",
            },
            {
                "id": "hipaa-3",
                "requirement": "Audit logging",
                "check": "Log all access to PHI",
            },
        ],
        ComplianceFramework.EU_AI_ACT: [
            {
                "id": "euai-1",
                "requirement": "Transparency",
                "check": "Disclose AI system usage to users",
            },
            {
                "id": "euai-2",
                "requirement": "Human oversight",
                "check": "Provide human-in-the-loop controls",
            },
            {
                "id": "euai-3",
                "requirement": "Risk assessment",
                "check": "Document AI system risk level",
            },
            {
                "id": "euai-4",
                "requirement": "Bias mitigation",
                "check": "Test and mitigate algorithmic bias",
            },
        ],
    }

    def __init__(self, client: FlowSync):
        self._client = client
        self._reports: List[ComplianceReport] = []

    async def check(
        self,
        target: str,
        frameworks: List[Union[str, ComplianceFramework]] = None,
        evidence: Dict[str, Any] = None
    ) -> ComplianceReport:
        """
        Run compliance checks

        Args:
            target: What to check (agent, workflow, or system component)
            frameworks: Which frameworks to check against
            evidence: Evidence data for checks

        Returns:
            ComplianceReport with results
        """
        # Parse frameworks
        fws = []
        for fw in (frameworks or [ComplianceFramework.GDPR]):
            if isinstance(fw, str):
                fws.append(ComplianceFramework(fw))
            else:
                fws.append(fw)

        evidence = evidence or {}
        checks = []

        # Run checks for each framework
        for framework in fws:
            rules = self.RULES.get(framework, [])
            for rule in rules:
                check_result = await self._run_check(rule, evidence)
                checks.append(ComplianceCheck(
                    framework=framework,
                    requirement=rule["requirement"],
                    status=check_result["status"],
                    details=check_result["details"],
                    remediation=check_result.get("remediation", ""),
                    evidence=check_result.get("evidence", {}),
                ))

        # Calculate score
        passed = len([c for c in checks if c.status == "passed"])
        total = len(checks)
        score = (passed / max(1, total)) * 100

        # Determine overall status
        if score == 100:
            overall = "compliant"
        elif score >= 70:
            overall = "partial"
        else:
            overall = "non_compliant"

        report_id = hashlib.sha256(
            f"{target}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        report = ComplianceReport(
            id=report_id,
            target=target,
            frameworks=fws,
            checks=checks,
            overall_status=overall,
            score=score,
        )

        self._reports.append(report)
        return report

    async def _run_check(self, rule: Dict, evidence: Dict) -> Dict[str, Any]:
        """Run a single compliance check"""
        # Simple evidence-based checking
        rule_id = rule["id"]

        # Check if evidence exists for this rule
        if rule_id in evidence:
            return {
                "status": "passed" if evidence[rule_id] else "failed",
                "details": f"Evidence provided: {evidence.get(rule_id)}",
                "evidence": {rule_id: evidence[rule_id]},
            }

        # Default to warning if no evidence
        return {
            "status": "warning",
            "details": f"No evidence provided for: {rule['check']}",
            "remediation": f"Provide evidence for {rule['requirement']}",
        }

    async def get_report(self, report_id: str) -> Optional[ComplianceReport]:
        """Get a compliance report by ID"""
        for report in self._reports:
            if report.id == report_id:
                return report
        return None

    async def list_reports(self) -> List[ComplianceReport]:
        """List all compliance reports"""
        return self._reports

    def get_requirements(self, framework: ComplianceFramework) -> List[Dict]:
        """Get requirements for a framework"""
        return self.RULES.get(framework, [])


# =============================================================================
# ECONOMY API
# =============================================================================

class TokenType(Enum):
    """Token types in the economy"""
    ORB = "orb"  # Main utility token
    COMPUTE = "compute"  # Compute credits
    STORAGE = "storage"  # Storage credits
    API_CALL = "api_call"  # API call credits


@dataclass
class Wallet:
    """A wallet in the FlowSync economy"""
    id: str
    owner: str
    balances: Dict[TokenType, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def balance(self, token: TokenType) -> float:
        """Get balance for a token type"""
        return self.balances.get(token, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize wallet"""
        return {
            "id": self.id,
            "owner": self.owner,
            "balances": {t.value: v for t, v in self.balances.items()},
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Transaction:
    """A transaction in the economy"""
    id: str
    from_wallet: str
    to_wallet: str
    token: TokenType
    amount: float
    fee: float
    status: str  # pending, confirmed, failed
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Stake:
    """A staking position"""
    id: str
    wallet_id: str
    amount: float
    node_type: str  # compute, storage, validator
    locked_until: datetime
    rewards_earned: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


class EconomyAPI:
    """
    Economy & Tokenomics API

    Manage tokens, wallets, staking, and marketplace.
    """

    # Fee structure
    FEES = {
        "transfer": 0.001,  # 0.1%
        "stake": 0.0,
        "unstake": 0.005,  # 0.5%
        "api_call": 0.0001,  # Per call
    }

    # Staking rewards (APY)
    STAKING_REWARDS = {
        "compute": 0.12,  # 12% APY
        "storage": 0.08,  # 8% APY
        "validator": 0.15,  # 15% APY
    }

    def __init__(self, client: FlowSync):
        self._client = client
        self._wallets: Dict[str, Wallet] = {}
        self._transactions: List[Transaction] = []
        self._stakes: List[Stake] = []

    async def create_wallet(self, owner: str) -> Wallet:
        """Create a new wallet"""
        wallet_id = hashlib.sha256(
            f"{owner}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        wallet = Wallet(
            id=wallet_id,
            owner=owner,
            balances={
                TokenType.ORB: 0.0,
                TokenType.COMPUTE: 0.0,
                TokenType.STORAGE: 0.0,
                TokenType.API_CALL: 0.0,
            },
        )

        self._wallets[wallet_id] = wallet
        return wallet

    async def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        """Get wallet by ID"""
        return self._wallets.get(wallet_id)

    async def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        token: TokenType,
        amount: float
    ) -> Transaction:
        """Transfer tokens between wallets"""
        sender = self._wallets.get(from_wallet)
        receiver = self._wallets.get(to_wallet)

        if not sender or not receiver:
            raise ValueError("Invalid wallet ID")

        fee = amount * self.FEES["transfer"]
        total = amount + fee

        if sender.balance(token) < total:
            raise ValueError("Insufficient balance")

        # Execute transfer
        sender.balances[token] -= total
        receiver.balances[token] = receiver.balance(token) + amount

        tx_id = hashlib.sha256(
            f"{from_wallet}-{to_wallet}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        tx = Transaction(
            id=tx_id,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            token=token,
            amount=amount,
            fee=fee,
            status="confirmed",
        )

        self._transactions.append(tx)
        return tx

    async def stake(
        self,
        wallet_id: str,
        amount: float,
        node_type: str,
        duration_days: int = 30
    ) -> Stake:
        """Stake tokens"""
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            raise ValueError("Invalid wallet ID")

        if wallet.balance(TokenType.ORB) < amount:
            raise ValueError("Insufficient balance")

        # Lock tokens
        wallet.balances[TokenType.ORB] -= amount

        stake_id = hashlib.sha256(
            f"{wallet_id}-stake-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        from datetime import timedelta
        stake = Stake(
            id=stake_id,
            wallet_id=wallet_id,
            amount=amount,
            node_type=node_type,
            locked_until=datetime.now() + timedelta(days=duration_days),
        )

        self._stakes.append(stake)
        return stake

    async def unstake(self, stake_id: str) -> float:
        """Unstake tokens (if lock period ended)"""
        for stake in self._stakes:
            if stake.id == stake_id:
                if datetime.now() < stake.locked_until:
                    raise ValueError("Stake still locked")

                wallet = self._wallets.get(stake.wallet_id)
                if wallet:
                    # Return principal + rewards minus fee
                    total = stake.amount + stake.rewards_earned
                    fee = total * self.FEES["unstake"]
                    wallet.balances[TokenType.ORB] += (total - fee)

                self._stakes.remove(stake)
                return total - fee

        raise ValueError("Stake not found")

    async def calculate_rewards(self, stake_id: str) -> float:
        """Calculate pending staking rewards"""
        for stake in self._stakes:
            if stake.id == stake_id:
                days_staked = (datetime.now() - stake.created_at).days
                apy = self.STAKING_REWARDS.get(stake.node_type, 0.05)
                reward = stake.amount * (apy / 365) * days_staked
                return reward
        return 0.0

    async def get_price(self, token: TokenType) -> float:
        """Get current token price (placeholder)"""
        # Would connect to price oracle
        prices = {
            TokenType.ORB: 1.50,
            TokenType.COMPUTE: 0.10,
            TokenType.STORAGE: 0.05,
            TokenType.API_CALL: 0.001,
        }
        return prices.get(token, 0.0)

    async def purchase_credits(
        self,
        wallet_id: str,
        credit_type: TokenType,
        amount: float
    ) -> Transaction:
        """Purchase compute/storage credits with ORB"""
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            raise ValueError("Invalid wallet ID")

        # Calculate ORB cost
        orb_price = await self.get_price(TokenType.ORB)
        credit_price = await self.get_price(credit_type)
        orb_cost = (amount * credit_price) / orb_price

        if wallet.balance(TokenType.ORB) < orb_cost:
            raise ValueError("Insufficient ORB balance")

        # Execute purchase
        wallet.balances[TokenType.ORB] -= orb_cost
        wallet.balances[credit_type] = wallet.balance(credit_type) + amount

        tx_id = hashlib.sha256(
            f"purchase-{wallet_id}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        tx = Transaction(
            id=tx_id,
            from_wallet=wallet_id,
            to_wallet="treasury",
            token=TokenType.ORB,
            amount=orb_cost,
            fee=0,
            status="confirmed",
            metadata={"credit_type": credit_type.value, "credit_amount": amount},
        )

        self._transactions.append(tx)
        return tx

    def get_stats(self) -> Dict[str, Any]:
        """Get economy statistics"""
        total_staked = sum(s.amount for s in self._stakes)
        total_transactions = len(self._transactions)

        return {
            "total_wallets": len(self._wallets),
            "total_staked": total_staked,
            "total_transactions": total_transactions,
            "active_stakes": len(self._stakes),
        }


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

# Quick start function
async def quick_start(api_key: str = None) -> FlowSync:
    """Quick start FlowSync client"""
    client = FlowSync(api_key=api_key or os.getenv("FLOWSYNC_API_KEY", "demo"))
    await client.connect()
    return client


# Export main classes
__all__ = [
    # Core
    "FlowSync",
    "FlowSyncConfig",

    # Agents
    "Agent",
    "AgentAPI",
    "AgentCapability",

    # Workflows
    "Workflow",
    "WorkflowAPI",
    "WorkflowRun",
    "Step",
    "StepType",

    # Compliance
    "ComplianceAPI",
    "ComplianceFramework",
    "ComplianceReport",
    "ComplianceCheck",

    # Economy
    "EconomyAPI",
    "Wallet",
    "Transaction",
    "Stake",
    "TokenType",

    # Utilities
    "quick_start",
]


# =============================================================================
# CLI DEMO
# =============================================================================

async def demo():
    """Run SDK demo"""
    print("\n" + "=" * 60)
    print("FLOWSYNC SDK DEMO")
    print("=" * 60)

    # Initialize client
    async with FlowSync(api_key="demo-key") as client:

        # 1. Create an agent
        print("\n[1] Creating Agent...")
        agent = await client.agents.create(
            name="demo-agent",
            capabilities=["nlp", "code-gen", "reasoning"],
        )
        print(f"    Created: {agent.name} ({agent.id})")

        # 2. Execute a task
        print("\n[2] Executing Task...")
        result = await agent.execute("Analyze this code for bugs")
        print(f"    Result: {result['success']}")

        # 3. Create a workflow
        print("\n[3] Creating Workflow...")
        workflow = await client.workflows.create(
            name="demo-workflow",
            description="A demo workflow",
            steps=[
                {"name": "analyze", "action": "analyze", "input": "$query", "output": "analysis"},
                {"name": "generate", "action": "generate", "input": "$analysis", "output": "code"},
            ],
        )
        print(f"    Created: {workflow.name} ({workflow.id})")

        # 4. Run workflow
        print("\n[4] Running Workflow...")
        run = await workflow.run(query="Build a dashboard")
        print(f"    Status: {run.status}")

        # 5. Compliance check
        print("\n[5] Running Compliance Check...")
        report = await client.compliance.check(
            target="demo-agent",
            frameworks=["gdpr", "eu-ai-act"],
            evidence={"gdpr-1": True, "gdpr-2": True, "euai-1": True},
        )
        print(f"    Score: {report.score:.1f}%")
        print(f"    Status: {report.overall_status}")

        # 6. Economy operations
        print("\n[6] Economy Operations...")
        wallet = await client.economy.create_wallet("demo-user")
        wallet.balances[TokenType.ORB] = 1000.0  # Give some tokens
        print(f"    Wallet: {wallet.id}")
        print(f"    Balance: {wallet.balance(TokenType.ORB)} ORB")

        # Stake
        stake = await client.economy.stake(wallet.id, 100.0, "compute", 30)
        print(f"    Staked: {stake.amount} ORB for {stake.node_type}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
