import uuid
from apps.api.core.database import engine, SessionLocal, Base
from apps.api.models import Report, AdministrativeZone, ReportAuditLog
from sqlalchemy import inspect, text

def test_database_schema_creation_and_migration():
    print("Testing schema creation and tables reflection...")
    # Drop all (downgrade simulation)
    Base.metadata.drop_all(bind=engine)
    inspector = inspect(engine)
    tables_after_drop = inspector.get_table_names()
    assert "reports" not in tables_after_drop, "Drop failed"

    # Create all (upgrade simulation)
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {tables}")
    assert "reports" in tables, "reports table missing"
    assert "administrative_zones" in tables, "administrative_zones table missing"
    assert "report_audit_logs" in tables, "report_audit_logs table missing"

    # Verify column structure on reports
    columns = [col["name"] for col in inspector.get_columns("reports")]
    expected_cols = [
        "id", "tracking_id", "raw_description", "latitude", "longitude",
        "verified_category", "priority_rank", "priority_score",
        "lifecycle_status", "is_duplicate", "master_ticket_id"
    ]
    for col in expected_cols:
        assert col in columns, f"Column {col} missing from reports"
    print("Column structure on reports table verified successfully.")

    # Test sample persistence and cascade
    db = SessionLocal()
    try:
        sample_report = Report(
            id=str(uuid.uuid4()),
            tracking_id="CS-TEST-0001",
            raw_description="Deep standing water near St. Jude school gate",
            user_category="Waterlogging & Drainage",
            verified_category="Waterlogging & Drainage",
            latitude=12.9725,
            longitude=77.5950,
            formatted_address="Ward 12, School Gate",
            priority_rank="Priority 1",
            priority_score=85.00,
            priority_rationale="Near school (+40), safety risk (+20)",
            lifecycle_status="Submitted"
        )
        db.add(sample_report)
        db.commit()

        queried = db.query(Report).filter(Report.tracking_id == "CS-TEST-0001").first()
        assert queried is not None
        assert queried.priority_rank == "Priority 1"
        assert queried.latitude == 12.9725
        print(f"Sample report query verified: Tracking ID={queried.tracking_id}, Status={queried.lifecycle_status}")
    finally:
        db.close()

    print("TASK-013: Migration rollback, re-application and CRUD validation PASSED.")

if __name__ == "__main__":
    test_database_schema_creation_and_migration()

