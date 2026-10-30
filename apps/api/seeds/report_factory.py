import uuid
from datetime import datetime, timezone, timedelta
from apps.api.seeds.geo_constants import ANCHOR_POIS, WARD_12_CENTER, calculate_haversine_distance

def generate_synthetic_reports():
    now = datetime.now(timezone.utc)
    reports = []

    # =========================================================================
    # TASK-017: High-Priority Safety Hazard & Proximity Edge Cases (2 Reports)
    # =========================================================================
    
    # Hazard 1: Exposed electrical conduit in standing water near St. Jude School Gate (~15m from school)
    h1_lat = ANCHOR_POIS["st_jude_school"]["latitude"] + 0.0001
    h1_lon = ANCHOR_POIS["st_jude_school"]["longitude"] + 0.0001
    h1_id = str(uuid.uuid4())
    reports.append({
        "id": h1_id,
        "tracking_id": "CS-HAZD-1001",
        "created_at": now - timedelta(hours=2),
        "raw_description": "Exposed live electrical conduit submerged in standing flood water directly outside St. Jude School Gate. Immediate danger of electrocution for students.",
        "user_category": "Public Utilities",
        "verified_category": "Public Utilities",
        "media_url": "/demo-media/live_wire_water.jpg",
        "latitude": h1_lat,
        "longitude": h1_lon,
        "formatted_address": "Opposite St. Jude Primary School Gate, Ward 12",
        "concise_summary": "Submerged live electrical line in standing water at school gate",
        "is_duplicate": False,
        "master_ticket_id": None,
        "duplicate_count": 1,
        "priority_rank": "Priority 1",
        "priority_score": 95.0,
        "priority_rationale": "Ranked Priority 1 (Critical). Rationale: Extreme safety threat of electrocution due to live utility wire in standing water within 15 meters of St. Jude School Zone.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Hazard 2: Open manhole on emergency ambulance access lane near City Central Hospital (~22m from hospital)
    h2_lat = ANCHOR_POIS["city_central_hospital"]["latitude"] - 0.00015
    h2_lon = ANCHOR_POIS["city_central_hospital"]["longitude"] + 0.0001
    h2_id = str(uuid.uuid4())
    reports.append({
        "id": h2_id,
        "tracking_id": "CS-HAZD-1002",
        "created_at": now - timedelta(hours=4),
        "raw_description": "Deep open manhole missing its concrete slab directly on the narrow ambulance emergency access road to City Central Hospital.",
        "user_category": "Road Failure & Potholes",
        "verified_category": "Road Failure & Potholes",
        "media_url": "/demo-media/open_manhole.jpg",
        "latitude": h2_lat,
        "longitude": h2_lon,
        "formatted_address": "Hospital Emergency Road, Ward 12",
        "concise_summary": "Missing manhole cover obstructing hospital emergency access corridor",
        "is_duplicate": False,
        "master_ticket_id": None,
        "duplicate_count": 1,
        "priority_rank": "Priority 1",
        "priority_score": 90.0,
        "priority_rationale": "Ranked Priority 1 (Critical). Rationale: Life safety hazard from open deep chamber on emergency medical vehicle transit route (< 25m from hospital).",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # =========================================================================
    # TASK-016: Deliberate Duplicate Reports Clusters (3 Clusters = 8 Reports)
    # =========================================================================

    # Cluster A: Flooded intersection at Market Gate (Master + 2 Duplicates within 30m)
    c1_master_id = str(uuid.uuid4())
    c1_lat, c1_lon = 12.9710, 77.5940
    reports.append({
        "id": c1_master_id,
        "tracking_id": "CS-DUPL-2001",
        "created_at": now - timedelta(hours=10),
        "raw_description": "Severe road flooding and knee-deep standing water at Market Gate intersection. Vehicles cannot pass.",
        "user_category": "Waterlogging & Drainage",
        "verified_category": "Waterlogging & Drainage",
        "media_url": "/demo-media/market_flood_1.jpg",
        "latitude": c1_lat,
        "longitude": c1_lon,
        "formatted_address": "Market Gate Cross, Ward 12",
        "concise_summary": "Knee-deep road waterlogging blocking Market Gate intersection",
        "is_duplicate": False,
        "master_ticket_id": None,
        "duplicate_count": 3,
        "priority_rank": "Priority 2",
        "priority_score": 68.0,
        "priority_rationale": "Ranked Priority 2 (High). Rationale: Arterial traffic blockage with 2 linked citizen duplicates logged within 30 meters.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Duplicate A.1
    reports.append({
        "id": str(uuid.uuid4()),
        "tracking_id": "CS-DUPL-2002",
        "created_at": now - timedelta(hours=7),
        "raw_description": "Huge pool of dirty rainwater stuck at the market corner, cars are getting submerged up to tyres.",
        "user_category": "Waterlogging & Drainage",
        "verified_category": "Waterlogging & Drainage",
        "media_url": "/demo-media/market_flood_2.jpg",
        "latitude": c1_lat + 0.00012, # ~13m away
        "longitude": c1_lon - 0.00008,
        "formatted_address": "Near Market Corner, Ward 12",
        "concise_summary": "Submerged street corner at market junction",
        "is_duplicate": True,
        "master_ticket_id": c1_master_id,
        "duplicate_count": 1,
        "priority_rank": "Priority 2",
        "priority_score": 68.0,
        "priority_rationale": "Linked duplicate of master ticket CS-DUPL-2001.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Duplicate A.2
    reports.append({
        "id": str(uuid.uuid4()),
        "tracking_id": "CS-DUPL-2003",
        "created_at": now - timedelta(hours=3),
        "raw_description": "Heavy water accumulation near market gate vegetable shops. Pedestrians cannot cross.",
        "user_category": "Waterlogging & Drainage",
        "verified_category": "Waterlogging & Drainage",
        "media_url": None,
        "latitude": c1_lat - 0.00010, # ~11m away
        "longitude": c1_lon + 0.00015,
        "formatted_address": "Market Gate North Lane, Ward 12",
        "concise_summary": "Drain overflow flooding market shops",
        "is_duplicate": True,
        "master_ticket_id": c1_master_id,
        "duplicate_count": 1,
        "priority_rank": "Priority 2",
        "priority_score": 68.0,
        "priority_rationale": "Linked duplicate of master ticket CS-DUPL-2001.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Cluster B: Severe Pothole Cluster Outside School Crossing (Master + 2 Duplicates within 25m)
    c2_master_id = str(uuid.uuid4())
    c2_lat, c2_lon = 12.9720, 77.5952
    reports.append({
        "id": c2_master_id,
        "tracking_id": "CS-DUPL-2004",
        "created_at": now - timedelta(hours=14),
        "raw_description": "Massive cluster of deep potholes directly on the pedestrian zebra crossing. Two two-wheelers fell today.",
        "user_category": "Road Failure & Potholes",
        "verified_category": "Road Failure & Potholes",
        "media_url": "/demo-media/pothole_cluster_1.jpg",
        "latitude": c2_lat,
        "longitude": c2_lon,
        "formatted_address": "School Road Zebra Crossing, Ward 12",
        "concise_summary": "Dangerous pothole crater cluster on pedestrian crossing",
        "is_duplicate": False,
        "master_ticket_id": None,
        "duplicate_count": 3,
        "priority_rank": "Priority 2",
        "priority_score": 65.0,
        "priority_rationale": "Ranked Priority 2 (High). Rationale: Pothole hazard adjacent to school walking route with 2 linked duplicate reports.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Duplicate B.1
    reports.append({
        "id": str(uuid.uuid4()),
        "tracking_id": "CS-DUPL-2005",
        "created_at": now - timedelta(hours=9),
        "raw_description": "Road surface broken into chunks at the crossing near school. Dangerous crater for school buses.",
        "user_category": "Road Failure & Potholes",
        "verified_category": "Road Failure & Potholes",
        "media_url": "/demo-media/pothole_cluster_2.jpg",
        "latitude": c2_lat + 0.00015, # ~16m away
        "longitude": c2_lon + 0.00005,
        "formatted_address": "Pedestrian Walk, School Road, Ward 12",
        "concise_summary": "Broken road surface at school crossing",
        "is_duplicate": True,
        "master_ticket_id": c2_master_id,
        "duplicate_count": 1,
        "priority_rank": "Priority 2",
        "priority_score": 65.0,
        "priority_rationale": "Linked duplicate of master ticket CS-DUPL-2004.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Duplicate B.2
    reports.append({
        "id": str(uuid.uuid4()),
        "tracking_id": "CS-DUPL-2006",
        "created_at": now - timedelta(hours=5),
        "raw_description": "Sharp edges and deep potholes in asphalt in front of school gate zebra crossing.",
        "user_category": "Road Failure & Potholes",
        "verified_category": "Road Failure & Potholes",
        "media_url": None,
        "latitude": c2_lat - 0.00010, # ~11m away
        "longitude": c2_lon - 0.00010,
        "formatted_address": "School Road 2nd Lane, Ward 12",
        "concise_summary": "Deep potholes on zebra crossing approach",
        "is_duplicate": True,
        "master_ticket_id": c2_master_id,
        "duplicate_count": 1,
        "priority_rank": "Priority 2",
        "priority_score": 65.0,
        "priority_rationale": "Linked duplicate of master ticket CS-DUPL-2004.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Cluster C: Overflowing Garbage Bin at 4th Cross (Master + 1 Duplicate within 20m)
    c3_master_id = str(uuid.uuid4())
    c3_lat, c3_lon = 12.9735, 77.5930
    reports.append({
        "id": c3_master_id,
        "tracking_id": "CS-DUPL-2007",
        "created_at": now - timedelta(hours=20),
        "raw_description": "Municipal waste bin overflowing onto main street. Stray animals scattering trash.",
        "user_category": "Waste Management",
        "verified_category": "Waste Management",
        "media_url": "/demo-media/waste_overflow_1.jpg",
        "latitude": c3_lat,
        "longitude": c3_lon,
        "formatted_address": "4th Cross Main Corner, Ward 12",
        "concise_summary": "Overflowing public waste bin scattering debris",
        "is_duplicate": False,
        "master_ticket_id": None,
        "duplicate_count": 2,
        "priority_rank": "Priority 3",
        "priority_score": 45.0,
        "priority_rationale": "Ranked Priority 3 (Medium). Rationale: Sanitation issue with 1 duplicate report within 20 meters.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # Duplicate C.1
    reports.append({
        "id": str(uuid.uuid4()),
        "tracking_id": "CS-DUPL-2008",
        "created_at": now - timedelta(hours=12),
        "raw_description": "Huge mound of garbage lying outside the bin on 4th cross corner.",
        "user_category": "Waste Management",
        "verified_category": "Waste Management",
        "media_url": None,
        "latitude": c3_lat + 0.00010, # ~11m away
        "longitude": c3_lon + 0.00012,
        "formatted_address": "4th Cross Corner, Ward 12",
        "concise_summary": "Uncollected trash pile at corner bin",
        "is_duplicate": True,
        "master_ticket_id": c3_master_id,
        "duplicate_count": 1,
        "priority_rank": "Priority 3",
        "priority_score": 45.0,
        "priority_rationale": "Linked duplicate of master ticket CS-DUPL-2007.",
        "lifecycle_status": "Under Review",
        "assigned_department": None,
    })

    # =========================================================================
    # TASK-018: Multi-Category Correlated Hotspot Corridor: MG Road (8 Reports)
    # =========================================================================
    # Spans a linear 100m corridor around (12.9740, 77.5960)
    # 4 Drainage + 3 Road + 1 Waste
    mg_center_lat, mg_center_lon = 12.9740, 77.5960

    mg_corridor_items = [
        # 1. Drainage
        ("CS-HOT-3001", "Waterlogging & Drainage", "Stormwater drain blocked by construction silt, causing water backflow.", 0.0001, 0.0001, "Priority 2", 62.0),
        # 2. Drainage
        ("CS-HOT-3002", "Waterlogging & Drainage", "Clogged gully trap overflowing into pedestrian sidewalk.", 0.0002, 0.0003, "Priority 2", 58.0),
        # 3. Drainage
        ("CS-HOT-3003", "Waterlogging & Drainage", "Standing wastewater accumulation along curb, breeding mosquitoes.", -0.0001, 0.0002, "Priority 3", 48.0),
        # 4. Drainage
        ("CS-HOT-3004", "Waterlogging & Drainage", "Storm drain grates completely missing and choked with mud.", 0.0003, -0.0001, "Priority 2", 60.0),
        # 5. Road Failure
        ("CS-HOT-3005", "Road Failure & Potholes", "Asphalt road edge eroded away by standing water along drain line.", 0.00015, 0.00025, "Priority 2", 55.0),
        # 6. Road Failure
        ("CS-HOT-3006", "Road Failure & Potholes", "Deep trench opening in road surface where water is seeping underneath.", -0.0002, 0.0001, "Priority 2", 64.0),
        # 7. Road Failure
        ("CS-HOT-3007", "Road Failure & Potholes", "Loose gravel and pavement cracks stretching along 30 meters.", 0.00025, -0.0002, "Priority 3", 42.0),
        # 8. Waste obstruction
        ("CS-HOT-3008", "Waste Management", "Construction debris dumped into open drainage channel on roadside.", 0.00005, 0.00035, "Priority 3", 45.0),
    ]

    for track_id, cat, desc, dlat, dlon, prank, pscore in mg_corridor_items:
        reports.append({
            "id": str(uuid.uuid4()),
            "tracking_id": track_id,
            "created_at": now - timedelta(hours=18),
            "raw_description": desc,
            "user_category": cat,
            "verified_category": cat,
            "media_url": "/demo-media/corridor_issue.jpg",
            "latitude": mg_center_lat + dlat,
            "longitude": mg_center_lon + dlon,
            "formatted_address": f"MG Road Corridor, Ward 12",
            "concise_summary": desc[:80] + "...",
            "is_duplicate": False,
            "master_ticket_id": None,
            "duplicate_count": 1,
            "priority_rank": prank,
            "priority_score": pscore,
            "priority_rationale": f"Part of MG Road Stormwater Infrastructure Failure Cluster corridor.",
            "lifecycle_status": "Under Review",
            "assigned_department": None,
        })

    # =========================================================================
    # TASK-015: Additional Baseline Reports to Fulfill PRD Category Quota (22 Reports)
    # Total so far: 2 (Hazards) + 8 (Duplicates) + 8 (Hotspot) = 18 reports
    # Need 22 more reports to reach 40 total reports:
    # Target totals for 40 reports:
    # - Waterlogging: 12 (Current: 3 in cluster A + 4 in hotspot = 7 -> need 5 more)
    # - Road Failure: 12 (Current: 1 hazard + 3 in cluster B + 3 in hotspot = 7 -> need 5 more)
    # - Waste Management: 8 (Current: 2 in cluster C + 1 in hotspot = 3 -> need 5 more)
    # - Street Lighting: 4 (Current: 0 -> need 4)
    # - Public Utilities: 4 (Current: 1 hazard -> need 3)
    # 5 + 5 + 5 + 4 + 3 = 22 reports!
    # =========================================================================

    baseline_items = [
        # 5 Waterlogging
        ("CS-BASE-4001", "Waterlogging & Drainage", "Rainwater flooding bus shelter area", 12.9715, 77.5965, "Priority 3", 40.0, "Submitted"),
        ("CS-BASE-4002", "Waterlogging & Drainage", "Water pooling in alleyway behind commercial complex", 12.9728, 77.5925, "Priority 3", 35.0, "Submitted"),
        ("CS-BASE-4003", "Waterlogging & Drainage", "Drainage cover blocked with plastic bags", 12.9702, 77.5955, "Priority 4", 25.0, "Submitted"),
        ("CS-BASE-4004", "Waterlogging & Drainage", "Overflowing storm chamber near park", 12.9745, 77.5935, "Priority 3", 38.0, "Submitted"),
        ("CS-BASE-4005", "Waterlogging & Drainage", "Road puddle persisting for 3 days after rain", 12.9695, 77.5940, "Priority 4", 20.0, "Resolved"),

        # 5 Road Failure
        ("CS-BASE-4006", "Road Failure & Potholes", "Single pothole near 8th Main speed breaker", 12.9712, 77.5975, "Priority 3", 35.0, "Submitted"),
        ("CS-BASE-4007", "Road Failure & Potholes", "Sunken road patch around utility access point", 12.9732, 77.5915, "Priority 3", 42.0, "Assigned"),
        ("CS-BASE-4008", "Road Failure & Potholes", "Cracked concrete slab at residential driveway entrance", 12.9708, 77.5960, "Priority 4", 22.0, "Submitted"),
        ("CS-BASE-4009", "Road Failure & Potholes", "Damaged road curbstones scattering onto lane", 12.9722, 77.5932, "Priority 4", 28.0, "Resolved"),
        ("CS-BASE-4010", "Road Failure & Potholes", "Road divider broken after minor vehicular collision", 12.9742, 77.5948, "Priority 3", 44.0, "Assigned"),

        # 5 Waste Management
        ("CS-BASE-4011", "Waste Management", "Commercial cardboard boxes dumped on sidewalk", 12.9718, 77.5938, "Priority 4", 25.0, "Submitted"),
        ("CS-BASE-4012", "Waste Management", "Dead tree branches obstructing pedestrian pathway", 12.9726, 77.5962, "Priority 4", 22.0, "Submitted"),
        ("CS-BASE-4013", "Waste Management", "Litter and food packaging outside fast food stall", 12.9738, 77.5920, "Priority 4", 18.0, "Resolved"),
        ("CS-BASE-4014", "Waste Management", "Full dry-waste collection bin requiring emptying", 12.9706, 77.5945, "Priority 3", 32.0, "Assigned"),
        ("CS-BASE-4015", "Waste Management", "Illegal night dumping of household garbage bags", 12.9698, 77.5958, "Priority 3", 36.0, "Submitted"),

        # 4 Street Lighting
        ("CS-BASE-4016", "Street Lighting", "Flickering street light fixture outside apartment building", 12.9714, 77.5955, "Priority 4", 24.0, "Submitted"),
        ("CS-BASE-4017", "Street Lighting", "Complete blackout of street lights on 6th Cross lane", 12.9729, 77.5942, "Priority 2", 52.0, "Assigned"),
        ("CS-BASE-4018", "Street Lighting", "Damaged pole leaning at angle after tree branch fell", 12.9704, 77.5968, "Priority 2", 56.0, "Under Review"),
        ("CS-BASE-4019", "Street Lighting", "Streetlight on during daytime hours continuously", 12.9748, 77.5952, "Priority 4", 15.0, "Resolved"),

        # 3 Public Utilities
        ("CS-BASE-4020", "Public Utilities", "Water pipe valve leaking clear water onto footpath", 12.9719, 77.5928, "Priority 3", 46.0, "Assigned"),
        ("CS-BASE-4021", "Public Utilities", "Exposed telecom junction box with tangled loose cables", 12.9734, 77.5966, "Priority 3", 40.0, "Submitted"),
        ("CS-BASE-4022", "Public Utilities", "Low hanging overhead cable touching commercial delivery trucks", 12.9701, 77.5932, "Priority 2", 58.0, "Under Review"),
    ]

    for track_id, cat, desc, lat, lon, prank, pscore, status in baseline_items:
        reports.append({
            "id": str(uuid.uuid4()),
            "tracking_id": track_id,
            "created_at": now - timedelta(hours=24),
            "raw_description": desc,
            "user_category": cat,
            "verified_category": cat,
            "media_url": None,
            "latitude": lat,
            "longitude": lon,
            "formatted_address": f"Ward 12, Sector Road",
            "concise_summary": desc,
            "is_duplicate": False,
            "master_ticket_id": None,
            "duplicate_count": 1,
            "priority_rank": prank,
            "priority_score": pscore,
            "priority_rationale": f"Standard operational triage based on service category and location.",
            "lifecycle_status": status,
            "assigned_department": "Public Works" if status == "Assigned" else None,
        })

    return reports

