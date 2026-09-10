# Exercises every endpoint against a throwaway SQLite database.
# Run with:  python test_endpoints.py
import os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_api.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from application import create_app
from application.models import db

app = create_app("DevelopmentConfig")
results = []

def check(label, resp, expect):
    ok = resp.status_code == expect
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {label:58} {resp.status_code} {str(resp.get_json())[:70]}")

with app.app_context():
    db.create_all()
    c = app.test_client()

    print("--- CUSTOMERS ---")
    check("POST /customers/", c.post("/customers/", json={"name": "Alice Nguyen", "email": "alice@example.com", "phone": "815-555-0100"}), 201)
    check("POST /customers/ (Bob)", c.post("/customers/", json={"name": "Bob Sanders", "email": "bob@example.com", "phone": "815-555-0101"}), 201)
    check("POST /customers/ missing email -> 400", c.post("/customers/", json={"name": "NoEmail", "phone": "1"}), 400)
    check("GET  /customers/", c.get("/customers/"), 200)
    check("GET  /customers/1", c.get("/customers/1"), 200)
    check("GET  /customers/999 -> 404", c.get("/customers/999"), 404)
    check("PUT  /customers/1", c.put("/customers/1", json={"name": "Alice N.", "email": "alice@example.com", "phone": "815-555-0199"}), 200)
    check("DELETE /customers/2", c.delete("/customers/2"), 200)
    check("DELETE /customers/999 -> 404", c.delete("/customers/999"), 404)

    print("--- MECHANICS ---")
    check("POST /mechanics/ (Dana)", c.post("/mechanics/", json={"name": "Dana Whitfield", "email": "dana@shop.com", "phone": "815-555-0200", "salary": 62000}), 201)
    check("POST /mechanics/ (Marcus)", c.post("/mechanics/", json={"name": "Marcus Reed", "email": "marcus@shop.com", "phone": "815-555-0201", "salary": 58000}), 201)
    check("POST /mechanics/ missing salary -> 400", c.post("/mechanics/", json={"name": "X", "email": "x@shop.com", "phone": "1"}), 400)
    check("GET  /mechanics/", c.get("/mechanics/"), 200)
    check("PUT  /mechanics/1", c.put("/mechanics/1", json={"name": "Dana Whitfield", "email": "dana@shop.com", "phone": "815-555-0200", "salary": 65000}), 200)
    check("PUT  /mechanics/999 -> 404", c.put("/mechanics/999", json={"name": "N", "email": "n@n.com", "phone": "1", "salary": 1}), 404)

    print("--- SERVICE TICKETS ---")
    check("POST /service-tickets/", c.post("/service-tickets/", json={"VIN": "1HGCM82633A004352", "service_date": "2026-09-09", "service_desc": "Brake pads and rotors", "customer_id": 1}), 201)
    check("POST /service-tickets/ bad customer -> 404", c.post("/service-tickets/", json={"VIN": "1HGCM82633A004352", "service_date": "2026-09-09", "service_desc": "Oil", "customer_id": 999}), 404)
    check("POST /service-tickets/ missing VIN -> 400", c.post("/service-tickets/", json={"service_date": "2026-09-09", "service_desc": "Oil", "customer_id": 1}), 400)
    check("PUT  /service-tickets/1/assign-mechanic/1", c.put("/service-tickets/1/assign-mechanic/1"), 200)
    check("PUT  /service-tickets/1/assign-mechanic/2", c.put("/service-tickets/1/assign-mechanic/2"), 200)
    check("PUT  assign same mechanic again -> 400", c.put("/service-tickets/1/assign-mechanic/1"), 400)
    check("PUT  assign bad mechanic -> 404", c.put("/service-tickets/1/assign-mechanic/999"), 404)
    check("PUT  assign to bad ticket -> 404", c.put("/service-tickets/999/assign-mechanic/1"), 404)
    r = c.get("/service-tickets/"); check("GET  /service-tickets/ (2 mechanics on ticket)", r, 200)
    names = [m["name"] for m in r.get_json()[0]["mechanics"]]
    print(f"      mechanics on ticket 1: {names}")
    results.append(names == ["Dana Whitfield", "Marcus Reed"])
    check("PUT  /service-tickets/1/remove-mechanic/2", c.put("/service-tickets/1/remove-mechanic/2"), 200)
    check("PUT  remove mechanic not on ticket -> 400", c.put("/service-tickets/1/remove-mechanic/2"), 400)
    r = c.get("/service-tickets/"); names = [m["name"] for m in r.get_json()[0]["mechanics"]]
    print(f"      mechanics on ticket 1 after removal: {names}")
    results.append(names == ["Dana Whitfield"])

    print("--- DELETE MECHANIC ---")
    check("DELETE /mechanics/2", c.delete("/mechanics/2"), 200)

print(f"\n{sum(results)}/{len(results)} passed")
