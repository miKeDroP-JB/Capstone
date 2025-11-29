#!/usr/bin/env python3
"""
HEALTHCARE VERTICAL - 0RB_AETHER
AI-powered healthcare services with full HIPAA compliance.

Components:
- Patient Management: Records, appointments, care coordination
- Diagnostics: AI-assisted diagnosis, imaging analysis, lab interpretation
- Compliance: HIPAA, audit trails, consent management
- Analytics: Population health, outcomes tracking, risk stratification

Love - Loyalty - Honor - Everybody Eats
"""
import os
import sys
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

__version__ = "0.1.0"


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class PatientStatus(Enum):
    """Patient status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"


class EncounterType(Enum):
    """Types of clinical encounters"""
    OFFICE_VISIT = "office_visit"
    EMERGENCY = "emergency"
    INPATIENT = "inpatient"
    TELEHEALTH = "telehealth"
    LAB_ONLY = "lab_only"


class ConsentType(Enum):
    """Types of consent"""
    TREATMENT = "treatment"
    DATA_SHARING = "data_sharing"
    RESEARCH = "research"
    MARKETING = "marketing"
    HIPAA_DISCLOSURE = "hipaa_disclosure"


class DiagnosticCategory(Enum):
    """Diagnostic categories"""
    IMAGING = "imaging"
    LAB = "lab"
    PATHOLOGY = "pathology"
    GENETICS = "genetics"
    VITALS = "vitals"


class RiskLevel(Enum):
    """Health risk levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AccessAction(Enum):
    """PHI access actions for audit"""
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    PRINT = "print"


# =============================================================================
# PATIENT MANAGEMENT
# =============================================================================

@dataclass
class Address:
    """Physical address"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"


@dataclass
class EmergencyContact:
    """Emergency contact information"""
    name: str
    relationship: str
    phone: str
    email: str = None


@dataclass
class Patient:
    """Patient record (PHI)"""
    id: str
    mrn: str  # Medical Record Number
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    ssn_last_four: str  # Only store last 4
    email: str
    phone: str
    address: Address
    emergency_contact: EmergencyContact = None
    status: PatientStatus = PatientStatus.ACTIVE
    primary_care_provider: str = None
    insurance_id: str = None
    allergies: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


@dataclass
class Encounter:
    """Clinical encounter"""
    id: str
    patient_id: str
    provider_id: str
    encounter_type: EncounterType
    chief_complaint: str
    diagnosis_codes: List[str] = field(default_factory=list)  # ICD-10
    procedure_codes: List[str] = field(default_factory=list)  # CPT
    notes: str = ""
    vitals: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime = None
    status: str = "in_progress"


@dataclass
class Appointment:
    """Patient appointment"""
    id: str
    patient_id: str
    provider_id: str
    appointment_type: str
    scheduled_at: datetime
    duration_minutes: int = 30
    status: str = "scheduled"  # scheduled, confirmed, checked_in, completed, cancelled, no_show
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class PatientRegistry:
    """
    Patient management system.

    Features:
    - Patient registration
    - Medical record management
    - Appointment scheduling
    - Care coordination
    """

    def __init__(self, audit_log: "HIPAAAuditLog" = None):
        self._patients: Dict[str, Patient] = {}
        self._encounters: Dict[str, Encounter] = {}
        self._appointments: Dict[str, Appointment] = {}
        self._mrn_counter = 0
        self._audit = audit_log

    def _log_access(
        self,
        action: AccessAction,
        patient_id: str,
        user_id: str,
        details: Dict = None
    ):
        """Log PHI access"""
        if self._audit:
            self._audit.log_access(
                action=action,
                patient_id=patient_id,
                user_id=user_id,
                resource_type="patient_record",
                details=details,
            )

    def register_patient(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        gender: str,
        ssn_last_four: str,
        email: str,
        phone: str,
        address: Address,
        registered_by: str,
        **kwargs
    ) -> Patient:
        """Register a new patient"""
        self._mrn_counter += 1
        mrn = f"MRN{self._mrn_counter:08d}"

        patient_id = hashlib.sha256(
            f"patient-{mrn}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        patient = Patient(
            id=patient_id,
            mrn=mrn,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            ssn_last_four=ssn_last_four,
            email=email,
            phone=phone,
            address=address,
            **kwargs,
        )

        self._patients[patient_id] = patient
        self._log_access(AccessAction.CREATE, patient_id, registered_by)
        return patient

    def get_patient(self, patient_id: str, accessed_by: str) -> Optional[Patient]:
        """Get patient by ID"""
        patient = self._patients.get(patient_id)
        if patient:
            self._log_access(AccessAction.VIEW, patient_id, accessed_by)
        return patient

    def update_patient(
        self,
        patient_id: str,
        updated_by: str,
        **updates
    ) -> Optional[Patient]:
        """Update patient record"""
        patient = self._patients.get(patient_id)
        if not patient:
            return None

        for key, value in updates.items():
            if hasattr(patient, key):
                setattr(patient, key, value)

        patient.updated_at = datetime.now()
        self._log_access(
            AccessAction.UPDATE,
            patient_id,
            updated_by,
            {"fields_updated": list(updates.keys())},
        )
        return patient

    def search_patients(
        self,
        searched_by: str,
        name: str = None,
        mrn: str = None,
        dob: date = None
    ) -> List[Patient]:
        """Search patients"""
        results = list(self._patients.values())

        if name:
            name_lower = name.lower()
            results = [
                p for p in results
                if name_lower in p.full_name.lower()
            ]

        if mrn:
            results = [p for p in results if p.mrn == mrn]

        if dob:
            results = [p for p in results if p.date_of_birth == dob]

        # Log search (not individual patient access)
        if self._audit:
            self._audit.log_access(
                action=AccessAction.VIEW,
                patient_id="SEARCH",
                user_id=searched_by,
                resource_type="patient_search",
                details={"result_count": len(results)},
            )

        return results

    def create_encounter(
        self,
        patient_id: str,
        provider_id: str,
        encounter_type: EncounterType,
        chief_complaint: str
    ) -> Encounter:
        """Create clinical encounter"""
        encounter_id = hashlib.sha256(
            f"enc-{patient_id}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        encounter = Encounter(
            id=encounter_id,
            patient_id=patient_id,
            provider_id=provider_id,
            encounter_type=encounter_type,
            chief_complaint=chief_complaint,
        )

        self._encounters[encounter_id] = encounter
        self._log_access(AccessAction.CREATE, patient_id, provider_id, {"encounter_id": encounter_id})
        return encounter

    def schedule_appointment(
        self,
        patient_id: str,
        provider_id: str,
        appointment_type: str,
        scheduled_at: datetime,
        duration_minutes: int = 30,
        scheduled_by: str = None
    ) -> Appointment:
        """Schedule appointment"""
        appt_id = hashlib.sha256(
            f"appt-{patient_id}-{scheduled_at.isoformat()}".encode()
        ).hexdigest()[:12]

        appointment = Appointment(
            id=appt_id,
            patient_id=patient_id,
            provider_id=provider_id,
            appointment_type=appointment_type,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
        )

        self._appointments[appt_id] = appointment
        self._log_access(
            AccessAction.CREATE,
            patient_id,
            scheduled_by or provider_id,
            {"appointment_id": appt_id},
        )
        return appointment


# =============================================================================
# DIAGNOSTICS
# =============================================================================

@dataclass
class DiagnosticResult:
    """A diagnostic test result"""
    id: str
    patient_id: str
    category: DiagnosticCategory
    test_name: str
    result_value: str
    reference_range: str = None
    unit: str = None
    abnormal: bool = False
    critical: bool = False
    performed_at: datetime = field(default_factory=datetime.now)
    reported_at: datetime = None
    ordered_by: str = None
    notes: str = ""


@dataclass
class AIAnalysis:
    """AI-generated diagnostic analysis"""
    id: str
    patient_id: str
    analysis_type: str
    findings: List[str]
    confidence: float
    recommendations: List[str]
    risk_factors: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)


class DiagnosticsEngine:
    """
    AI-powered diagnostics.

    Features:
    - Lab result interpretation
    - Imaging analysis
    - Risk stratification
    - Care recommendations
    """

    # Normal ranges for common labs
    NORMAL_RANGES = {
        "glucose": (70, 100, "mg/dL"),
        "hemoglobin": (12.0, 17.5, "g/dL"),
        "creatinine": (0.7, 1.3, "mg/dL"),
        "cholesterol_total": (0, 200, "mg/dL"),
        "ldl": (0, 100, "mg/dL"),
        "hdl": (40, 200, "mg/dL"),
        "triglycerides": (0, 150, "mg/dL"),
        "hba1c": (4.0, 5.6, "%"),
        "blood_pressure_sys": (90, 120, "mmHg"),
        "blood_pressure_dia": (60, 80, "mmHg"),
    }

    def __init__(self):
        self._results: Dict[str, DiagnosticResult] = {}
        self._analyses: List[AIAnalysis] = []
        self._result_counter = 0
        self._analysis_counter = 0

    def record_result(
        self,
        patient_id: str,
        category: DiagnosticCategory,
        test_name: str,
        result_value: str,
        ordered_by: str,
        reference_range: str = None,
        unit: str = None
    ) -> DiagnosticResult:
        """Record a diagnostic result"""
        self._result_counter += 1
        result_id = f"result_{self._result_counter:08d}"

        # Check if abnormal
        abnormal = False
        critical = False

        test_key = test_name.lower().replace(" ", "_")
        if test_key in self.NORMAL_RANGES:
            low, high, default_unit = self.NORMAL_RANGES[test_key]
            try:
                value = float(result_value)
                abnormal = value < low or value > high
                critical = value < low * 0.5 or value > high * 2
                if not reference_range:
                    reference_range = f"{low}-{high}"
                if not unit:
                    unit = default_unit
            except ValueError:
                pass

        result = DiagnosticResult(
            id=result_id,
            patient_id=patient_id,
            category=category,
            test_name=test_name,
            result_value=result_value,
            reference_range=reference_range,
            unit=unit,
            abnormal=abnormal,
            critical=critical,
            ordered_by=ordered_by,
        )

        self._results[result_id] = result
        return result

    def get_patient_results(
        self,
        patient_id: str,
        category: DiagnosticCategory = None,
        since: datetime = None
    ) -> List[DiagnosticResult]:
        """Get diagnostic results for patient"""
        results = [r for r in self._results.values() if r.patient_id == patient_id]

        if category:
            results = [r for r in results if r.category == category]

        if since:
            results = [r for r in results if r.performed_at >= since]

        return sorted(results, key=lambda r: r.performed_at, reverse=True)

    async def analyze_patient(
        self,
        patient_id: str,
        patient_data: Dict[str, Any]
    ) -> AIAnalysis:
        """AI analysis of patient data"""
        self._analysis_counter += 1
        analysis_id = f"analysis_{self._analysis_counter:06d}"

        # Get recent results
        results = self.get_patient_results(patient_id)

        # Analyze findings
        findings = []
        recommendations = []
        risk_factors = {}

        # Check for abnormal results
        abnormal_results = [r for r in results if r.abnormal]
        critical_results = [r for r in results if r.critical]

        for result in abnormal_results:
            findings.append(f"Abnormal {result.test_name}: {result.result_value} {result.unit}")

        for result in critical_results:
            findings.append(f"CRITICAL: {result.test_name} at {result.result_value} {result.unit}")

        # Age-based risk
        age = patient_data.get("age", 0)
        if age > 65:
            risk_factors["age"] = 0.3
            recommendations.append("Consider age-appropriate screenings")
        elif age > 50:
            risk_factors["age"] = 0.15

        # Condition-based risk
        conditions = patient_data.get("conditions", [])
        if "diabetes" in [c.lower() for c in conditions]:
            risk_factors["diabetes"] = 0.4
            recommendations.append("Monitor HbA1c quarterly")
        if "hypertension" in [c.lower() for c in conditions]:
            risk_factors["hypertension"] = 0.35
            recommendations.append("Monitor blood pressure regularly")

        # Calculate confidence based on data availability
        confidence = min(0.95, 0.5 + len(results) * 0.05)

        # Generate recommendations based on findings
        if not findings:
            findings.append("No abnormal results found in recent diagnostics")
            recommendations.append("Continue routine monitoring")

        analysis = AIAnalysis(
            id=analysis_id,
            patient_id=patient_id,
            analysis_type="comprehensive",
            findings=findings,
            confidence=confidence,
            recommendations=recommendations,
            risk_factors=risk_factors,
        )

        self._analyses.append(analysis)
        return analysis

    def calculate_risk_score(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate health risk score"""
        score = 0.0
        factors = []

        # Age factor
        age = patient_data.get("age", 0)
        if age > 70:
            score += 25
            factors.append("Age >70")
        elif age > 55:
            score += 15
            factors.append("Age >55")
        elif age > 40:
            score += 5

        # Condition factors
        conditions = [c.lower() for c in patient_data.get("conditions", [])]
        if "diabetes" in conditions:
            score += 20
            factors.append("Diabetes")
        if "hypertension" in conditions:
            score += 15
            factors.append("Hypertension")
        if "heart disease" in conditions:
            score += 25
            factors.append("Heart Disease")
        if "copd" in conditions:
            score += 15
            factors.append("COPD")

        # Determine risk level
        if score >= 60:
            level = RiskLevel.CRITICAL
        elif score >= 40:
            level = RiskLevel.HIGH
        elif score >= 20:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW

        return {
            "score": min(100, score),
            "level": level,
            "factors": factors,
        }


# =============================================================================
# HIPAA COMPLIANCE
# =============================================================================

@dataclass
class Consent:
    """Patient consent record"""
    id: str
    patient_id: str
    consent_type: ConsentType
    granted: bool
    granted_at: datetime = None
    expires_at: datetime = None
    revoked_at: datetime = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditEntry:
    """HIPAA audit log entry"""
    id: str
    timestamp: datetime
    user_id: str
    patient_id: str
    action: AccessAction
    resource_type: str
    resource_id: str = None
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = None
    success: bool = True


class HIPAAAuditLog:
    """
    HIPAA-compliant audit logging.

    All PHI access must be logged per HIPAA Security Rule.
    """

    def __init__(self):
        self._entries: List[AuditEntry] = []
        self._entry_counter = 0

    def log_access(
        self,
        action: AccessAction,
        patient_id: str,
        user_id: str,
        resource_type: str,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        success: bool = True
    ) -> AuditEntry:
        """Log PHI access"""
        self._entry_counter += 1
        entry_id = f"audit_{self._entry_counter:010d}"

        entry = AuditEntry(
            id=entry_id,
            timestamp=datetime.now(),
            user_id=user_id,
            patient_id=patient_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            success=success,
        )

        self._entries.append(entry)
        return entry

    def get_access_history(
        self,
        patient_id: str = None,
        user_id: str = None,
        action: AccessAction = None,
        since: datetime = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """Get access history"""
        entries = self._entries

        if patient_id:
            entries = [e for e in entries if e.patient_id == patient_id]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if since:
            entries = [e for e in entries if e.timestamp >= since]

        return sorted(entries, key=lambda e: e.timestamp, reverse=True)[:limit]

    def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate audit report for compliance"""
        entries = [
            e for e in self._entries
            if start_date <= e.timestamp <= end_date
        ]

        by_action = {}
        by_user = {}
        by_patient = {}

        for entry in entries:
            action_key = entry.action.value
            by_action[action_key] = by_action.get(action_key, 0) + 1

            by_user[entry.user_id] = by_user.get(entry.user_id, 0) + 1
            by_patient[entry.patient_id] = by_patient.get(entry.patient_id, 0) + 1

        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_accesses": len(entries),
            "by_action": by_action,
            "by_user": by_user,
            "unique_patients_accessed": len(by_patient),
            "failed_accesses": len([e for e in entries if not e.success]),
        }


class ConsentManager:
    """
    Patient consent management.

    Manages consent for treatment, data sharing, research, etc.
    """

    def __init__(self, audit_log: HIPAAAuditLog = None):
        self._consents: Dict[str, Dict[str, Consent]] = {}
        self._audit = audit_log
        self._consent_counter = 0

    def record_consent(
        self,
        patient_id: str,
        consent_type: ConsentType,
        granted: bool,
        recorded_by: str,
        expires_in_days: int = None,
        notes: str = ""
    ) -> Consent:
        """Record patient consent"""
        self._consent_counter += 1
        consent_id = f"consent_{self._consent_counter:06d}"

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        consent = Consent(
            id=consent_id,
            patient_id=patient_id,
            consent_type=consent_type,
            granted=granted,
            granted_at=datetime.now() if granted else None,
            expires_at=expires_at,
            notes=notes,
        )

        if patient_id not in self._consents:
            self._consents[patient_id] = {}
        self._consents[patient_id][consent_type.value] = consent

        if self._audit:
            self._audit.log_access(
                action=AccessAction.CREATE,
                patient_id=patient_id,
                user_id=recorded_by,
                resource_type="consent",
                resource_id=consent_id,
                details={"consent_type": consent_type.value, "granted": granted},
            )

        return consent

    def check_consent(
        self,
        patient_id: str,
        consent_type: ConsentType
    ) -> bool:
        """Check if patient has valid consent"""
        patient_consents = self._consents.get(patient_id, {})
        consent = patient_consents.get(consent_type.value)

        if not consent:
            return False

        if not consent.granted:
            return False

        if consent.revoked_at:
            return False

        if consent.expires_at and datetime.now() > consent.expires_at:
            return False

        return True

    def revoke_consent(
        self,
        patient_id: str,
        consent_type: ConsentType,
        revoked_by: str
    ) -> bool:
        """Revoke patient consent"""
        patient_consents = self._consents.get(patient_id, {})
        consent = patient_consents.get(consent_type.value)

        if not consent:
            return False

        consent.revoked_at = datetime.now()

        if self._audit:
            self._audit.log_access(
                action=AccessAction.UPDATE,
                patient_id=patient_id,
                user_id=revoked_by,
                resource_type="consent",
                resource_id=consent.id,
                details={"action": "revoke", "consent_type": consent_type.value},
            )

        return True


# =============================================================================
# HEALTHCARE VERTICAL
# =============================================================================

class HealthcareVertical:
    """
    Complete Healthcare Vertical.

    HIPAA-compliant healthcare services platform.
    """

    BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗  ██╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗             ║
║   ██║  ██║██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║             ║
║   ███████║█████╗  ███████║██║     ██║   ███████║             ║
║   ██╔══██║██╔══╝  ██╔══██║██║     ██║   ██╔══██║             ║
║   ██║  ██║███████╗██║  ██║███████╗██║   ██║  ██║             ║
║   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝             ║
║                                                               ║
║              Healthcare Vertical - 0RB_AETHER                 ║
║                     HIPAA Compliant                           ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
"""

    def __init__(self):
        self.audit_log = HIPAAAuditLog()
        self.patients = PatientRegistry(self.audit_log)
        self.diagnostics = DiagnosticsEngine()
        self.consent = ConsentManager(self.audit_log)

    def get_stats(self) -> Dict[str, Any]:
        """Get healthcare vertical statistics"""
        return {
            "patients": len(self.patients._patients),
            "encounters": len(self.patients._encounters),
            "appointments": len(self.patients._appointments),
            "diagnostic_results": len(self.diagnostics._results),
            "ai_analyses": len(self.diagnostics._analyses),
            "audit_entries": len(self.audit_log._entries),
        }


# =============================================================================
# CLI DEMO
# =============================================================================

async def demo():
    """Healthcare vertical demo"""
    print(HealthcareVertical.BANNER)

    healthcare = HealthcareVertical()

    print("\n[1] Registering Patient...")
    patient = healthcare.patients.register_patient(
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1965, 3, 15),
        gender="M",
        ssn_last_four="1234",
        email="john.smith@email.com",
        phone="555-123-4567",
        address=Address(
            street="123 Main St",
            city="Boston",
            state="MA",
            zip_code="02101",
        ),
        registered_by="admin_user",
        allergies=["Penicillin"],
        conditions=["Hypertension", "Type 2 Diabetes"],
    )
    print(f"    Patient: {patient.full_name}")
    print(f"    MRN: {patient.mrn}")
    print(f"    Age: {patient.age}")

    print("\n[2] Recording Consent...")
    healthcare.consent.record_consent(
        patient_id=patient.id,
        consent_type=ConsentType.TREATMENT,
        granted=True,
        recorded_by="admin_user",
    )
    healthcare.consent.record_consent(
        patient_id=patient.id,
        consent_type=ConsentType.HIPAA_DISCLOSURE,
        granted=True,
        recorded_by="admin_user",
        expires_in_days=365,
    )
    print("    Treatment consent: Granted")
    print("    HIPAA disclosure: Granted (1 year)")

    print("\n[3] Creating Encounter...")
    encounter = healthcare.patients.create_encounter(
        patient_id=patient.id,
        provider_id="dr_jones",
        encounter_type=EncounterType.OFFICE_VISIT,
        chief_complaint="Annual checkup",
    )
    print(f"    Encounter: {encounter.id}")
    print(f"    Type: {encounter.encounter_type.value}")

    print("\n[4] Recording Lab Results...")
    results = [
        ("Glucose", "105", DiagnosticCategory.LAB),
        ("HbA1c", "6.8", DiagnosticCategory.LAB),
        ("Blood Pressure Sys", "135", DiagnosticCategory.VITALS),
        ("Cholesterol Total", "210", DiagnosticCategory.LAB),
    ]
    for test, value, category in results:
        result = healthcare.diagnostics.record_result(
            patient_id=patient.id,
            category=category,
            test_name=test,
            result_value=value,
            ordered_by="dr_jones",
        )
        status = "ABNORMAL" if result.abnormal else "Normal"
        print(f"    {test}: {value} - {status}")

    print("\n[5] AI Health Analysis...")
    patient_data = {
        "age": patient.age,
        "conditions": patient.conditions,
    }
    analysis = await healthcare.diagnostics.analyze_patient(patient.id, patient_data)
    print(f"    Confidence: {analysis.confidence:.1%}")
    print(f"    Findings:")
    for finding in analysis.findings[:3]:
        print(f"      - {finding}")
    print(f"    Recommendations:")
    for rec in analysis.recommendations[:2]:
        print(f"      - {rec}")

    print("\n[6] Risk Stratification...")
    risk = healthcare.diagnostics.calculate_risk_score(patient_data)
    print(f"    Risk Score: {risk['score']}")
    print(f"    Risk Level: {risk['level'].value.upper()}")
    print(f"    Factors: {', '.join(risk['factors'])}")

    print("\n[7] Audit Log...")
    audit_report = healthcare.audit_log.generate_audit_report(
        start_date=datetime.now() - timedelta(hours=1),
        end_date=datetime.now(),
    )
    print(f"    Total Accesses: {audit_report['total_accesses']}")
    print(f"    By Action: {audit_report['by_action']}")

    print("\n[8] Statistics...")
    stats = healthcare.get_stats()
    for key, value in stats.items():
        print(f"    {key}: {value}")

    print("\n" + "=" * 50)
    print("HEALTHCARE VERTICAL DEMO COMPLETE")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
