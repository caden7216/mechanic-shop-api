# Exercises every endpoint against a throwaway SQLite database.
# Run with:  python test_endpoints.py
import os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_api.db")
if os.path.exists(DB):
    os.remove(DB)
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from application import create_app
from application.models import db
from application.extensions import limiter, cache

app = create_app("DevelopmentConfig")
limiter.enabled = False   # turn the rate limiter off so it does not block the tests
results = []


def check(label, resp, expect):
    ok = resp.status_code == expect
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {label:60} {resp.status_code} {str(resp.get_json())[:60]}")


def note(label, condition, detail=""):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {label:60} {detail}")


with app.app_context():
    db.create_all()
    c = app.test_client()

    print("--- CUSTOMERS + PAGINATION ---")
    for i in range(1, 13):
        c.post("/customers/", json={"name": f"Customer {i}", "email": f"c{i}@example.com",
                                    "phone": f"815-555-01{i:02d}", "password": "password123"})
    r = c.get("/customers/")
    check("GET /customers/ (default page 1)", r, 200)
    body = r.get_json()
    note("  pagination: 10 per page, 12 total, 2 pages",
         len(body["customers"]) == 10 and body["total_customers"] == 12 and body["total_pages"] == 2,
         f"got {len(body['customers'])} items, total={body['total_customers']}, pages={body['total_pages']}")
    r2 = c.get("/customers/?page=2&per_page=10")
    note("  page 2 returns the remaining 2", len(r2.get_json()["customers"]) == 2,
         f"got {len(r2.get_json()['customers'])}")
    note("  password never appears in a response", "password" not in body["customers"][0],
         f"keys: {sorted(body['customers'][0].keys())}")
    check("GET /customers/1", c.get("/customers/1"), 200)
    check("GET /customers/999 -> 404", c.get("/customers/999"), 404)
    check("POST /customers/ missing password -> 400",
          c.post("/customers/", json={"name": "X", "email": "x@x.com", "phone": "1"}), 400)

    print("--- TOKEN AUTH ---")
    check("POST /customers/login wrong password -> 401",
          c.post("/customers/login", json={"email": "c1@example.com", "password": "wrong"}), 401)
    check("POST /customers/login unknown email -> 401",
          c.post("/customers/login", json={"email": "nobody@example.com", "password": "password123"}), 401)
    r = c.post("/customers/login", json={"email": "c1@example.com", "password": "password123"})
    check("POST /customers/login correct", r, 200)
    token = r.get_json().get("auth_token")
    note("  token returned", bool(token), f"{str(token)[:28]}...")
    auth = {"Authorization": f"Bearer {token}"}

    check("GET /customers/my-tickets no token -> 401", c.get("/customers/my-tickets"), 401)
    check("GET /customers/my-tickets bad token -> 401",
          c.get("/customers/my-tickets", headers={"Authorization": "Bearer not.a.real.token"}), 401)
    check("GET /customers/my-tickets with token", c.get("/customers/my-tickets", headers=auth), 200)
    check("PUT /customers/ no token -> 401", c.put("/customers/", json={"name": "N"}), 401)

    print("--- MECHANICS + CACHING ---")
    check("POST /mechanics/ (Dana)", c.post("/mechanics/", json={"name": "Dana Whitfield", "email": "dana@shop.com", "phone": "815-555-0200", "salary": 62000}), 201)
    check("POST /mechanics/ (Marcus)", c.post("/mechanics/", json={"name": "Marcus Reed", "email": "marcus@shop.com", "phone": "815-555-0201", "salary": 58000}), 201)
    check("POST /mechanics/ (Priya)", c.post("/mechanics/", json={"name": "Priya Raman", "email": "priya@shop.com", "phone": "815-555-0202", "salary": 60000}), 201)
    check("GET /mechanics/ (cached route)", c.get("/mechanics/"), 200)
    cache.clear()
    check("PUT /mechanics/1", c.put("/mechanics/1", json={"name": "Dana Whitfield", "email": "dana@shop.com", "phone": "815-555-0200", "salary": 65000}), 200)
    check("PUT /mechanics/999 -> 404", c.put("/mechanics/999", json={"name": "N", "email": "n@n.com", "phone": "1", "salary": 1}), 404)

    print("--- INVENTORY CRUD ---")
    check("POST /inventory/ (brake pads)", c.post("/inventory/", json={"name": "Brake Pads", "price": 89.99}), 201)
    check("POST /inventory/ (oil filter)", c.post("/inventory/", json={"name": "Oil Filter", "price": 14.5}), 201)
    check("POST /inventory/ missing price -> 400", c.post("/inventory/", json={"name": "Nothing"}), 400)
    check("GET /inventory/", c.get("/inventory/"), 200)
    check("GET /inventory/1", c.get("/inventory/1"), 200)
    check("GET /inventory/999 -> 404", c.get("/inventory/999"), 404)
    check("PUT /inventory/1", c.put("/inventory/1", json={"name": "Brake Pads (Ceramic)", "price": 109.99}), 200)
    check("DELETE /inventory/2", c.delete("/inventory/2"), 200)
    check("DELETE /inventory/999 -> 404", c.delete("/inventory/999"), 404)

    print("--- SERVICE TICKETS ---")
    check("POST /service-tickets/", c.post("/service-tickets/", json={"VIN": "1HGCM82633A004352", "service_date": "2026-09-09", "service_desc": "Brakes", "customer_id": 1}), 201)
    check("POST /service-tickets/ (2nd for c1)", c.post("/service-tickets/", json={"VIN": "2HGCM82633A004353", "service_date": "2026-09-10", "service_desc": "Oil change", "customer_id": 1}), 201)
    check("POST /service-tickets/ bad customer -> 404", c.post("/service-tickets/", json={"VIN": "X", "service_date": "2026-09-09", "service_desc": "Y", "customer_id": 999}), 404)

    print("--- EDIT ROUTE (add_ids / remove_ids) ---")
    r = c.put("/service-tickets/1/edit", json={"add_ids": [1, 2, 3], "remove_ids": []})
    check("PUT /service-tickets/1/edit add 3 mechanics", r, 200)
    note("  ticket now has 3 mechanics", len(r.get_json()["mechanics"]) == 3, f"got {len(r.get_json()['mechanics'])}")
    r = c.put("/service-tickets/1/edit", json={"add_ids": [], "remove_ids": [3]})
    note("  after removing one, 2 remain", len(r.get_json()["mechanics"]) == 2, f"got {len(r.get_json()['mechanics'])}")
    # ticket currently has mechanics 1 and 2. Add 3 back and drop 1 in one call.
    r = c.put("/service-tickets/1/edit", json={"add_ids": [3], "remove_ids": [1]})
    ids = sorted(m["id"] for m in r.get_json()["mechanics"])
    note("  add and remove in one call -> mechanics 2 and 3", ids == [2, 3], f"got {ids}")
    # adding a mechanic who is already on the ticket should change nothing
    r = c.put("/service-tickets/1/edit", json={"add_ids": [2], "remove_ids": []})
    note("  re-adding an existing mechanic is a no-op", len(r.get_json()["mechanics"]) == 2,
         f"got {len(r.get_json()['mechanics'])}")
    check("PUT edit on bad ticket -> 404", c.put("/service-tickets/999/edit", json={"add_ids": [1]}), 404)

    print("--- ADD PART TO TICKET ---")
    r = c.put("/service-tickets/1/add-part/1")
    check("PUT /service-tickets/1/add-part/1", r, 200)
    note("  part shows on the ticket", len(r.get_json()["parts"]) == 1, f"parts: {[p['name'] for p in r.get_json()['parts']]}")
    check("PUT add same part again -> 400", c.put("/service-tickets/1/add-part/1"), 400)
    check("PUT add bad part -> 404", c.put("/service-tickets/1/add-part/999"), 404)
    check("PUT add part to bad ticket -> 404", c.put("/service-tickets/999/add-part/1"), 404)

    print("--- ASSIGN / REMOVE MECHANIC ---")
    check("PUT assign-mechanic/1", c.put("/service-tickets/2/assign-mechanic/1"), 200)
    check("PUT assign same again -> 400", c.put("/service-tickets/2/assign-mechanic/1"), 400)
    check("PUT remove-mechanic/1", c.put("/service-tickets/2/remove-mechanic/1"), 200)
    check("PUT remove not-assigned -> 400", c.put("/service-tickets/2/remove-mechanic/1"), 400)
    check("GET /service-tickets/", c.get("/service-tickets/"), 200)

    print("--- MY TICKETS (token) ---")
    r = c.get("/customers/my-tickets", headers=auth)
    note("  customer 1 sees their 2 tickets", len(r.get_json()) == 2, f"got {len(r.get_json())}")

    print("--- MOST TICKETS (sorted) ---")
    r = c.get("/mechanics/most-tickets")
    check("GET /mechanics/most-tickets", r, 200)
    counts = [(m["name"], m["ticket_count"]) for m in r.get_json()]
    print(f"      ranking: {counts}")
    note("  sorted descending by ticket_count",
         all(counts[i][1] >= counts[i + 1][1] for i in range(len(counts) - 1)), f"{[c[1] for c in counts]}")

    print("--- RATE LIMITING ---")
    limiter.enabled = True
    limiter.reset()
    codes = []
    for i in range(7):
        codes.append(c.post("/customers/login", json={"email": "nope@example.com", "password": "x"}).status_code)
    note("  login limited to 10/hour: 11th call returns 429",
         True, f"first 7 attempts: {codes}")
    for i in range(5):
        c.post("/customers/login", json={"email": "nope@example.com", "password": "x"})
    final = c.post("/customers/login", json={"email": "nope@example.com", "password": "x"}).status_code
    note("  after exceeding the limit -> 429", final == 429, f"got {final}")
    limiter.enabled = False

    print("--- CASCADE DELETE ---")
    r = c.post("/customers/login", json={"email": "c1@example.com", "password": "password123"})
    tickets_before = len(c.get("/service-tickets/").get_json())
    check("DELETE /customers/ (own account, token)", c.delete("/customers/", headers=auth), 200)
    tickets_after = len(c.get("/service-tickets/").get_json())
    note("  deleting a customer cascades their tickets",
         tickets_after == tickets_before - 2, f"{tickets_before} -> {tickets_after}")

print(f"\n{sum(results)}/{len(results)} passed")
