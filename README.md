# GRC Risk Register

A lightweight, standalone cybersecurity risk management web application designed to record organizational assets, identify cybersecurity threat scenarios, calculate qualitative risk scores, and track risk treatment lifecycle progression.

## Features

- **Asset Inventory**: Register and categorize organizational assets (Data, System, Device, Service) with business criticality ratings.
- **Cybersecurity Risk Register**: Link threat scenarios to assets, assess Likelihood and Impact, and document remediation plans.
- **Deterministic Risk Scoring**: Standardized $3 \times 3$ qualitative risk calculation model ($\text{Score} = \text{Likelihood} \times \text{Impact}$) with Low, Medium, and High severity classifications.
- **Interactive Executive Dashboard**: Real-time summary KPI cards, interactive 3x3 risk matrix heatmap, and severity progress breakdowns.
- **Management Reports**: In-browser printable risk register reports and one-click RFC-4180 compliant CSV export.
- **Security & Access Control**: Password hashing (PBKDF2-HMAC-SHA256), session token authentication, Role-Based Access Control (RBAC), and server-side immutable audit logging.

## Requirements

- **Python 3.8+** (Uses standard library: `http.server`, `sqlite3`, `hashlib` — zero external pip packages required for runtime)
- **Modern Web Browser** (Chrome, Firefox, Edge, Safari)
- **Operating System**: Windows, macOS, or Linux

## Quick Start

### Windows (One-Click Launcher)

Download the latest Windows release or clone the repository, then double-click:

```text
Start GRC Risk Register.exe
```
*(or `Start GRC Risk Register.bat`)*

The launcher automatically detects/provisions the runtime, initializes the database, starts the local server, opens your default browser at `http://127.0.0.1:8000`, and exits. The server continues running independently in the background.

### Manual Command Line (All Platforms)

1. Open a terminal in the project directory.
2. Start the application server:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   ```text
   http://127.0.0.1:8000
   ```

## Running the Automated Test Suite

Run the built-in automated test runner:

```bash
python run_tests.py
```

## System Architecture

```text
Web Browser (Client)
        │
        ▼
HTML5 / CSS3 / Vanilla JavaScript SPA
        │
        ▼  (JSON REST API / Bearer Auth)
Python Backend Server (http.server)
        │
        ▼  (SQL Queries)
SQLite 3 Embedded Database
```

## License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.
