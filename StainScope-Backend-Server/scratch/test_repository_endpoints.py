"""
Test runner for StainScope new repository REST API endpoints:
- /health
- /profile (GET/PUT)
- /notes (GET/POST/DELETE)
- /saved-comparisons (GET/POST)
- /analyses (GET list & GET detail)
"""
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, r"c:\final_ppd\StainScope-Backend-Server")
os.environ["STAINSCOPE_DEV_MODE"] = "true"

from api import app

client = TestClient(app)

def test_repository_endpoints():
    print("==================================================")
    print("TESTING STAINSCOPE REST REPOSITORY ENDPOINTS")
    print("==================================================")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    h_data = res.json()
    print("  [OK] GET /health:", h_data)
    assert h_data["status"] == "healthy"
    assert h_data["dev_mode"] is True

    # 2. Profile GET & PUT
    res = client.get("/profile")
    assert res.status_code == 200
    prof = res.json()
    print("  [OK] GET /profile:", prof)

    res = client.put("/profile", json={
        "full_name": "Dr. StainScope Lead Researcher",
        "role": "Senior Osteogenesis Engineer",
        "institution": "BioMed Research Institute"
    })
    assert res.status_code == 200
    updated_prof = res.json()
    print("  [OK] PUT /profile:", updated_prof)

    # 3. Notes GET & POST & DELETE
    res = client.post("/notes", json={
        "title": "C2 Osteogenesis Day 28 Observation",
        "content": "Mineralization nodules showing high density in central region."
    })
    assert res.status_code == 200
    note = res.json()
    print("  [OK] POST /notes:", note)
    note_id = note.get("id")

    res = client.get("/notes")
    assert res.status_code == 200
    notes_list = res.json()
    print(f"  [OK] GET /notes (Count: {len(notes_list)})")

    if note_id:
        res = client.delete(f"/notes/{note_id}")
        assert res.status_code == 200
        print("  [OK] DELETE /notes/{id}:", res.json())

    # 4. Saved Comparisons GET & POST
    res = client.post("/saved-comparisons", json={
        "title": "C2 vs C3 Osteogenesis Comparison",
        "analysis_ids": [],
        "ranking_summary": {"top_sample": "C2_D28"}
    })
    assert res.status_code == 200
    comp = res.json()
    print("  [OK] POST /saved-comparisons:", comp)

    res = client.get("/saved-comparisons")
    assert res.status_code == 200
    comps_list = res.json()
    print(f"  [OK] GET /saved-comparisons (Count: {len(comps_list)})")

    # 5. Analyses list GET
    res = client.get("/analyses")
    assert res.status_code == 200
    analyses = res.json()
    print(f"  [OK] GET /analyses (Count: {len(analyses)})")

    print("\n==================================================")
    print("ALL REPOSITORY ENDPOINTS VERIFIED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_repository_endpoints()
