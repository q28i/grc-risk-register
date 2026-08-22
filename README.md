# GRC Risk Register

A simple cybersecurity risk management application for recording organizational assets, assessing cybersecurity risks, tracking risk treatment, and generating basic reports.

## Features

- **Asset Management**: Register and categorize organizational assets (Data, System, Device, Service) with criticality ratings.
- **Cybersecurity Risk Register**: Link threat scenarios to assets and calculate qualitative risk scores.
- **3×3 Qualitative Risk Assessment**: Deterministic scoring ($Score = Likelihood \times Impact$) with Low, Medium, and High severity ratings.
- **Risk Treatment Tracking**: Track remediation progression across Open, In Progress, Treated, and Closed statuses.
- **Executive Dashboard**: Summary KPI cards, interactive 3×3 heatmap, and severity breakdowns.
- **Reports & Export**: In-browser printable risk register reports and RFC-4180 CSV export.
- **User Authentication & RBAC**: Password hashing (PBKDF2-HMAC-SHA256), session token authentication, and role-based access control.

## Requirements

- **Python 3.8+** (Built with the Python 3 Standard Library — zero external pip packages required)
- **Modern Web Browser** (Chrome, Firefox, Edge, Safari)
- **Operating System**: Windows, macOS, or Linux

## Running

### Windows (One-Click Launcher)

Double-click:

```text
Start GRC Risk Register.exe
```

*(or `Start GRC Risk Register.bat`)*

The launcher initializes the environment, starts the local server, and opens your default browser at `http://127.0.0.1:8000`.

### Manual (All Platforms)

If Python 3 is installed:

```bash
cd "Grc Risk Management Code"
python app.py
```

Then open your browser and navigate to:

```text
http://127.0.0.1:8000
```

## Running Tests

To run the test suite:

```bash
cd "Grc Risk Management Code"
python run_tests.py
```

## License

This project is licensed under the Apache License 2.0. See the `LICENSE` and `NOTICE` files for details.

