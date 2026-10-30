from apps.api.core.database import SessionLocal
from apps.api.models import Report, AdministrativeZone
from apps.api.seeds.geo_constants import calculate_haversine_distance, ANCHOR_POIS

def test_phase_3_synthetic_dataset_integrity():
    db = SessionLocal()
    try:
        # TASK-014: Administrative Hierarchy & Anchors
        zones = db.query(AdministrativeZone).all()
        assert len(zones) >= 4, "Administrative hierarchy levels missing"
        ward12 = db.query(AdministrativeZone).filter(AdministrativeZone.level == "Ward").first()
        assert ward12.name == "Ward 12", "Ward 12 missing"

        # TASK-015: 40 reports with exact category distribution
        total = db.query(Report).count()
        assert total == 40, f"Expected 40 reports, found {total}"

        counts = {}
        for r in db.query(Report).all():
            counts[r.verified_category] = counts.get(r.verified_category, 0) + 1

        assert counts["Waterlogging & Drainage"] == 12, "Waterlogging quota mismatch (expected 12 / 30%)"
        assert counts["Road Failure & Potholes"] == 12, "Road Failure quota mismatch (expected 12 / 30%)"
        assert counts["Waste Management"] == 8, "Waste Management quota mismatch (expected 8 / 20%)"
        assert counts["Street Lighting"] == 4, "Street Lighting quota mismatch (expected 4 / 10%)"
        assert counts["Public Utilities"] == 4, "Public Utilities quota mismatch (expected 4 / 10%)"

        # TASK-016: Deliberate Duplicates (3 Clusters, 5 children)
        duplicates = db.query(Report).filter(Report.is_duplicate == True).all()
        assert len(duplicates) == 5, f"Expected 5 child duplicates, got {len(duplicates)}"
        master_ids = set(d.master_ticket_id for d in duplicates)
        assert len(master_ids) == 3, f"Expected 3 distinct master tickets, got {len(master_ids)}"

        # TASK-017: 2 High Priority Hazards
        hazards = db.query(Report).filter(Report.priority_rank == "Priority 1").all()
        assert len(hazards) == 2, f"Expected 2 Priority 1 hazards, got {len(hazards)}"
        h1 = db.query(Report).filter(Report.tracking_id == "CS-HAZD-1001").first()
        d_school = calculate_haversine_distance(
            h1.latitude, h1.longitude,
            ANCHOR_POIS["st_jude_school"]["latitude"], ANCHOR_POIS["st_jude_school"]["longitude"]
        )
        assert d_school < 25.0, f"Hazard 1 should be < 25m from school, got {d_school}"

        # TASK-018: MG Road Hotspot Corridor (8 interconnected reports)
        corridor_reports = db.query(Report).filter(Report.tracking_id.like("CS-HOT-%")).all()
        assert len(corridor_reports) == 8, f"Expected 8 hotspot reports, got {len(corridor_reports)}"

        # Verify all 8 reports are within 100 meters of corridor center
        center_lat, center_lon = 12.9740, 77.5960
        for cr in corridor_reports:
            dist = calculate_haversine_distance(cr.latitude, cr.longitude, center_lat, center_lon)
            assert dist <= 100.0, f"Report {cr.tracking_id} outside 100m cluster ({dist}m)"

        print("ALL PHASE 3 SYNTHETIC DATASET INTEGRITY CHECKS PASSED.")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase_3_synthetic_dataset_integrity()

