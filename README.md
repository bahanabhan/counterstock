# CounterStock: Real-Time POS & Inventory System

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![Debian Package](https://img.shields.io/badge/Package-Debian%20.deb-D70A53.svg)](https://github.com/bahanabhan/counterstock)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

CounterStock is an enterprise-grade Point-of-Sale (POS) and inventory synchronization platform engineered specifically for fast-service gastronomy and high-throughput snack bar environments. 

Traditional POS systems treat sales records and inventory ledgers as loosely coupled entities, resulting in phantom orders, mid-service stockouts, and administrative inventory drift. CounterStock eliminates this design flaw by establishing a strictly normalized relational core where available menu portions are dynamically computed from raw ingredient stock and checkout operations enforce pessimistic row-level database locks.

---

## Video Demonstration & Pitch

[![Watch the Pitch & Demo](https://img.youtube.com/vi/N1YBXGlobhc/0.jpg)](https://www.youtube.com/watch?v=N1YBXGlobhc)

> 🎬 **[Click here to watch the CounterStock Project Pitch & Live Walkthrough on YouTube](https://www.youtube.com/watch?v=N1YBXGlobhc)**
---

## Deliverables & Documentation

| Document | Format | Description |
|---|---|---|
| **User Manual** | [Download PDF](docs/user_manual.pdf) | Cashier workflow, POS terminal authentication, dynamic ordering, HTTP 409 conflict handling, and delivery intake |
| **Developer Guide** | [Download PDF](docs/developer_docs.pdf) | 3NF database schema, FastAPI concurrency handling, Docker orchestration, and test suite execution |
| **Debian Package** | [Download .deb](pkg/db-frontend_0.1.0_amd64.deb) | Pre-compiled native client package targeted for Ubuntu/Debian operating environments |

---

## Core Capabilities & Engineering Highlights

* **Real-Time Dynamic Portion Calculation:** Menu availability is never a static manual counter. Available servings are calculated dynamically as the bottleneck ratio between ingredient stock levels and recipe definitions:
  $$\text{Portions Available} = \min_{i \in \text{Ingredients}} \left\lfloor \frac{\text{Stock}_i}{\text{Requirement}_i} \right\rfloor$$
* **Pessimistic Locking & Concurrency Control:** Prevents race conditions across concurrent cashier terminals by utilizing PostgreSQL `SELECT ... FOR UPDATE` row locks inside atomic database transactions. If two terminals attempt to sell the final portion simultaneously, the second transaction is safely rejected with an explicit `HTTP 409 Conflict`.
* **Relational Integrity in 3rd Normal Form (3NF):** Elimination of insertion, update, and deletion anomalies via isolated relation tables (`ingredients`, `menu_items`, `recipes`, `orders`, `order_items`).
* **Packaging & Portability:** Native packaging via a pre-built `.deb` binary for standard workstation distribution alongside containerized PostgreSQL and FastAPI deployment via Docker Compose.

---

## System Architecture

```text
                       ┌───────────────────────────────┐
                       │    Cashier Desktop Client     │
                       │         (Tkinter GUI)         │
                       └──────────────┬────────────────┘
                                      │ HTTP / JSON
                                      │ Header: X-API-Token
                                      ▼
                       ┌───────────────────────────────┐
                       │     Backend REST Service      │
                       │       (FastAPI / Uvicorn)     │
                       └──────────────┬────────────────┘
                                      │ SQLAlchemy Session
                                      │ (SELECT ... FOR UPDATE)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PostgreSQL 16 Database Engine                          │
│                                                                             │
│  ┌───────────────────┐       ┌───────────────────┐       ┌───────────────┐  │
│  │    ingredients    │◀──────│      recipes      │──────▶│  menu_items   │  │
│  │ stock_quantity>=0 │       │ ingredient_id, qty│       │ item_id, price│  │
│  └───────────────────┘       └───────────────────┘       └───────┬───────┘  │
│                                                                  │          │
│                              ┌───────────────────┐               │          │
│                              │    order_items    │◀──────────────┘          │
│                              │ order_id, item_id │                          │
│                              └─────────┬─────────┘                          │
│                                        │                                    │
│                              ┌─────────▼─────────┐                          │
│                              │      orders       │                          │
│                              │ total, timestamp  │                          │
│                              └───────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘

---

---

## Terminal Download & Installation

You can clone the entire repository or fetch only the pre-compiled frontend package directly using your terminal:

### Option A: Clone the Full Project Repository
```bash
git clone https://github.com/bahanabhan/counterstock.git
cd counterstock
```

### Option B: Download & Install the Debian Package Directly
```bash
wget https://raw.githubusercontent.com/bahanabhan/counterstock/main/pkg/db-frontend_0.1.0_amd64.deb
```
```bash
sudo dpkg -i db-frontend_0.1.0_amd64.deb
```

---

## How to Run the Program

Follow these steps to launch both services:

### 1. Start the Backend & Database
```bash
cd ~/counterstock/backend
docker compose up -d --build
```

### 2. Launch the Frontend POS Terminal

If installed via the Debian package:
```bash
db-frontend
```

Or run directly from the source repository:
```bash
python3 ~/counterstock/frontend/app.py
```
