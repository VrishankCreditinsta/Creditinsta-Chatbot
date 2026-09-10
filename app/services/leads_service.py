import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Default to testing/staging or production URL if provided in environment
CREDIN_API_BASE_URL = os.getenv(
    "CREDIN_API_BASE_URL", 
    "https://credvisorapistaging.addonshareware.com"
).rstrip("/")

DASHBOARD_API = f"{CREDIN_API_BASE_URL}/api/DashBoard/GetDashboard"
LEADS_CATEGORY_API = f"{CREDIN_API_BASE_URL}/api/DashBoard/GetAllDashboard"


def fetch_lead_dashboard(token: str):
    """
    Fetches the overall dashboard summary containing lead stats (inProgress, fulfilled, etc.)
    """
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "application/json"
    }

    response = requests.get(DASHBOARD_API, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    elif isinstance(data, dict):
        return data
    return None


def fetch_leads_by_category(token: str, category_type: int = 4):
    """
    Fetches categorized leads list:
    1: Submitted, 2: Assigned, 3: Closed, 4: Total
    """
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "application/json"
    }

    url = f"{LEADS_CATEGORY_API}/{category_type}"
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data if isinstance(data, list) else []


def format_lead_summary(data: dict) -> str:
    """
    Converts lead dashboard stats into a clean summary matching CredVisor My Leads screen.
    """
    if not data:
        return "No lead information found for your account at this time."

    # In CredVisor App (MyLeadsPage):
    # Total Leads -> leadFrom (fallback: noOfLeads)
    # Closed Leads -> leadCompleted (fallback: fulfilled)
    # Assigned Leads -> leadAssigned
    # Submitted Leads -> leadSubmitted
    total_leads = data.get("leadFrom") if data.get("leadFrom") is not None else data.get("noOfLeads", 0)
    closed_leads = data.get("leadCompleted") if data.get("leadCompleted") is not None else data.get("fulfilled", 0)
    assigned_leads = data.get("leadAssigned", 0)
    submitted_leads = data.get("leadSubmitted", 0)
    in_progress = data.get("inProgress") or data.get("inProgess") or (total_leads - closed_leads)

    msg = f"Here is your leads overview:\n"
    msg += f"• Total Leads: {total_leads}\n"
    msg += f"• Closed Leads: {closed_leads}\n"
    msg += f"• Assigned Leads: {assigned_leads}\n"
    msg += f"• Submitted Leads: {submitted_leads}\n"
    if in_progress > 0:
        msg += f"• Open / In-Progress: {in_progress}\n"

    return msg.strip()


