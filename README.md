# Mechanic Shop API — Advanced

A REST API for a mechanic shop, built with **Flask**, **Flask-SQLAlchemy**,
**Flask-Marshmallow**, and **MySQL** using the **Application Factory Pattern**
and **Blueprints**. Built for the Coding Temple BE Module 1 Project.

It manages **customers**, **mechanics**, **service tickets**, and **inventory**,
with token authentication, rate limiting, caching, pagination, and advanced
relationship queries.

## Setup

### 1. Install

```bash
git clone https://github.com/caden7216/mechanic-shop-api.git
cd mechanic-shop-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

(On Windows the activate command is `venv\Scripts\activate`.)

### 2. Create the database and tables

```bash
python setup_db.py
```

It asks for your MySQL root password (typing is hidden), creates the
`mechanic_shop_db` database if it does not exist, builds all six tables, and
lists them.

> If you already ran an earlier version of this project, **drop the database
> first** — the `customers` table gained a `password` column and there are two
> new tables. In MySQL Workbench: `DROP DATABASE mechanic_shop_db;` then re-run
> `setup_db.py`.

### 3. Run the app

```bash
python app.py
```

It asks for the password again unless you set it first:

```bash
export MYSQL_PASSWORD='your_mysql_password'
```

Use **single quotes** so the shell does not mangle special characters. The
password is never written into the code, so it cannot end up on GitHub.

The API runs at `http://127.0.0.1:5001`.

> Why 5001 and not 5000? On macOS the AirPlay Receiver already listens on port
> 5000 and answers every request with a 403, so Flask cannot use it. If you are
> not on a Mac you can change the port back in `app.py`.

## Project Structure

```
mechanic-shop-api/
├── app.py                       # creates the app and runs it
├── config.py                    # DevelopmentConfig with the database URI
├── setup_db.py                  # one-time database + table setup
├── test_endpoints.py            # runs every endpoint against SQLite
├── mechanic_shop.postman_collection.json
└── application/
    ├── __init__.py              # create_app() factory, registers blueprints
    ├── extensions.py            # Marshmallow, Limiter, Cache
    ├── models.py                # Customer, Mechanic, ServiceTicket, Inventory + 2 junction tables
    ├── utils/
    │   └── util.py              # encode_token() and the token_required decorator
    └── blueprints/
        ├── customers/           # __init__.py, routes.py, schemas.py
        ├── mechanics/           # __init__.py, routes.py, schemas.py
        ├── service_tickets/     # __init__.py, routes.py, schemas.py
        └── inventory/           # __init__.py, routes.py, schemas.py
```

## Database Models

| Table | Columns |
| --- | --- |
| `customers` | `id`, `name`, `email` (unique), `phone`, `password` |
| `mechanics` | `id`, `name`, `email` (unique), `phone`, `salary` |
| `service_tickets` | `id`, `VIN`, `service_date`, `service_desc`, `customer_id` (FK) |
| `inventory` | `id`, `name`, `price` |
| `service_mechanic` | `ticket_id`, `mechanic_id` — junction table |
| `ticket_inventory` | `ticket_id`, `inventory_id` — junction table |

**Relationships**

- **One Customer → Many Service Tickets.** Uses `cascade="all, delete"`, so
  deleting a customer also deletes their tickets instead of orphaning them.
- **Many Service Tickets ←→ Many Mechanics** through `service_mechanic`.
- **Many Service Tickets ←→ Many Inventory parts** through `ticket_inventory`.

Both junction tables use a composite primary key (`ticket_id` + the other id),
so the same mechanic or part cannot be added to the same ticket twice.

## Token Authentication

`application/utils/util.py` has the two pieces:

- **`encode_token(customer_id)`** — builds a JWT with `exp` (1 hour out), `iat`,
  and `sub` (the customer id, cast to a string so the token is not malformed).
  Signed with HS256 using **python-jose**.
- **`@token_required`** — pulls the token out of the `Authorization: Bearer
  <token>` header, decodes it, and passes the `customer_id` into the route.
  Returns 401 for a missing, invalid, or expired token.

**How to use it:**

1. `POST /customers/login` with an email and password → returns an `auth_token`
2. Send that token on protected routes as `Authorization: Bearer <token>`

In Postman the collection does this automatically — the Login request has a test
script that saves the token to a `{{auth_token}}` collection variable, and the
protected requests use it.

**Protected routes:** `GET /customers/my-tickets`, `PUT /customers/`,
`DELETE /customers/`. Update and delete no longer take an id in the URL, because
the id comes from the token — you can only change your own account.

**Note:** passwords are stored in plain text, which is what the lesson asks for.
A real app would hash them.

## Rate Limiting and Caching

**Rate limited routes** (Flask-Limiter, per client IP):

| Route | Limit | Why |
| --- | --- | --- |
| `POST /customers/login` | 10 per hour | A login route is the obvious target for someone guessing passwords. This makes brute forcing impractical. |
| `POST /customers/` | 5 per hour | Account creation is easy to abuse — without a limit someone could script thousands of junk customers into the database. |

Going over the limit returns **429 Too Many Requests**.

**Cached route** (Flask-Caching, `SimpleCache`):

| Route | Timeout | Why |
| --- | --- | --- |
| `GET /mechanics/` | 30 seconds | The mechanic list barely ever changes but gets read a lot. The first request queries the database, the rest come out of the cache. |

> Because it is cached, a mechanic you just created may not show up in
> `GET /mechanics/` for up to 30 seconds. That is the cache doing its job, not a
> bug.

## Endpoints

### Customers — `/customers`

| Method | Route | Notes |
| --- | --- | --- |
| POST | `/customers/` | Create a customer. **Rate limited 5/hour** |
| POST | `/customers/login` | Returns an auth token. **Rate limited 10/hour** |
| GET | `/customers/` | All customers, **paginated** (`?page=1&per_page=10`) |
| GET | `/customers/<id>` | One customer |
| GET | `/customers/my-tickets` | **Token required.** That customer's tickets |
| PUT | `/customers/` | **Token required.** Updates your own account |
| DELETE | `/customers/` | **Token required.** Deletes your own account |

### Mechanics — `/mechanics`

| Method | Route | Notes |
| --- | --- | --- |
| POST | `/mechanics/` | Create a mechanic |
| GET | `/mechanics/` | All mechanics. **Cached 30s** |
| GET | `/mechanics/most-tickets` | Mechanics ranked by how many tickets they have worked |
| PUT | `/mechanics/<id>` | Update a mechanic |
| DELETE | `/mechanics/<id>` | Delete a mechanic |

### Inventory — `/inventory`

| Method | Route | Notes |
| --- | --- | --- |
| POST | `/inventory/` | Add a part |
| GET | `/inventory/` | All parts |
| GET | `/inventory/<id>` | One part |
| PUT | `/inventory/<id>` | Update a part |
| DELETE | `/inventory/<id>` | Delete a part |

### Service Tickets — `/service-tickets`

| Method | Route | Notes |
| --- | --- | --- |
| POST | `/service-tickets/` | Create a ticket (needs an existing `customer_id`) |
| GET | `/service-tickets/` | All tickets with their mechanics and parts |
| PUT | `/service-tickets/<ticket_id>/edit` | Add and remove several mechanics at once |
| PUT | `/service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>` | Add one mechanic |
| PUT | `/service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>` | Remove one mechanic |
| PUT | `/service-tickets/<ticket_id>/add-part/<part_id>` | Add a part to the ticket |

### Example bodies

Customer:
```json
{ "name": "Alice Nguyen", "email": "alice@example.com", "phone": "815-555-0100", "password": "password123" }
```

Login:
```json
{ "email": "alice@example.com", "password": "password123" }
```

Mechanic:
```json
{ "name": "Dana Whitfield", "email": "dana@shop.com", "phone": "815-555-0200", "salary": 62000 }
```

Part:
```json
{ "name": "Brake Pads", "price": 89.99 }
```

Service ticket:
```json
{ "VIN": "1HGCM82633A004352", "service_date": "2026-09-09", "service_desc": "Brake pads and rotors", "customer_id": 1 }
```

Edit ticket (add and remove mechanics in one call):
```json
{ "add_ids": [1, 2], "remove_ids": [3] }
```

## Advanced Queries

- **`GET /mechanics/most-tickets`** — the relationship attribute gives back a
  plain Python list, so `len(mechanic.service_tickets)` is the ticket count.
  Sorted with `mechanics.sort(key=lambda m: len(m.service_tickets), reverse=True)`
  so the busiest mechanic is first. Each result includes a `ticket_count`.
- **`PUT /<ticket_id>/edit`** — loops the `add_ids` and `remove_ids` lists and
  uses `ticket.mechanics.append()` / `.remove()`. It checks membership first,
  because `.remove()` raises an error if the mechanic is not on the ticket.
- **Pagination on `GET /customers/`** — uses `db.paginate()` and returns the
  page, per_page, total_customers, and total_pages alongside the results.

## Error Handling

| Situation | Response |
| --- | --- |
| ID that does not exist | `404` with a message |
| Missing or invalid fields | `400` with the Marshmallow validation errors |
| Ticket for a customer that does not exist | `404 "Invalid customer id"` |
| Assigning a mechanic already on the ticket | `400` |
| Removing a mechanic who is not on the ticket | `400` |
| Adding a part already on the ticket | `400` |
| Missing / invalid / expired token | `401` |
| Wrong email or password | `401` |
| Over the rate limit | `429` |

## Postman Collection

`mechanic_shop.postman_collection.json` has a request for all 23 endpoints in
Customers / Mechanics / Inventory / Service Tickets folders.

In Postman: **Import** → drop the file in → start the app → send.

Suggested order: create a customer → **Login** (the token saves itself) → create
mechanics → create parts → create a ticket → edit/assign/add-part.

## Testing

`test_endpoints.py` runs 56 checks against a temporary SQLite database so you
can verify everything without touching MySQL:

```bash
python test_endpoints.py
```

It covers every endpoint plus the error cases, and confirms:

- Pagination returns 10 of 12 customers on page 1 and 2 on page 2
- The password never appears in any response
- Login returns a token; missing, invalid, and expired tokens all give 401
- `my-tickets` returns only that customer's tickets
- The edit route adds and removes mechanics in the same request
- Re-adding a mechanic who is already on a ticket changes nothing
- `most-tickets` comes back sorted descending
- Going over the login rate limit returns 429
- Deleting a customer cascades and removes their tickets

All 56 pass.
