"""Emergency Incident Management Store and Workflow for AAGAAH.

Enables District Emergency Operations Centre (DEOC) operators to:
- Track active flash flood and debris flow incidents
- Transition lifecycle: NEW -> UNDER_REVIEW -> VERIFIED -> MONITORING -> RESOLVED
- Maintain an audit trail of operator actions and field verification checks
"""
from datetime import datetime, timezone
from enum import StrEnum
import threading
import uuid
from pydantic import BaseModel, Field

class IncidentStatus(StrEnum):
    NEW = 'NEW'
    UNDER_REVIEW = 'UNDER_REVIEW'
    VERIFIED = 'VERIFIED'
    MONITORING = 'MONITORING'
    RESOLVED = 'RESOLVED'

class IncidentSeverity(StrEnum):
    P1_CRITICAL = 'P1_CRITICAL'
    P2_HIGH = 'P2_HIGH'
    P3_MEDIUM = 'P3_MEDIUM'
    P4_LOW = 'P4_LOW'

class IncidentCreate(BaseModel):
    location_id: str
    location_name: str
    title: str
    severity: IncidentSeverity = IncidentSeverity.P2_HIGH
    summary: str
    operator_notes: str = ''
    reported_by: str = 'DEOC Operator'

class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    severity: IncidentSeverity | None = None
    operator_notes: str | None = None
    verification_details: str | None = None
    updated_by: str = 'Duty Officer'

class IncidentRecord(BaseModel):
    id: str
    location_id: str
    location_name: str
    title: str
    severity: IncidentSeverity
    status: IncidentStatus
    summary: str
    operator_notes: str
    reported_by: str
    created_at: str
    updated_at: str
    audit_log: list[dict] = Field(default_factory=list)

class IncidentStore:
    def __init__(self):
        self._lock = threading.RLock()
        self._incidents: dict[str, IncidentRecord] = {}
        self._seed_default_incidents()

    def _seed_default_incidents(self):
        now = datetime.now(timezone.utc).isoformat()
        seed_1 = IncidentRecord(
            id='INC-2026-001',
            location_id='sonprayag',
            location_name='Sonprayag Confluence Reach',
            title='Upstream Runoff Surge Monitoring at Mandakini-Songanga Confluence',
            severity=IncidentSeverity.P2_HIGH,
            status=IncidentStatus.MONITORING,
            summary='Elevated upstream rainfall at Gaurikund and Kedarnath propagating into Sonprayag narrow gorge. Pedestrian bridge corridor under observation.',
            operator_notes='Gaurikund barrier team alerted; pilgrim holding area in Sonprayag bazaar informed to maintain standby.',
            reported_by='DEOC Rudraprayag',
            created_at=now,
            updated_at=now,
            audit_log=[
                {'timestamp': now, 'action': 'CREATED', 'actor': 'System Sentinel', 'details': 'Automated advisory escalation based on Warning alert level'},
                {'timestamp': now, 'action': 'STATUS_CHANGE', 'actor': 'Duty Officer Sharma', 'details': 'Moved from NEW to MONITORING following field radio contact'}
            ]
        )
        seed_2 = IncidentRecord(
            id='INC-2026-002',
            location_id='guptkashi',
            location_name='Guptkashi Valley Approach',
            title='Culvert Scour and Road Access Check on NH-107',
            severity=IncidentSeverity.P3_MEDIUM,
            status=IncidentStatus.UNDER_REVIEW,
            summary='Rainfall rate exceeding 15 mm/h on steep roadside slopes. BRO patrol dispatched to inspect drainage culvert at km 34.',
            operator_notes='Patrol vehicle en route; transit traffic moving under caution.',
            reported_by='DDMA Garhwal',
            created_at=now,
            updated_at=now,
            audit_log=[
                {'timestamp': now, 'action': 'CREATED', 'actor': 'DDMA Dispatch', 'details': 'Report logged from traffic police check post'}
            ]
        )
        self._incidents[seed_1.id] = seed_1
        self._incidents[seed_2.id] = seed_2

    def list_all(self) -> list[IncidentRecord]:
        with self._lock:
            return sorted(self._incidents.values(), key=lambda i: i.created_at, reverse=True)

    def list(self) -> list[IncidentRecord]:
        return self.list_all()

    def get(self, incident_id: str) -> IncidentRecord | None:
        with self._lock:
            return self._incidents.get(incident_id)

    def create(self, data: IncidentCreate) -> IncidentRecord:
        with self._lock:
            now = datetime.now(timezone.utc).isoformat()
            new_id = f"INC-2026-{len(self._incidents) + 1:03d}"
            record = IncidentRecord(
                id=new_id,
                location_id=data.location_id,
                location_name=data.location_name,
                title=data.title,
                severity=data.severity,
                status=IncidentStatus.NEW,
                summary=data.summary,
                operator_notes=data.operator_notes,
                reported_by=data.reported_by,
                created_at=now,
                updated_at=now,
                audit_log=[
                    {'timestamp': now, 'action': 'CREATED', 'actor': data.reported_by, 'details': 'Incident initiated from operational dashboard'}
                ]
            )
            self._incidents[new_id] = record
            return record

    def update(self, incident_id: str, data: IncidentUpdate) -> IncidentRecord | None:
        with self._lock:
            record = self._incidents.get(incident_id)
            if not record:
                return None
            now = datetime.now(timezone.utc).isoformat()
            if data.status and data.status != record.status:
                record.audit_log.append({
                    'timestamp': now,
                    'action': 'STATUS_CHANGE',
                    'actor': data.updated_by,
                    'details': f"Status changed from {record.status} to {data.status}"
                })
                record.status = data.status
            if data.severity and data.severity != record.severity:
                record.audit_log.append({
                    'timestamp': now,
                    'action': 'SEVERITY_CHANGE',
                    'actor': data.updated_by,
                    'details': f"Severity changed from {record.severity} to {data.severity}"
                })
                record.severity = data.severity
            if data.operator_notes:
                record.operator_notes = (record.operator_notes + "\n" + data.operator_notes).strip()
            if data.verification_details:
                record.audit_log.append({
                    'timestamp': now,
                    'action': 'VERIFICATION_LOG',
                    'actor': data.updated_by,
                    'details': data.verification_details
                })
            record.updated_at = now
            return record

INCIDENT_STORE = IncidentStore()
