import threading
import time
import json
import urllib.request
import urllib.error
import urllib.parse
from http.server import HTTPServer
from apps.api.standalone_server import CitySenseApiHandler

PORT = 8005
BASE_URL = f"http://127.0.0.1:{PORT}"

def start_test_server():
    server = HTTPServer(("127.0.0.1", PORT), CitySenseApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    return server

def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def http_post(path, data):
    url = f"{BASE_URL}{path}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def run_integration_tests():
    print("=" * 60)
    print("STARTING CAPTURE API INTEGRATION TESTS (PHASE 4)")
    print("=" * 60)
    server = start_test_server()

    try:
        # Test 1: Root & Health Probes
        code, body = http_get("/")
        assert code == 200, f"Root returned {code}"
        assert body["platform"] == "CitySense"
        print("Test 1a: Root endpoint (200 OK) verified.")

        code, db_body = http_get("/api/health/db")
        assert code == 200, f"Health DB returned {code}"
        assert db_body["status"] == "healthy"
        print("Test 1b: Database health probe (SELECT 1 healthy) verified.")

        # Test 2: Valid Report Submission (Capture)
        report_payload = {
            "raw_description": "Water pipe burst on 5th Cross road flooding the lane",
            "latitude": 12.9720,
            "longitude": 77.5955,
            "user_category": "Waterlogging & Drainage"
        }
        code, create_res = http_post("/api/v1/reports", report_payload)
        assert code == 201, f"Expected 201, got {code}: {create_res}"
        assert "tracking_id" in create_res
        assert create_res["tracking_id"].startswith("CS-")
        assert create_res["lifecycle_status"] in ("Submitted", "Under Review")
        new_tid = create_res["tracking_id"]
        print(f"Test 2: Public Report Submission (201 Created) verified. Tracking ID={new_tid}")

        # Test 3: Input Validation Errors
        # Missing coordinates
        code, err_res1 = http_post("/api/v1/reports", {"raw_description": "Valid description without coordinates"})
        assert code == 422, f"Expected 422, got {code}"
        print("Test 3a: Missing coordinate validation error (422) verified.")

        # Description too short (< 5 chars)
        code, err_res2 = http_post("/api/v1/reports", {"raw_description": "abc", "latitude": 12.9, "longitude": 77.5})
        assert code == 422, f"Expected 422, got {code}"
        print("Test 3b: Short description validation error (422) verified.")

        # Test 4: Tracking Lookup
        code, track_res = http_get(f"/api/v1/reports/track/{new_tid}")
        assert code == 200, f"Expected 200, got {code}"
        assert track_res["tracking_id"] == new_tid
        assert track_res["lifecycle_status"] in ("Submitted", "Under Review")
        assert track_res["user_category"] == "Waterlogging & Drainage"
        assert track_res["verified_category"] in ("Waterlogging & Drainage", "Public Utilities")
        print(f"Test 4a: Tracking lookup for valid ID (200 OK) verified: Status={track_res['lifecycle_status']}.")

        # Non-existent Tracking ID
        code, not_found_res = http_get("/api/v1/reports/track/CS-INVALID-000")
        assert code == 404, f"Expected 404, got {code}"
        print("Test 4b: Tracking lookup for non-existent ID (404 Not Found) verified.")

        # Test 5: Listing Reports
        code, list_res = http_get("/api/v1/reports")
        assert code == 200, f"Expected 200, got {code}"
        assert len(list_res) >= 41, f"Expected >= 41 reports, got {len(list_res)}"
        print(f"Test 5: Listing active reports verified. Total retrieved: {len(list_res)}")

        print("\nALL PHASE 4 CAPTURE API INTEGRATION TESTS PASSED SUCCESSFULLY.")

    finally:
        server.shutdown()

if __name__ == "__main__":
    run_integration_tests()
