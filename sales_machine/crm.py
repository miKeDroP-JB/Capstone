#!/usr/bin/env python3
"""
CRM - Lead Tracking & Commission Management
Track leads, calls, appointments, and revenue.

Love - Loyalty - Honor - Everybody Eats
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    APPOINTMENT_SET = "appointment_set"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    NOT_INTERESTED = "not_interested"
    NO_ANSWER = "no_answer"
    CALLBACK = "callback"
    DO_NOT_CALL = "do_not_call"


class AppointmentStatus(Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


@dataclass
class Appointment:
    """A booked appointment"""
    id: str
    lead_id: str
    scheduled_time: datetime
    duration_minutes: int = 60
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    service_type: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    revenue: float = 0.0


@dataclass
class Commission:
    """Commission tracking"""
    id: str
    lead_id: str
    appointment_id: str
    total_revenue: float
    commission_rate: float = 0.10  # 10%
    commission_amount: float = 0.0
    client_amount: float = 0.0
    status: str = "pending"  # pending, paid, disputed
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None


@dataclass
class CallLog:
    """Record of a call"""
    id: str
    lead_id: str
    phone_number: str
    direction: str  # inbound, outbound
    duration_seconds: int
    outcome: str
    notes: str = ""
    recording_url: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CRMLead:
    """A lead in the CRM"""
    id: str
    business_name: str
    phone: str
    email: str = ""
    owner_name: str = ""
    address: str = ""
    city: str = ""
    state: str = ""

    # Status
    status: LeadStatus = LeadStatus.NEW
    source: str = ""

    # Activity
    calls: List[str] = field(default_factory=list)  # Call IDs
    appointments: List[str] = field(default_factory=list)  # Appointment IDs
    total_calls: int = 0
    last_contacted: Optional[datetime] = None
    next_callback: Optional[datetime] = None

    # Value
    total_revenue: float = 0.0
    lifetime_value: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Tags
    tags: List[str] = field(default_factory=list)
    notes: str = ""


# ═══════════════════════════════════════════════════════════════
# CRM ENGINE
# ═══════════════════════════════════════════════════════════════

class CRM:
    """
    Complete CRM for sales tracking.
    Tracks leads, calls, appointments, revenue, commissions.
    """

    def __init__(self, data_dir: str = "./crm_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage
        self.leads: Dict[str, CRMLead] = {}
        self.calls: Dict[str, CallLog] = {}
        self.appointments: Dict[str, Appointment] = {}
        self.commissions: Dict[str, Commission] = {}

        # Counters
        self._lead_counter = 0
        self._call_counter = 0
        self._apt_counter = 0
        self._comm_counter = 0

        # Load existing data
        self._load_data()

    def _generate_id(self, prefix: str, counter_name: str) -> str:
        """Generate unique ID"""
        counter = getattr(self, counter_name)
        setattr(self, counter_name, counter + 1)
        return f"{prefix}_{counter + 1:08d}"

    # ═══════════════════════════════════════════════════════════
    # LEAD MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def add_lead(
        self,
        business_name: str,
        phone: str,
        email: str = "",
        source: str = "",
        **kwargs
    ) -> CRMLead:
        """Add a new lead"""
        lead = CRMLead(
            id=self._generate_id("lead", "_lead_counter"),
            business_name=business_name,
            phone=phone,
            email=email,
            source=source,
            **kwargs
        )

        self.leads[lead.id] = lead
        self._save_data()
        return lead

    def get_lead(self, lead_id: str) -> Optional[CRMLead]:
        """Get lead by ID"""
        return self.leads.get(lead_id)

    def find_lead_by_phone(self, phone: str) -> Optional[CRMLead]:
        """Find lead by phone number"""
        # Normalize phone
        phone_digits = ''.join(filter(str.isdigit, phone))
        for lead in self.leads.values():
            lead_digits = ''.join(filter(str.isdigit, lead.phone))
            if phone_digits[-10:] == lead_digits[-10:]:  # Compare last 10 digits
                return lead
        return None

    def update_lead_status(self, lead_id: str, status: LeadStatus):
        """Update lead status"""
        lead = self.leads.get(lead_id)
        if lead:
            lead.status = status
            lead.updated_at = datetime.now()
            self._save_data()

    def get_leads_by_status(self, status: LeadStatus) -> List[CRMLead]:
        """Get all leads with specific status"""
        return [l for l in self.leads.values() if l.status == status]

    def get_callback_leads(self) -> List[CRMLead]:
        """Get leads that need callback"""
        now = datetime.now()
        return [
            l for l in self.leads.values()
            if l.next_callback and l.next_callback <= now
        ]

    # ═══════════════════════════════════════════════════════════
    # CALL LOGGING
    # ═══════════════════════════════════════════════════════════

    def log_call(
        self,
        lead_id: str,
        phone_number: str,
        direction: str,
        duration_seconds: int,
        outcome: str,
        notes: str = "",
        recording_url: str = "",
    ) -> CallLog:
        """Log a call"""
        call = CallLog(
            id=self._generate_id("call", "_call_counter"),
            lead_id=lead_id,
            phone_number=phone_number,
            direction=direction,
            duration_seconds=duration_seconds,
            outcome=outcome,
            notes=notes,
            recording_url=recording_url,
        )

        self.calls[call.id] = call

        # Update lead
        lead = self.leads.get(lead_id)
        if lead:
            lead.calls.append(call.id)
            lead.total_calls += 1
            lead.last_contacted = datetime.now()
            lead.updated_at = datetime.now()

        self._save_data()
        return call

    # ═══════════════════════════════════════════════════════════
    # APPOINTMENT MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def book_appointment(
        self,
        lead_id: str,
        scheduled_time: datetime,
        service_type: str = "",
        duration_minutes: int = 60,
        notes: str = "",
    ) -> Appointment:
        """Book an appointment"""
        apt = Appointment(
            id=self._generate_id("apt", "_apt_counter"),
            lead_id=lead_id,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            service_type=service_type,
            notes=notes,
        )

        self.appointments[apt.id] = apt

        # Update lead
        lead = self.leads.get(lead_id)
        if lead:
            lead.appointments.append(apt.id)
            lead.status = LeadStatus.APPOINTMENT_SET
            lead.updated_at = datetime.now()

        self._save_data()
        return apt

    def confirm_appointment(self, apt_id: str):
        """Confirm an appointment"""
        apt = self.appointments.get(apt_id)
        if apt:
            apt.status = AppointmentStatus.CONFIRMED
            apt.confirmed_at = datetime.now()
            self._save_data()

    def complete_appointment(self, apt_id: str, revenue: float):
        """Mark appointment as completed with revenue"""
        apt = self.appointments.get(apt_id)
        if apt:
            apt.status = AppointmentStatus.COMPLETED
            apt.completed_at = datetime.now()
            apt.revenue = revenue

            # Update lead
            lead = self.leads.get(apt.lead_id)
            if lead:
                lead.status = LeadStatus.CLOSED_WON
                lead.total_revenue += revenue
                lead.lifetime_value += revenue

            # Create commission
            self._create_commission(apt)

            self._save_data()

    def get_upcoming_appointments(self, days: int = 7) -> List[Appointment]:
        """Get appointments in the next N days"""
        now = datetime.now()
        cutoff = now + timedelta(days=days)

        return [
            apt for apt in self.appointments.values()
            if apt.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
            and now <= apt.scheduled_time <= cutoff
        ]

    # ═══════════════════════════════════════════════════════════
    # COMMISSION TRACKING
    # ═══════════════════════════════════════════════════════════

    def _create_commission(self, apt: Appointment):
        """Create commission record for completed appointment"""
        commission_rate = 0.10  # 10%
        commission_amount = apt.revenue * commission_rate
        client_amount = apt.revenue - commission_amount

        commission = Commission(
            id=self._generate_id("comm", "_comm_counter"),
            lead_id=apt.lead_id,
            appointment_id=apt.id,
            total_revenue=apt.revenue,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            client_amount=client_amount,
        )

        self.commissions[commission.id] = commission

    def get_commission_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get commission summary for period"""
        commissions = list(self.commissions.values())

        if start_date:
            commissions = [c for c in commissions if c.created_at >= start_date]
        if end_date:
            commissions = [c for c in commissions if c.created_at <= end_date]

        total_revenue = sum(c.total_revenue for c in commissions)
        total_commission = sum(c.commission_amount for c in commissions)
        total_client = sum(c.client_amount for c in commissions)

        return {
            "total_appointments": len(commissions),
            "total_revenue": total_revenue,
            "commission_amount": total_commission,
            "client_amount": total_client,
            "commission_rate": 0.10,
        }

    # ═══════════════════════════════════════════════════════════
    # ANALYTICS
    # ═══════════════════════════════════════════════════════════

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get sales pipeline summary"""
        summary = {status.value: 0 for status in LeadStatus}

        for lead in self.leads.values():
            summary[lead.status.value] += 1

        return summary

    def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """Get stats for a specific day"""
        date = date or datetime.now()
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        calls_today = [
            c for c in self.calls.values()
            if start <= c.created_at < end
        ]

        apts_today = [
            a for a in self.appointments.values()
            if start <= a.created_at < end
        ]

        return {
            "date": start.strftime("%Y-%m-%d"),
            "calls_made": len(calls_today),
            "total_talk_time": sum(c.duration_seconds for c in calls_today),
            "appointments_booked": len(apts_today),
            "conversion_rate": len(apts_today) / max(1, len(calls_today)),
        }

    def get_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Get performance report for last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        calls = [c for c in self.calls.values() if c.created_at >= start_date]
        apts = [a for a in self.appointments.values() if a.created_at >= start_date]
        completed = [a for a in apts if a.status == AppointmentStatus.COMPLETED]

        total_revenue = sum(a.revenue for a in completed)
        commission = total_revenue * 0.10

        return {
            "period_days": days,
            "total_calls": len(calls),
            "total_appointments": len(apts),
            "completed_appointments": len(completed),
            "total_revenue": total_revenue,
            "commission_earned": commission,
            "client_earnings": total_revenue - commission,
            "calls_per_day": len(calls) / days,
            "apts_per_day": len(apts) / days,
            "conversion_rate": len(apts) / max(1, len(calls)),
            "avg_deal_size": total_revenue / max(1, len(completed)),
        }

    # ═══════════════════════════════════════════════════════════
    # PERSISTENCE
    # ═══════════════════════════════════════════════════════════

    def _save_data(self):
        """Save all data to disk"""
        data = {
            "leads": {k: self._serialize(v) for k, v in self.leads.items()},
            "calls": {k: self._serialize(v) for k, v in self.calls.items()},
            "appointments": {k: self._serialize(v) for k, v in self.appointments.items()},
            "commissions": {k: self._serialize(v) for k, v in self.commissions.items()},
            "counters": {
                "lead": self._lead_counter,
                "call": self._call_counter,
                "apt": self._apt_counter,
                "comm": self._comm_counter,
            },
        }

        filepath = self.data_dir / "crm_data.json"
        filepath.write_text(json.dumps(data, indent=2, default=str))

    def _load_data(self):
        """Load data from disk"""
        filepath = self.data_dir / "crm_data.json"
        if not filepath.exists():
            return

        try:
            data = json.loads(filepath.read_text())
            # Restore counters
            counters = data.get("counters", {})
            self._lead_counter = counters.get("lead", 0)
            self._call_counter = counters.get("call", 0)
            self._apt_counter = counters.get("apt", 0)
            self._comm_counter = counters.get("comm", 0)
        except Exception as e:
            print(f"  [!] Error loading CRM data: {e}")

    def _serialize(self, obj) -> Dict:
        """Serialize dataclass to dict"""
        data = asdict(obj) if hasattr(obj, '__dataclass_fields__') else obj
        # Convert enums
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    # ═══════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════

    def export_report(self, filepath: str):
        """Export full report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "pipeline": self.get_pipeline_summary(),
            "performance": self.get_performance_report(30),
            "commissions": self.get_commission_summary(),
            "upcoming_appointments": len(self.get_upcoming_appointments()),
        }

        Path(filepath).write_text(json.dumps(report, indent=2))


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    """Demo the CRM"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                          CRM                                  ║
║                                                               ║
║   Lead tracking, appointments, commissions                    ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    crm = CRM()

    # Add test lead
    lead = crm.add_lead(
        business_name="Cool Air HVAC",
        phone="+1-555-0100",
        email="info@coolair.com",
        source="scraper",
    )
    print(f"Added lead: {lead.business_name} ({lead.id})")

    # Log a call
    call = crm.log_call(
        lead_id=lead.id,
        phone_number=lead.phone,
        direction="outbound",
        duration_seconds=180,
        outcome="interested",
    )
    print(f"Logged call: {call.id} ({call.outcome})")

    # Book appointment
    apt = crm.book_appointment(
        lead_id=lead.id,
        scheduled_time=datetime.now() + timedelta(days=2),
        service_type="demo",
    )
    print(f"Booked appointment: {apt.id}")

    # Show pipeline
    print(f"\nPipeline: {crm.get_pipeline_summary()}")

    # Show performance
    perf = crm.get_performance_report(30)
    print(f"\nPerformance (30 days):")
    print(f"  Calls: {perf['total_calls']}")
    print(f"  Appointments: {perf['total_appointments']}")
    print(f"  Revenue: ${perf['total_revenue']:.2f}")
    print(f"  Commission: ${perf['commission_earned']:.2f}")


if __name__ == "__main__":
    main()
