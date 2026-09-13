
# CounterStock: Real-Time POS & Inventory System

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![Debian Package](https://img.shields.io/badge/Package-Debian%20.deb-D70A53.svg)](https://github.com/bahanabhan/counterstock)

CounterStock is an automated inventory management and Point-of-Sale (POS) platform designed for fast-service gastronomy and snack bars. It eliminates phantom orders by dynamically calculating available portions from physical ingredient stock levels and enforcing row-level transaction locks during order placement.

---

## Video Demonstration & Pitch

> **Project Pitch & Walkthrough (MP4):**  
> 🎬 **[Watch / Download `docs/counterstock_pitch.mp4`](docs/counterstock_pitch.mp4)**  
> *(Click the link above to view or download the presentation pitch)*

---

## Deliverables & Documentation

| Document | Format | Description |
|---|---|---|
| **User Manual** | [Download PDF](docs/user_manual.pdf) | Cashier setup, dynamic ordering, 409 handling, delivery intake |
| **Developer Guide** | [Download PDF](docs/developer_docs.pdf) | 3NF database schema, FastAPI concurrency, test coverage |
| **Debian Package** | [Download .deb](pkg/db-frontend_0.1.0_amd64.deb) | Pre-compiled native client for Ubuntu/Debian |

---

## Quick Start Guide

### 1. Launch the Database and Backend API
Make sure Docker is running, then launch the backend stack:

```bash
cd ~/counterstock/counterstock-backend
docker compose up -d --build

