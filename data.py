"""
data.py — Sample / Demo Data for Hospital Bed & Resource Availability Tracker
==============================================================================
ALL data in this file is FICTIONAL and created solely for academic demonstration.
No real hospital, patient, or clinical information is used.
"""

import pandas as pd
import random
from datetime import datetime, timedelta

# ── Lookup Lists ──────────────────────────────────────────────────────────────
HOSPITALS = [
    "City General Hospital",
    "Sunrise Medical Center",
    "Green Valley Hospital",
]

DEPARTMENTS = [
    "Emergency",
    "ICU",
    "General Ward",
    "Pediatrics",
    "Cardiology",
    "Orthopedics",
    "Maternity",
]

RESOURCE_TYPES = [
    "General Bed",
    "ICU Bed",
    "Ventilator",
    "Oxygen Concentrator",
    "Cardiac Monitor",
    "Infusion Pump",
]

STATUSES = ["Available", "Occupied", "Under Maintenance"]

# ── Generate Main Resource Table ──────────────────────────────────────────────
def generate_resource_data() -> pd.DataFrame:
    """
    Returns a DataFrame of fictional hospital resources.
    Columns: Hospital, Department, Resource Type, Resource ID, Status, Last Updated
    """
    random.seed(42)          # fixed seed → same data every time the app starts

    rows = []
    counter = 1

    for hospital in HOSPITALS:
        for dept in DEPARTMENTS:
            # decide how many resources this dept gets
            for rtype in RESOURCE_TYPES:
                count = random.randint(2, 6)
                for i in range(1, count + 1):
                    resource_id = f"{hospital[:3].upper()}-{dept[:3].upper()}-{rtype[:3].upper()}-{counter:03d}"
                    counter += 1

                    # weighted random status so the demo is interesting
                    status = random.choices(
                        STATUSES,
                        weights=[0.45, 0.45, 0.10],
                        k=1,
                    )[0]

                    # fake "last updated" timestamp within the last 48 h
                    hours_ago = random.randint(0, 48)
                    last_updated = datetime.now() - timedelta(hours=hours_ago)

                    rows.append(
                        {
                            "Hospital": hospital,
                            "Department": dept,
                            "Resource Type": rtype,
                            "Resource ID": resource_id,
                            "Status": status,
                            "Last Updated": last_updated.strftime("%Y-%m-%d %H:%M"),
                        }
                    )

    return pd.DataFrame(rows)


# ── Generate Historical Occupancy Data ───────────────────────────────────────
def generate_historical_data(days: int = 30) -> pd.DataFrame:
    """
    Returns a DataFrame of daily availability snapshots for the past `days` days.
    Used to draw trend charts.
    Columns: Date, Hospital, Resource Type, Total, Available, Occupied, Under Maintenance
    """
    random.seed(99)

    rows = []
    today = datetime.now().date()

    for hospital in HOSPITALS:
        for rtype in RESOURCE_TYPES:
            total = random.randint(15, 40)
            # start with a baseline occupancy
            occupied = random.randint(int(total * 0.3), int(total * 0.7))

            for d in range(days, -1, -1):
                date = today - timedelta(days=d)

                # slowly drift occupied count day by day
                drift = random.randint(-3, 3)
                occupied = max(0, min(total, occupied + drift))
                maintenance = random.randint(0, max(1, int(total * 0.05)))
                available = max(0, total - occupied - maintenance)

                rows.append(
                    {
                        "Date": date.strftime("%Y-%m-%d"),
                        "Hospital": hospital,
                        "Resource Type": rtype,
                        "Total": total,
                        "Available": available,
                        "Occupied": occupied,
                        "Under Maintenance": maintenance,
                    }
                )

    return pd.DataFrame(rows)
