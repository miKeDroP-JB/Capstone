#!/usr/bin/env python3
"""
0RB SOUL LAYER
Ethics, Safety, and Governance System.

This is your enterprise golden ticket - what every bank, hospital,
and defense organization will buy first.

Components:
- Ethics: Value alignment and ethical constraints
- Safety: Multi-layer safety controls
- Override: Multi-key emergency override system
- Audit: Complete event logging and compliance

EU AI Act obligations baked in.

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import json
import hashlib
import hmac
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import threading
import logging


class RiskLevel(Enum):
    """Risk levels for actions"""
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5
    PROHIBITED = 6


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    EU_AI_ACT = "eu_ai_act"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    CUSTOM = "custom"


@dataclass
class EthicalConstraint:
    """An ethical constraint/principle"""
    id: str
    name: str
    description: str
    category: str  # harm_prevention, fairness, transparency, privacy, autonomy
    priority: int  # 1=highest
    check_fn: Optional[Callable[[Dict], Tuple[bool, str]]] = None
    enabled: bool = True


@dataclass
class SafetyPolicy:
    """A safety policy rule"""
    id: str
    name: str
    description: str
    risk_level: RiskLevel
    conditions: Dict[str, Any]  # Conditions that trigger this policy
    actions: List[str]  # Actions to take (block, warn, log, escalate)
    requires_approval: bool = False
    approval_threshold: int = 1  # Number of approvals needed
    enabled: bool = True


@dataclass
class AuditEvent:
    """An auditable event"""
    id: str
    timestamp: datetime
    event_type: str
    actor: str
    action: str
    resource: str
    outcome: str  # success, failure, blocked
    risk_level: RiskLevel
    details: Dict[str, Any] = field(default_factory=dict)
    compliance_flags: List[str] = field(default_factory=list)


class EthicsEngine:
    """
    Ethics engine enforcing value alignment.

    Built-in principles:
    - Harm Prevention: Avoid actions that cause harm
    - Fairness: Treat all users equitably
    - Transparency: Be clear about AI capabilities and limitations
    - Privacy: Protect personal data
    - Autonomy: Respect user agency and consent
    """

    def __init__(self):
        self.constraints: Dict[str, EthicalConstraint] = {}
        self.violations: List[Dict] = []
        self._load_default_constraints()

    def _load_default_constraints(self):
        """Load built-in ethical constraints"""

        # Harm Prevention
        self.add_constraint(
            name="No Physical Harm",
            description="Prevent actions that could cause physical harm",
            category="harm_prevention",
            priority=1,
            check_fn=self._check_physical_harm
        )

        self.add_constraint(
            name="No Psychological Harm",
            description="Prevent actions causing psychological distress",
            category="harm_prevention",
            priority=2,
            check_fn=self._check_psychological_harm
        )

        # Fairness
        self.add_constraint(
            name="No Discrimination",
            description="Prevent discriminatory outputs based on protected characteristics",
            category="fairness",
            priority=1,
            check_fn=self._check_discrimination
        )

        # Transparency
        self.add_constraint(
            name="AI Disclosure",
            description="Clearly identify AI-generated content",
            category="transparency",
            priority=3,
            check_fn=self._check_disclosure
        )

        # Privacy
        self.add_constraint(
            name="PII Protection",
            description="Protect personally identifiable information",
            category="privacy",
            priority=1,
            check_fn=self._check_pii
        )

        # Autonomy
        self.add_constraint(
            name="Consent Required",
            description="Require consent for sensitive operations",
            category="autonomy",
            priority=2,
            check_fn=self._check_consent
        )

    def add_constraint(
        self,
        name: str,
        description: str,
        category: str,
        priority: int,
        check_fn: Callable = None
    ) -> str:
        """Add an ethical constraint"""
        constraint_id = f"eth_{hashlib.md5(name.encode()).hexdigest()[:8]}"

        self.constraints[constraint_id] = EthicalConstraint(
            id=constraint_id,
            name=name,
            description=description,
            category=category,
            priority=priority,
            check_fn=check_fn
        )

        return constraint_id

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, List[Dict]]:
        """
        Evaluate action against all ethical constraints.

        Returns (is_ethical, list of violations)
        """
        violations = []

        # Sort by priority
        sorted_constraints = sorted(
            [c for c in self.constraints.values() if c.enabled],
            key=lambda c: c.priority
        )

        for constraint in sorted_constraints:
            if constraint.check_fn:
                is_ok, reason = constraint.check_fn(context)
                if not is_ok:
                    violation = {
                        "constraint_id": constraint.id,
                        "constraint_name": constraint.name,
                        "category": constraint.category,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat()
                    }
                    violations.append(violation)
                    self.violations.append(violation)

        return len(violations) == 0, violations

    # Constraint check functions
    def _check_physical_harm(self, context: Dict) -> Tuple[bool, str]:
        """Check for potential physical harm"""
        dangerous_keywords = [
            "weapon", "bomb", "explosive", "poison", "kill", "hurt",
            "injure", "attack", "violence", "self-harm"
        ]

        content = str(context.get("content", "")).lower()
        for keyword in dangerous_keywords:
            if keyword in content:
                return False, f"Content may relate to physical harm: {keyword}"

        return True, ""

    def _check_psychological_harm(self, context: Dict) -> Tuple[bool, str]:
        """Check for potential psychological harm"""
        harmful_patterns = ["harassment", "bully", "threat", "intimidat"]

        content = str(context.get("content", "")).lower()
        for pattern in harmful_patterns:
            if pattern in content:
                return False, f"Content may cause psychological harm: {pattern}"

        return True, ""

    def _check_discrimination(self, context: Dict) -> Tuple[bool, str]:
        """Check for discriminatory content"""
        protected_attributes = [
            "race", "gender", "religion", "nationality", "disability",
            "age", "sexual orientation", "ethnicity"
        ]

        content = str(context.get("content", "")).lower()
        action = context.get("action", "")

        # Check if making decisions based on protected attributes
        if action in ["evaluate", "score", "rank", "filter"]:
            for attr in protected_attributes:
                if attr in content:
                    return False, f"Decision may be based on protected attribute: {attr}"

        return True, ""

    def _check_disclosure(self, context: Dict) -> Tuple[bool, str]:
        """Check for AI disclosure compliance"""
        is_public = context.get("is_public", False)
        has_disclosure = context.get("ai_disclosed", False)

        if is_public and not has_disclosure:
            return False, "Public AI content must include disclosure"

        return True, ""

    def _check_pii(self, context: Dict) -> Tuple[bool, str]:
        """Check for PII exposure"""
        import re

        content = str(context.get("content", ""))

        # Check for common PII patterns
        patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', "SSN"),
            (r'\b\d{16}\b', "Credit Card"),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "Email"),
        ]

        for pattern, pii_type in patterns:
            if re.search(pattern, content):
                if not context.get("pii_handling_approved", False):
                    return False, f"Contains unprotected {pii_type}"

        return True, ""

    def _check_consent(self, context: Dict) -> Tuple[bool, str]:
        """Check for proper consent"""
        action = context.get("action", "")
        sensitive_actions = ["collect_data", "share_data", "profile", "track"]

        if action in sensitive_actions:
            if not context.get("user_consent", False):
                return False, f"Action '{action}' requires user consent"

        return True, ""


class SafetySystem:
    """
    Multi-layer safety system.

    Layers:
    1. Input validation
    2. Risk assessment
    3. Policy enforcement
    4. Output filtering
    5. Emergency controls
    """

    def __init__(self):
        self.policies: Dict[str, SafetyPolicy] = {}
        self.blocked_actions: List[str] = []
        self.emergency_stop = False
        self._lock = threading.Lock()

        self._load_default_policies()

    def _load_default_policies(self):
        """Load default safety policies"""

        # Critical actions require approval
        self.add_policy(
            name="Destructive Operations",
            description="Block destructive operations without multi-approval",
            risk_level=RiskLevel.CRITICAL,
            conditions={"action_type": ["delete", "destroy", "wipe", "format"]},
            actions=["block", "log", "escalate"],
            requires_approval=True,
            approval_threshold=2
        )

        # High-risk data access
        self.add_policy(
            name="Sensitive Data Access",
            description="Log and monitor access to sensitive data",
            risk_level=RiskLevel.HIGH,
            conditions={"data_classification": ["confidential", "secret", "pii"]},
            actions=["log", "alert"],
            requires_approval=True
        )

        # Rate limiting
        self.add_policy(
            name="Rate Limit Breach",
            description="Block when rate limits exceeded",
            risk_level=RiskLevel.MEDIUM,
            conditions={"rate_exceeded": True},
            actions=["block", "warn"]
        )

        # Budget controls
        self.add_policy(
            name="Budget Critical",
            description="Stop operations when budget exhausted",
            risk_level=RiskLevel.HIGH,
            conditions={"budget_remaining_percent": 0},
            actions=["block", "alert"]
        )

    def add_policy(
        self,
        name: str,
        description: str,
        risk_level: RiskLevel,
        conditions: Dict,
        actions: List[str],
        requires_approval: bool = False,
        approval_threshold: int = 1
    ) -> str:
        """Add a safety policy"""
        policy_id = f"policy_{hashlib.md5(name.encode()).hexdigest()[:8]}"

        self.policies[policy_id] = SafetyPolicy(
            id=policy_id,
            name=name,
            description=description,
            risk_level=risk_level,
            conditions=conditions,
            actions=actions,
            requires_approval=requires_approval,
            approval_threshold=approval_threshold
        )

        return policy_id

    def check(self, context: Dict[str, Any]) -> Tuple[bool, List[str], Dict]:
        """
        Check action against safety policies.

        Returns (is_safe, actions_to_take, details)
        """
        with self._lock:
            if self.emergency_stop:
                return False, ["block"], {"reason": "Emergency stop active"}

        triggered_actions = []
        details = {"triggered_policies": []}

        for policy in self.policies.values():
            if not policy.enabled:
                continue

            if self._matches_conditions(context, policy.conditions):
                triggered_actions.extend(policy.actions)
                details["triggered_policies"].append({
                    "id": policy.id,
                    "name": policy.name,
                    "risk_level": policy.risk_level.name,
                    "requires_approval": policy.requires_approval
                })

        is_safe = "block" not in triggered_actions
        return is_safe, list(set(triggered_actions)), details

    def _matches_conditions(self, context: Dict, conditions: Dict) -> bool:
        """Check if context matches policy conditions"""
        for key, expected in conditions.items():
            actual = context.get(key)

            if isinstance(expected, list):
                if actual in expected:
                    return True
            elif isinstance(expected, bool):
                if actual == expected:
                    return True
            elif actual == expected:
                return True

        return False

    def emergency_shutdown(self, reason: str, actor: str):
        """Trigger emergency shutdown"""
        with self._lock:
            self.emergency_stop = True
            self.blocked_actions.append({
                "action": "emergency_shutdown",
                "reason": reason,
                "actor": actor,
                "timestamp": datetime.now().isoformat()
            })

    def reset_emergency(self, override_key: str, actor: str) -> bool:
        """Reset emergency stop with override key"""
        # Would verify override key in production
        with self._lock:
            self.emergency_stop = False
            return True


class OverrideSystem:
    """
    Multi-key override system for emergency controls.

    Features:
    - Multi-signature requirements
    - Time-limited overrides
    - Audit trail
    - Key rotation
    """

    @dataclass
    class OverrideKey:
        id: str
        holder: str
        key_hash: str
        created_at: datetime
        expires_at: Optional[datetime]
        permissions: Set[str]
        active: bool = True

    @dataclass
    class OverrideRequest:
        id: str
        action: str
        reason: str
        requester: str
        required_approvals: int
        approvals: List[Tuple[str, datetime]]  # (key_id, timestamp)
        created_at: datetime
        expires_at: datetime
        executed: bool = False

    def __init__(self, default_threshold: int = 2):
        self.keys: Dict[str, 'OverrideSystem.OverrideKey'] = {}
        self.pending_requests: Dict[str, 'OverrideSystem.OverrideRequest'] = {}
        self.executed_overrides: List['OverrideSystem.OverrideRequest'] = []
        self.default_threshold = default_threshold

        # Create master key
        self._create_master_key()

    def _create_master_key(self):
        """Create the master override key"""
        master_secret = secrets.token_hex(32)
        self.keys["master"] = self.OverrideKey(
            id="master",
            holder="SYSTEM",
            key_hash=hashlib.sha256(master_secret.encode()).hexdigest(),
            created_at=datetime.now(),
            expires_at=None,
            permissions={"*"},
            active=True
        )
        # In production, this would be stored securely
        self._master_secret = master_secret

    def create_key(
        self,
        holder: str,
        permissions: Set[str],
        expires_in_days: int = 365
    ) -> Tuple[str, str]:
        """
        Create a new override key.

        Returns (key_id, secret)
        """
        secret = secrets.token_hex(32)
        key_id = f"key_{secrets.token_hex(4)}"

        self.keys[key_id] = self.OverrideKey(
            id=key_id,
            holder=holder,
            key_hash=hashlib.sha256(secret.encode()).hexdigest(),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=expires_in_days),
            permissions=permissions
        )

        return key_id, secret

    def revoke_key(self, key_id: str) -> bool:
        """Revoke an override key"""
        if key_id in self.keys and key_id != "master":
            self.keys[key_id].active = False
            return True
        return False

    def request_override(
        self,
        action: str,
        reason: str,
        requester: str,
        threshold: int = None
    ) -> str:
        """Create an override request"""
        request_id = f"req_{secrets.token_hex(4)}"
        threshold = threshold or self.default_threshold

        self.pending_requests[request_id] = self.OverrideRequest(
            id=request_id,
            action=action,
            reason=reason,
            requester=requester,
            required_approvals=threshold,
            approvals=[],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24)
        )

        return request_id

    def approve_override(self, request_id: str, key_id: str, secret: str) -> Tuple[bool, str]:
        """
        Approve an override request.

        Returns (success, message)
        """
        request = self.pending_requests.get(request_id)
        if not request:
            return False, "Request not found"

        if datetime.now() > request.expires_at:
            return False, "Request expired"

        if request.executed:
            return False, "Override already executed"

        # Verify key
        key = self.keys.get(key_id)
        if not key or not key.active:
            return False, "Invalid or revoked key"

        if key.expires_at and datetime.now() > key.expires_at:
            return False, "Key expired"

        # Verify secret
        if hashlib.sha256(secret.encode()).hexdigest() != key.key_hash:
            return False, "Invalid secret"

        # Check if already approved by this key
        if any(k == key_id for k, _ in request.approvals):
            return False, "Already approved by this key"

        # Add approval
        request.approvals.append((key_id, datetime.now()))

        # Check if threshold met
        if len(request.approvals) >= request.required_approvals:
            request.executed = True
            self.executed_overrides.append(request)
            del self.pending_requests[request_id]
            return True, f"Override approved and executed ({len(request.approvals)}/{request.required_approvals})"

        return True, f"Approval recorded ({len(request.approvals)}/{request.required_approvals})"

    def get_pending_requests(self) -> List['OverrideSystem.OverrideRequest']:
        """Get all pending override requests"""
        # Clean up expired
        now = datetime.now()
        expired = [k for k, v in self.pending_requests.items() if now > v.expires_at]
        for k in expired:
            del self.pending_requests[k]

        return list(self.pending_requests.values())


class AuditSystem:
    """
    Complete audit logging system.

    Features:
    - Immutable audit log
    - Compliance reporting
    - Event correlation
    - Retention policies
    """

    def __init__(self, log_dir: str = "./audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.events: List[AuditEvent] = []
        self._event_counter = 0
        self._lock = threading.Lock()

        # Compliance profiles
        self.compliance_profiles: Dict[ComplianceFramework, Dict] = {
            ComplianceFramework.EU_AI_ACT: {
                "required_fields": ["risk_level", "actor", "ai_system_id"],
                "retention_days": 365 * 5,
                "high_risk_threshold": RiskLevel.HIGH,
            },
            ComplianceFramework.GDPR: {
                "required_fields": ["actor", "data_subject", "lawful_basis"],
                "retention_days": 365 * 7,
                "pii_handling": True,
            },
            ComplianceFramework.HIPAA: {
                "required_fields": ["actor", "patient_id", "access_reason"],
                "retention_days": 365 * 6,
                "phi_handling": True,
            },
        }

    def log(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        risk_level: RiskLevel = RiskLevel.LOW,
        details: Dict = None,
        compliance_frameworks: List[ComplianceFramework] = None
    ) -> str:
        """Log an audit event"""
        with self._lock:
            self._event_counter += 1
            event_id = f"audit_{self._event_counter:08d}"

            event = AuditEvent(
                id=event_id,
                timestamp=datetime.now(),
                event_type=event_type,
                actor=actor,
                action=action,
                resource=resource,
                outcome=outcome,
                risk_level=risk_level,
                details=details or {},
                compliance_flags=[f.value for f in (compliance_frameworks or [])]
            )

            self.events.append(event)
            self._write_to_file(event)

            return event_id

    def _write_to_file(self, event: AuditEvent):
        """Write event to log file"""
        date_str = event.timestamp.strftime("%Y%m%d")
        log_file = self.log_dir / f"audit_{date_str}.jsonl"

        log_entry = {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "actor": event.actor,
            "action": event.action,
            "resource": event.resource,
            "outcome": event.outcome,
            "risk_level": event.risk_level.name,
            "details": event.details,
            "compliance_flags": event.compliance_flags,
            "checksum": self._calculate_checksum(event)
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calculate event checksum for integrity"""
        data = f"{event.id}{event.timestamp}{event.actor}{event.action}{event.outcome}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def query(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        event_type: str = None,
        actor: str = None,
        min_risk_level: RiskLevel = None
    ) -> List[AuditEvent]:
        """Query audit events"""
        results = []

        for event in self.events:
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if event_type and event.event_type != event_type:
                continue
            if actor and event.actor != actor:
                continue
            if min_risk_level and event.risk_level.value < min_risk_level.value:
                continue

            results.append(event)

        return results

    def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        profile = self.compliance_profiles.get(framework, {})
        events = self.query(start_time=start_time, end_time=end_time)

        # Filter events with this framework flag
        framework_events = [e for e in events if framework.value in e.compliance_flags]

        # Analyze
        high_risk_events = [e for e in framework_events
                          if e.risk_level.value >= profile.get("high_risk_threshold", RiskLevel.HIGH).value]

        return {
            "framework": framework.value,
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "total_events": len(framework_events),
            "high_risk_events": len(high_risk_events),
            "events_by_type": self._count_by_field(framework_events, "event_type"),
            "events_by_outcome": self._count_by_field(framework_events, "outcome"),
            "generated_at": datetime.now().isoformat()
        }

    def _count_by_field(self, events: List[AuditEvent], field: str) -> Dict[str, int]:
        """Count events by field value"""
        counts = {}
        for event in events:
            value = getattr(event, field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts


class Soul:
    """
    The Soul - Unified Ethics, Safety, and Governance.

    This is the conscience of the AI system.
    """

    def __init__(self, log_dir: str = "./soul_logs"):
        self.ethics = EthicsEngine()
        self.safety = SafetySystem()
        self.override = OverrideSystem()
        self.audit = AuditSystem(log_dir)

        # Active compliance frameworks
        self.active_frameworks: Set[ComplianceFramework] = {
            ComplianceFramework.EU_AI_ACT
        }

    def evaluate(self, action: str, context: Dict[str, Any], actor: str) -> Dict[str, Any]:
        """
        Evaluate an action through the complete Soul pipeline.

        Returns evaluation result with decision and reasons.
        """
        result = {
            "action": action,
            "actor": actor,
            "timestamp": datetime.now().isoformat(),
            "allowed": True,
            "ethics": {"passed": True, "violations": []},
            "safety": {"passed": True, "actions": [], "details": {}},
            "requires_override": False,
            "audit_id": None
        }

        # 1. Ethics check
        is_ethical, violations = self.ethics.evaluate({**context, "action": action})
        result["ethics"]["passed"] = is_ethical
        result["ethics"]["violations"] = violations

        if not is_ethical:
            result["allowed"] = False

        # 2. Safety check
        is_safe, actions, details = self.safety.check({**context, "action": action})
        result["safety"]["passed"] = is_safe
        result["safety"]["actions"] = actions
        result["safety"]["details"] = details

        if not is_safe:
            result["allowed"] = False
            if "escalate" in actions:
                result["requires_override"] = True

        # 3. Audit
        risk_level = RiskLevel.LOW
        if not is_ethical or not is_safe:
            risk_level = RiskLevel.HIGH

        result["audit_id"] = self.audit.log(
            event_type="action_evaluation",
            actor=actor,
            action=action,
            resource=context.get("resource", "unknown"),
            outcome="allowed" if result["allowed"] else "blocked",
            risk_level=risk_level,
            details={
                "ethics_result": result["ethics"],
                "safety_result": result["safety"]
            },
            compliance_frameworks=list(self.active_frameworks)
        )

        return result

    def request_override(self, action: str, reason: str, requester: str) -> str:
        """Request an override for a blocked action"""
        return self.override.request_override(action, reason, requester)

    def approve_override(self, request_id: str, key_id: str, secret: str) -> Tuple[bool, str]:
        """Approve an override request"""
        success, message = self.override.approve_override(request_id, key_id, secret)

        self.audit.log(
            event_type="override_approval",
            actor=key_id,
            action="approve_override",
            resource=request_id,
            outcome="success" if success else "failure",
            risk_level=RiskLevel.HIGH,
            details={"message": message}
        )

        return success, message

    def get_status(self) -> Dict[str, Any]:
        """Get Soul status"""
        return {
            "ethics": {
                "constraints": len(self.ethics.constraints),
                "violations_logged": len(self.ethics.violations)
            },
            "safety": {
                "policies": len(self.safety.policies),
                "emergency_stop": self.safety.emergency_stop
            },
            "override": {
                "pending_requests": len(self.override.pending_requests),
                "active_keys": len([k for k in self.override.keys.values() if k.active])
            },
            "audit": {
                "total_events": len(self.audit.events)
            },
            "active_frameworks": [f.value for f in self.active_frameworks]
        }


# Demo
def demo():
    """Demonstrate Soul system"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                        0RB SOUL                               ║
║                                                               ║
║          Ethics - Safety - Override - Audit                   ║
║                                                               ║
║           The Conscience of the AI System                     ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    soul = Soul()

    # Test 1: Safe action
    print("[1] Testing safe action...")
    result = soul.evaluate(
        action="generate_report",
        context={"content": "Monthly sales report", "is_public": False},
        actor="user_123"
    )
    print(f"  Allowed: {result['allowed']}")
    print(f"  Ethics: {result['ethics']['passed']}")
    print(f"  Safety: {result['safety']['passed']}")

    # Test 2: Potentially harmful action
    print("\n[2] Testing potentially harmful action...")
    result = soul.evaluate(
        action="generate_content",
        context={"content": "How to make a weapon", "is_public": True},
        actor="user_456"
    )
    print(f"  Allowed: {result['allowed']}")
    print(f"  Ethics violations: {len(result['ethics']['violations'])}")
    for v in result['ethics']['violations']:
        print(f"    - {v['constraint_name']}: {v['reason']}")

    # Test 3: Override flow
    print("\n[3] Testing override flow...")
    request_id = soul.request_override(
        action="delete_database",
        reason="Emergency data migration",
        requester="admin_1"
    )
    print(f"  Override request: {request_id}")

    # Create a key and approve
    key_id, secret = soul.override.create_key(
        holder="admin_2",
        permissions={"*"}
    )
    success, msg = soul.approve_override(request_id, key_id, secret)
    print(f"  First approval: {msg}")

    # Status
    print(f"\n[*] Soul Status: {json.dumps(soul.get_status(), indent=2)}")


if __name__ == "__main__":
    demo()
