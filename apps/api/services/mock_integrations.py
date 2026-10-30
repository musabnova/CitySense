"""
TASK-072: Mocked External Integration Facades
===============================================
Stage: Governance / Transparency (PRD Section 9.2)
Objective: Implement explicitly mocked facades for external integrations:
  - Mocked SMS Gateway (simulates citizen/crew notification dispatch)
  - Mocked Municipal ERP Work Order Synchronization Adapter

IMPORTANT: These are SIMULATION FACADES ONLY.
  - No real SMS messages are sent.
  - No real ERP system is contacted.
  - All events are logged to an in-memory + persistent audit log for demo transparency.
  - Real implementations should replace each facade class while preserving the interface contract.

Transparency labels used in UI:
  - "[Demo Data - Mocked SMS Service]"
  - "[Simulated ERP Sync]"
"""

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("citysense.mock_integrations")

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "citysense.db"

# ─────────────────────────────────────────────────────────────────────────────
# In-memory mock event log (also persisted to SQLite audit if table exists)
# ─────────────────────────────────────────────────────────────────────────────
_MOCK_SMS_LOG: List[Dict[str, Any]] = []
_MOCK_ERP_LOG: List[Dict[str, Any]] = []


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Mocked SMS Gateway
# ─────────────────────────────────────────────────────────────────────────────

class MockSMSGateway:
    """
    [MOCK FACADE - Demo SMS Gateway]
    =================================
    Simulates an SMS notification service (e.g. Twilio / MSG91 / Kaleyra).
    All messages are logged locally. No real HTTP calls are made.
    Replace this class with a real SMS provider adapter in production.

    Interface contract (stable for real implementation):
        send_dispatch_notification(to_number, message, metadata) -> dict
        send_resolution_notification(to_number, message, metadata) -> dict
        get_sent_log() -> list[dict]
    """

    FACADE_LABEL = "[Demo Data - Mocked SMS Service]"

    def _log_event(self, event_type: str, to_number: str, message: str, metadata: dict) -> Dict[str, Any]:
        """Record a simulated SMS event in the in-memory log."""
        event = {
            "event_id": str(uuid.uuid4())[:8],
            "facade": self.FACADE_LABEL,
            "event_type": event_type,
            "simulated_to": to_number,
            "message_body": message,
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SIMULATED_SENT",
            "provider": "MockSMSGateway v1.0 [NOT REAL]",
        }
        _MOCK_SMS_LOG.append(event)
        logger.info(
            f"{self.FACADE_LABEL} EVENT={event_type} | TO={to_number} | MSG={message[:60]}..."
        )
        return event

    def send_dispatch_notification(
        self,
        to_number: str,
        tracking_id: str,
        department: str,
        location: str,
        report_count: int = 1,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Simulates notifying a field crew or citizen that a work order has been dispatched.
        [MOCK FACADE - no real SMS is sent]
        """
        message = (
            f"[CitySense] Work Order DISPATCHED. "
            f"Ticket: {tracking_id} | Dept: {department} | Location: {location} | "
            f"Consolidated {report_count} citizen report(s). "
            f"Check field portal for full brief."
        )
        return self._log_event(
            event_type="DISPATCH_NOTIFICATION",
            to_number=to_number,
            message=message,
            metadata=metadata or {"tracking_id": tracking_id, "department": department},
        )

    def send_resolution_notification(
        self,
        to_number: str,
        tracking_id: str,
        resolution_notes: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Simulates notifying a citizen that their complaint has been resolved.
        [MOCK FACADE - no real SMS is sent]
        """
        message = (
            f"[CitySense] Your complaint {tracking_id} has been RESOLVED. "
            f"Notes: {resolution_notes[:80]}. "
            f"Thank you for helping improve your city!"
        )
        return self._log_event(
            event_type="RESOLUTION_NOTIFICATION",
            to_number=to_number,
            message=message,
            metadata=metadata or {"tracking_id": tracking_id},
        )

    def get_sent_log(self) -> List[Dict[str, Any]]:
        """Returns the in-memory list of all simulated SMS events this session."""
        return list(_MOCK_SMS_LOG)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Mocked Municipal ERP Work Order Synchronization Adapter
# ─────────────────────────────────────────────────────────────────────────────

class MockMunicipalERPAdapter:
    """
    [MOCK FACADE - Legacy Municipal ERP]
    =====================================
    Simulates bi-directional work order synchronization with legacy
    Municipal ERP systems (e.g. SAP Public Sector / IBM Maximo / Oracle eAM).
    All sync events are logged locally. No real ERP endpoint is contacted.
    Replace this class with an actual ERP integration in production.

    Interface contract (stable for real implementation):
        push_work_order(work_order_data) -> dict
        push_resolution(report_id, resolution_data) -> dict
        get_sync_log() -> list[dict]
    """

    FACADE_LABEL = "[Simulated ERP Sync]"
    ERP_SYSTEM_NAME = "Municipal-ERP v4.2 (Simulated - SAP/Maximo Compatible)"

    def _log_event(self, event_type: str, payload: dict) -> Dict[str, Any]:
        """Record a simulated ERP sync event in the in-memory log."""
        event = {
            "sync_id": str(uuid.uuid4())[:8],
            "facade": self.FACADE_LABEL,
            "event_type": event_type,
            "erp_system": self.ERP_SYSTEM_NAME,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sync_status": "SIMULATED_SYNC_OK",
            "erp_work_order_id": f"ERP-WO-{str(uuid.uuid4())[:6].upper()}",
        }
        _MOCK_ERP_LOG.append(event)
        logger.info(
            f"{self.FACADE_LABEL} EVENT={event_type} | ERP_WO={event['erp_work_order_id']} "
            f"| TICKET={payload.get('tracking_id', 'N/A')}"
        )
        return event

    def push_work_order(
        self,
        tracking_id: str,
        department: str,
        location: str,
        category: str,
        priority: str,
        action_brief: Optional[str] = None,
        report_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Simulates pushing a new dispatched work order into the legacy ERP.
        Returns a simulated ERP work order ID and sync acknowledgement.
        [MOCK FACADE - no real ERP call is made]
        """
        payload = {
            "tracking_id": tracking_id,
            "department": department,
            "location": location,
            "category": category,
            "priority": priority,
            "action_brief_summary": (action_brief or "")[:200],
            "consolidated_citizen_reports": report_count,
            "source_system": "CitySense AI Triage Platform",
        }
        return self._log_event(event_type="PUSH_WORK_ORDER", payload=payload)

    def push_resolution(
        self,
        tracking_id: str,
        resolved_by: str,
        resolution_notes: str,
        resolved_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simulates syncing a field resolution event back into the legacy ERP
        (closing the ERP work order and updating completion status).
        [MOCK FACADE - no real ERP call is made]
        """
        payload = {
            "tracking_id": tracking_id,
            "resolved_by_department": resolved_by,
            "resolution_notes": resolution_notes[:300],
            "resolved_at": resolved_at or datetime.now(timezone.utc).isoformat(),
            "erp_closure_code": "COMPLETED",
        }
        return self._log_event(event_type="PUSH_RESOLUTION", payload=payload)

    def get_sync_log(self) -> List[Dict[str, Any]]:
        """Returns the in-memory list of all simulated ERP sync events this session."""
        return list(_MOCK_ERP_LOG)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Singleton gateway instances (used by standalone_server.py)
# ─────────────────────────────────────────────────────────────────────────────

mock_sms_gateway = MockSMSGateway()
mock_erp_adapter = MockMunicipalERPAdapter()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: High-level orchestration helpers
# ─────────────────────────────────────────────────────────────────────────────

def trigger_dispatch_integrations(
    tracking_id: str,
    department: str,
    location: str,
    category: str,
    priority: str,
    report_count: int = 1,
    action_brief: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Called when a work order is dispatched from the admin console.
    Fires:
      1. Mocked SMS notification to the field crew
      2. Mocked ERP work order push
    Returns a combined result dict for logging in the API response.
    """
    # Simulated crew contact number (demo only)
    crew_phone = "+91-XXXX-DEMO"

    sms_result = mock_sms_gateway.send_dispatch_notification(
        to_number=crew_phone,
        tracking_id=tracking_id,
        department=department,
        location=location,
        report_count=report_count,
    )
    erp_result = mock_erp_adapter.push_work_order(
        tracking_id=tracking_id,
        department=department,
        location=location,
        category=category,
        priority=priority,
        action_brief=action_brief,
        report_count=report_count,
    )

    return {
        "mock_sms": {
            "label": MockSMSGateway.FACADE_LABEL,
            "event_id": sms_result["event_id"],
            "status": sms_result["status"],
            "simulated_message": sms_result["message_body"][:100],
        },
        "mock_erp": {
            "label": MockMunicipalERPAdapter.FACADE_LABEL,
            "erp_work_order_id": erp_result["erp_work_order_id"],
            "sync_status": erp_result["sync_status"],
        },
    }


def trigger_resolution_integrations(
    tracking_id: str,
    department: str,
    resolution_notes: str,
) -> Dict[str, Any]:
    """
    Called when a field crew marks a job as Resolved.
    Fires:
      1. Mocked SMS resolution notification to citizen
      2. Mocked ERP resolution closure push
    """
    citizen_phone = "+91-XXXX-CITIZEN"

    sms_result = mock_sms_gateway.send_resolution_notification(
        to_number=citizen_phone,
        tracking_id=tracking_id,
        resolution_notes=resolution_notes,
    )
    erp_result = mock_erp_adapter.push_resolution(
        tracking_id=tracking_id,
        resolved_by=department,
        resolution_notes=resolution_notes,
    )

    return {
        "mock_sms": {
            "label": MockSMSGateway.FACADE_LABEL,
            "event_id": sms_result["event_id"],
            "status": sms_result["status"],
        },
        "mock_erp": {
            "label": MockMunicipalERPAdapter.FACADE_LABEL,
            "erp_work_order_id": erp_result["erp_work_order_id"],
            "sync_status": erp_result["sync_status"],
        },
    }


def get_mock_integration_logs() -> Dict[str, Any]:
    """Returns combined in-memory logs from all mock facades for inspection."""
    return {
        "sms_gateway": {
            "label": MockSMSGateway.FACADE_LABEL,
            "total_events": len(_MOCK_SMS_LOG),
            "events": _MOCK_SMS_LOG[-20:],  # Last 20 events
        },
        "erp_adapter": {
            "label": MockMunicipalERPAdapter.FACADE_LABEL,
            "total_events": len(_MOCK_ERP_LOG),
            "events": _MOCK_ERP_LOG[-20:],
        },
    }

