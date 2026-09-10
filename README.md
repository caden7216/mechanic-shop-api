# Mechanic Shop API

A REST API for a mechanic shop, built with **Flask**, **Flask-SQLAlchemy**,
**Flask-Marshmallow**, and **MySQL** using the **Application Factory Pattern**
and **Blueprints**. Built for the Coding Temple Backend Specialization,
Lesson 5 continuation.

It manages **customers**, **mechanics**, and **service tickets**, with a
one-to-many between customers and tickets and a many-to-many between tickets
and mechanics.

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
`mechanic_shop_db` database if it does not exist, builds all four tables, and
lists them.

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

The API runs at `http://127.0.0.1:5000`.

## Project Structure (Application Factory Pattern)

```
mechanic-shop-api/
├── app.py                       # creates the app and runs it
├── config.py                    # DevelopmentConfig with the database URI
├── setup_db.py                  # one-time database + table setup
├── test_endpoints.py            # runs every endpoint against SQLite
├── mechanic_shop.postman_collection.json
└── application/
    ├── __init__.py              # create_app() factory, registers blueprints
    ├── extensions.py            # Marshmallow instance
    ├── models.py                # Customer, Mechanic, ServiceTicket, junction table
    └── blueprints/
        ├── customers/
        │   ├── __init__.py      # customers_bp
        │   ├── routes.py
        │   └── schemas.py
        ├── mechanics/
        │   ├── __init__.py      # mechanics_bp
        │   ├── routes.py
        │   └── schemas.py
        └── service_tickets/
            ├── __init__.py      # service_tickets_bp
            ├── routes.py
            └── schemas.py
```

`create_app()` in `application/__init__.py` builds the Flask app, hooks up
SQLAlchemy and Marshmallow, and registers the three blueprints with their url
prefixes. Each blueprint folder has the same three files: `__init__.py` makes
the blueprint and imports the routes, `routes.py` has the endpoints, and
`schemas.py` has the Marshmallow schema.

## Database Models

| Table | Columns |
| --- | --- |
| `customers` | `id`, `name`, `email` (unique), `phone` |
| `mechanics` | `id`, `name`, `email` (unique), `phone`, `salary` |
| `service_tickets` | `id`, `VIN`, `service_date`, `service_desc`, `customer_id` (FK) |
| `service_mechanic` | `ticket_id` (FK), `mechanic_id` (FK) — junction table |

**Relationships**

- **One Customer → Many Service Tickets** (`customer_id` foreign key)
- **Many Service Tickets ←→ Many Mechanics** through the `service_mechanic`
  junction table. `ticket_id` and `mechanic_id` together are the primary key,
  so the same mechanic cannot be assigned to the same ticket twice.

## Marshmallow Schemas

All three are `SQLAlchemyAutoSchema`s, so the fields come straight from the
models. `ServiceTicketSchema` sets `include_fk = True` so `customer_id` is
accepted when creating a ticket, and nests the `MechanicSchema` so every ticket
shows the mechanics assigned to it.

## Endpoints

### Customers — `/customers`

| Method | Route | What it does |
| --- | --- | --- |
| POST | `/customers/` | Create a customer |
| GET | `/customers/` | All customers |
| GET | `/customers/<id>` | One customer |
| PUT | `/customers/<id>` | Update a customer |
| DELETE | `/customers/<id>` | Delete a customer |

### Mechanics — `/mechanics`

| Method | Route | What it does |
| --- | --- | --- |
| POST | `/mechanics/` | Create a mechanic |
| GET | `/mechanics/` | All mechanics |
| PUT | `/mechanics/<id>` | Update a mechanic |
| DELETE | `/mechanics/<id>` | Delete a mechanic |

### Service Tickets — `/service-tickets`

| Method | Route | What it does |
| --- | --- | --- |
| POST | `/service-tickets/` | Create a ticket (needs an existing `customer_id`) |
| PUT | `/service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>` | Add a mechanic to the ticket |
| PUT | `/service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>` | Take a mechanic off the ticket |
| GET | `/service-tickets/` | All tickets, each with its mechanics |

Assigning and removing use the relationship attribute like a list:
`ticket.mechanics.append(mechanic)` and `ticket.mechanics.remove(mechanic)`.

### Example bodies

Customer:
```json
{ "name": "Alice Nguyen", "email": "alice@example.com", "phone": "815-555-0100" }
```

Mechanic:
```json
{ "name": "Dana Whitfield", "email": "dana@shop.com", "phone": "815-555-0200", "salary": 62000 }
```

Service ticket:
```json
{ "VIN": "1HGCM82633A004352", "service_date": "2026-09-09", "service_desc": "Brake pads and rotors", "customer_id": 1 }
```

## Error Handling

| Situation | Response |
| --- | --- |
| ID that does not exist | `404` with a message |
| Missing or invalid fields | `400` with the Marshmallow validation errors |
| Ticket for a customer that does not exist | `404 "Invalid customer id"` |
| Assigning a mechanic already on the ticket | `400` |
| Removing a mechanic who is not on the ticket | `400` |

## Postman Collection

`mechanic_shop.postman_collection.json` has a request for all 13 endpoints in
Customers / Mechanics / Service Tickets folders. In Postman: **Import** → drop
the file in → start the app → send. Create a customer and a mechanic first,
then a ticket, then assign.

## Testing

`test_endpoints.py` runs 29 checks against a temporary SQLite database so you
can verify the API without touching MySQL:

```bash
python test_endpoints.py
```

It covers every endpoint plus the error cases, and confirms that assigning two
mechanics shows both on the ticket and removing one leaves the other. All 29
pass.
