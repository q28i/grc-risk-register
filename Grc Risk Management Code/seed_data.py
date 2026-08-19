"""
GRC Risk Register - Seed Data Generator
Populates realistic cybersecurity assets and risks for academic demonstration.
"""

from database import init_db, create_asset, create_risk, get_assets, get_risks, DB_PATH
import os

SAMPLE_ASSETS = [
    {
        "name": "Cardholder Payment Database",
        "type": "Data",
        "owner": "Data Security Lead",
        "importance": "High",
        "description": "Encrypted database cluster storing tokenized customer credit card records and billing history."
    },
    {
        "name": "Active Directory Domain Controller",
        "type": "System",
        "owner": "Identity & Access Team",
        "importance": "High",
        "description": "Central identity provider managing enterprise Kerberos authentication, LDAP directories, and Group Policy."
    },
    {
        "name": "Customer Web Portal",
        "type": "Service",
        "owner": "Application Security Engineer",
        "importance": "Medium",
        "description": "Public HTTPS web application serving customer dashboard, self-service transactions, and account management."
    },
    {
        "name": "Corporate Employee Laptops",
        "type": "Device",
        "owner": "Endpoint Support Manager",
        "importance": "Medium",
        "description": "Enterprise Windows 11 and macOS endpoints deployed to remote and office staff with BitLocker full-disk encryption."
    },
    {
        "name": "Cloud Backup Storage Bucket",
        "type": "Data",
        "owner": "Disaster Recovery Team",
        "importance": "High",
        "description": "Offsite immutable object storage bucket containing daily encrypted database and system volume snapshots."
    },
    {
        "name": "VPN Remote Access Gateway",
        "type": "Service",
        "owner": "Network Operations Lead",
        "importance": "Medium",
        "description": "IPsec/SSL VPN appliance providing multi-factor authenticated remote access to internal subnets."
    }
]

SAMPLE_RISKS = [
    {
        "asset_name": "Corporate Employee Laptops",
        "title": "Ransomware Outbreak via Malicious Email Attachment",
        "description": "A phishing email payload executes ransomware on an employee laptop, attempting lateral SMB propagation.",
        "consequence": "Potential workstation encryption, lost productivity, and risk of network lateral movement.",
        "likelihood": 3,
        "impact": 3,
        "owner": "Endpoint Security Lead",
        "status": "Open",
        "notes": "Deploying behavioral EDR agent and restricting local administrator privileges on all endpoints."
    },
    {
        "asset_name": "Customer Web Portal",
        "title": "SQL Injection & Unauthorized Data Extraction",
        "description": "Unsanitized user inputs in search API parameters allow SQL injection into the backend relational database.",
        "consequence": "Unauthorized exfiltration of customer database records and exposure of personally identifiable information.",
        "likelihood": 2,
        "impact": 3,
        "owner": "AppSec Engineer",
        "status": "In Progress",
        "notes": "Transitioning all queries to parameterized prepared statements and deploying WAF virtual patch rules."
    },
    {
        "asset_name": "Cardholder Payment Database",
        "title": "Direct Database Access via Compromised Service Account",
        "description": "Stale hardcoded credentials for a legacy reporting service are compromised by an unauthorized insider.",
        "consequence": "Severe PCI-DSS compliance failure, regulatory fines, and reputational damage.",
        "likelihood": 2,
        "impact": 3,
        "owner": "Data Security Officer",
        "status": "Open",
        "notes": "Rotating master credentials into an automated Secrets Vault and enabling strict IP whitelist on port 5432."
    },
    {
        "asset_name": "Active Directory Domain Controller",
        "title": "Privilege Escalation via Kerberoasting",
        "description": "Attackers request Kerberos service tickets for SPNs and perform offline password cracking to elevate privileges.",
        "consequence": "Full domain compromise, rogue admin account creation, and total active directory takeover.",
        "likelihood": 1,
        "impact": 3,
        "owner": "IAM Lead",
        "status": "In Progress",
        "notes": "Migrated service accounts to Group Managed Service Accounts (gMSA) with 128-bit randomized passwords."
    },
    {
        "asset_name": "Cloud Backup Storage Bucket",
        "title": "Public Bucket Misconfiguration Leading to Backup Leak",
        "description": "An accidental IAM policy modification removes public access restrictions on offsite snapshot buckets.",
        "consequence": "Exposure of entire historical database backups to public internet crawlers.",
        "likelihood": 1,
        "impact": 3,
        "owner": "Cloud Security Architect",
        "status": "Treated",
        "notes": "Enabled AWS S3 Block Public Access at the organization root level and configured KMS customer-managed keys."
    },
    {
        "asset_name": "VPN Remote Access Gateway",
        "title": "DDoS Service Disruption of Remote Workforce Access",
        "description": "Volumetric SYN flood saturates gateway WAN interface during core business hours.",
        "consequence": "Temporary inability for 300+ remote staff to access internal corporate services.",
        "likelihood": 2,
        "impact": 2,
        "owner": "Network Operations Lead",
        "status": "Closed",
        "notes": "Activated cloud scrubbing center and configured secondary upstream carrier with BGP automatic failover."
    },
    {
        "asset_name": "Corporate Employee Laptops",
        "title": "Lost Laptop with Removable Storage Vulnerability",
        "description": "An employee loses an encrypted laptop with unencrypted portable USB flash media in transit.",
        "consequence": "Minor local file loss; BitLocker prevents OS drive extraction.",
        "likelihood": 2,
        "impact": 1,
        "owner": "IT Helpdesk Lead",
        "status": "Treated",
        "notes": "Enforced USB mass storage device write-restriction policy via Intune MDM."
    }
]


def seed_database(db_path: str = DB_PATH, force: bool = False) -> None:
    """Populates seed assets and risks if database is empty or force=True."""
    init_db(db_path)
    existing_assets = get_assets(active_only=False, db_path=db_path)
    
    if len(existing_assets) > 0 and not force:
        print(f"[Seed] Database already contains {len(existing_assets)} assets. Skipping seed.")
        return

    print("[Seed] Populating realistic cybersecurity assets and risks...")
    asset_id_map = {}

    for asset_data in SAMPLE_ASSETS:
        created = create_asset(asset_data, user_id=1, username="admin", db_path=db_path)
        asset_id_map[asset_data["name"]] = created["id"]
        print(f"  + Asset: [{created['asset_id']}] {created['name']} ({created['type']})")

    for risk_data in SAMPLE_RISKS:
        asset_name = risk_data["asset_name"]
        asset_id = asset_id_map.get(asset_name)
        if not asset_id:
            continue
        
        payload = {
            "title": risk_data["title"],
            "description": risk_data["description"],
            "consequence": risk_data["consequence"],
            "asset_id": asset_id,
            "likelihood": risk_data["likelihood"],
            "impact": risk_data["impact"],
            "owner": risk_data["owner"],
            "status": risk_data["status"],
            "notes": risk_data["notes"],
            "active": 1
        }
        created = create_risk(payload, user_id=1, username="admin", db_path=db_path)
        print(f"  + Risk:  [{created['risk_id']}] {created['title']} -> Score: {created['score']} ({created['level']})")

    print("[Seed] Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
