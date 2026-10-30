import uuid
from apps.api.core.database import engine, SessionLocal, Base
from apps.api.models import Report, AdministrativeZone
from apps.api.seeds.report_factory import generate_synthetic_reports
from apps.api.seeds.geo_constants import calculate_haversine_distance, ANCHOR_POIS

def seed_database():
    print("=" * 60)
    print("CITYSENSE: SEEDING SYNTHETIC DATASET (PHASE 3)")
    print("=" * 60)

    # 1. Ensure schema is initialized
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 2. Seed Administrative Hierarchy
        db.query(AdministrativeZone).delete()
        
        city = AdministrativeZone(
            id=str(uuid.uuid4()),
            name="Metropolis City",
            level="City",
            parent_id=None
        )
        db.add(city)
        db.flush()

        division = AdministrativeZone(
            id=str(uuid.uuid4()),
            name="Central Division",
            level="Division",
            parent_id=city.id
        )
        db.add(division)
        db.flush()

        zone = AdministrativeZone(
            id=str(uuid.uuid4()),
            name="East Zone",
            level="Zone",
            parent_id=division.id
        )
        db.add(zone)
        db.flush()

        ward12 = AdministrativeZone(
            id=str(uuid.uuid4()),
            name="Ward 12",
            level="Ward",
            parent_id=zone.id
        )
        db.add(ward12)
        db.flush()
        print(f"Administrative Hierarchy created: {city.name} -> {division.name} -> {zone.name} -> {ward12.name}")

        # 3. Seed Synthetic Reports
        db.query(Report).delete()
        reports_data = generate_synthetic_reports()

        for item in reports_data:
            report_obj = Report(
                id=item["id"],
                tracking_id=item["tracking_id"],
                created_at=item["created_at"],
                raw_description=item["raw_description"],
                user_category=item["user_category"],
                verified_category=item["verified_category"],
                media_url=item["media_url"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                formatted_address=item["formatted_address"],
                concise_summary=item["concise_summary"],
                is_duplicate=item["is_duplicate"],
                master_ticket_id=item["master_ticket_id"],
                duplicate_count=item["duplicate_count"],
                priority_rank=item["priority_rank"],
                priority_score=item["priority_score"],
                priority_rationale=item["priority_rationale"],
                lifecycle_status=item["lifecycle_status"],
                assigned_department=item["assigned_department"],
            )
            db.add(report_obj)

        db.commit()
        total_count = db.query(Report).count()
        print(f"\nSuccessfully seeded {total_count} reports into database.")

        # 4. Statistical Verification & Categorization Breakdown
        categories = {}
        priorities = {}
        duplicate_count = 0
        master_tickets_with_duplicates = 0

        for r in db.query(Report).all():
            cat = r.verified_category
            categories[cat] = categories.get(cat, 0) + 1
            priorities[r.priority_rank] = priorities.get(r.priority_rank, 0) + 1
            if r.is_duplicate:
                duplicate_count += 1
            if r.duplicate_count > 1 and not r.is_duplicate:
                master_tickets_with_duplicates += 1

        print("\n--- CATEGORY DISTRIBUTION (Target: 30% Drainage, 30% Roads, 20% Waste, 10% Light, 10% Util) ---")
        for cat, cnt in sorted(categories.items()):
            pct = (cnt / total_count) * 100
            print(f"  {cat:<28}: {cnt:>2} reports ({pct:.1f}%)")

        print("\n--- PRIORITY BREAKDOWN ---")
        for p, cnt in sorted(priorities.items()):
            print(f"  {p:<15}: {cnt:>2} reports")

        print(f"\n--- DUPLICATE CLUSTERING ---")
        print(f"  Master tickets with linked duplicates : {master_tickets_with_duplicates}")
        print(f"  Total child duplicate reports linked  : {duplicate_count}")

        # Proximity Verification for Hazards
        h1 = db.query(Report).filter(Report.tracking_id == "CS-HAZD-1001").first()
        dist_to_school = calculate_haversine_distance(
            h1.latitude, h1.longitude,
            ANCHOR_POIS["st_jude_school"]["latitude"], ANCHOR_POIS["st_jude_school"]["longitude"]
        )
        print(f"\n--- HAZARD PROXIMITY VERIFICATION ---")
        print(f"  Hazard 1 distance to St. Jude School: {dist_to_school:.1f} meters (< 20m target)")

        return total_count

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

