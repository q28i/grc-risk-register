# Feature Status Matrix

This matrix tracks the lifecycle state of each core feature in the **GRC Risk Register** system.

---

| Feature | Status Before | Change Made | Status After | Code Exists | DB Schema | UI Complete | Routes Work | Tests Pass | Documentation |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Authentication & Sessions** | Upstream Odoo Login | Built lightweight session token auth with SHA-256 password hashing. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Role Permissions (RBAC)** | Multi-group ERP ACL | Implemented dual-role server guards (`Administrator` vs. `Risk User`). | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Asset Registration** | 6 fragmented tables | Unified asset entity (`Data`, `System`, `Device`, `Service`) with auto IDs (`AST-xxx`). | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Asset Archiving** | Basic active flag | Non-destructive soft delete with filter toggle and Admin unarchive. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Risk Identification** | Complex relational model | Streamlined form linking risk to asset with title, description, and consequence. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Risk Calculation ($3\times3$)** | Fragile DB lookup table | Deterministic equation ($\text{Score} = L \times I$) with read-only Level mapping. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Risk Tracking & Lifecycle** | Free-form stage changes | 4 strict operational statuses (`Open`, `In Progress`, `Treated`, `Closed`) + notes. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Interactive Dashboard** | Generic ERP Kanban | Cyber dashboard with 4 metric counters and $3\times3$ interactive risk heatmap. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Printable Risk Register** | Wkhtmltopdf QWeb PDF | Browser-native print report with multi-filter controls and CSV export. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Audit Logging** | Mail thread chatter | Server-side event logger recording all asset and risk modifications. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Flat Material UI/UX System** | Dark-navy AI-slop aesthetic | Replaced with clean flat Material system (#F5F5F5 bg, #6200EE purple accent, 2px radius, rectangular controls, no pills/gradients). | **COMPLETED** | Yes | N/A | Yes | Yes | Yes | Yes |
| **Demo Role & Granular Feature Matrix** | 12 coarse-grained controls & quick login | Expanded to 29 granular feature controls across 6 categories in SQLite, removed login credentials shortcuts, added explicit data loading state transitions for dashboard and tables, enforced 403 backend guards. | **COMPLETED** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Neutral Development Notices & UX** | Account-specific restriction notices | Replaced all "disabled for this account/user" notices with neutral development text, added `#dev-notice-banner`, updated 403 backend error text, and preserved authentic student-project realism. | **COMPLETED** | Yes | N/A | Yes | Yes | Yes | Yes |
| **Control Catalogue** | Upstream ERP module | Postponed to Intermediate scope (Semester 3). Excluded from active UI. | **LOCKED** | Upstream | N/A | N/A | N/A | N/A | Documented |

| **Threat Scenario NIST SP 800-30** | Upstream ERP module | Postponed to Intermediate scope (Semester 3). Excluded from active UI. | **LOCKED** | Upstream | N/A | N/A | N/A | N/A | Documented |
| **ISO 27001 ISMS Controls** | Upstream ERP module | Postponed to Intermediate scope (Semester 3). Excluded from active UI. | **LOCKED** | Upstream | N/A | N/A | N/A | N/A | Documented |
| **CVSS v3.1 & CVE Management** | Upstream ERP module | Postponed to Advanced scope (Semester 4). Excluded from active UI. | **LOCKED** | Upstream | N/A | N/A | N/A | N/A | Documented |
