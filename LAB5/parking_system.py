
"""Manage parking permits and check vehicles in parking zones."""

import json
import secrets
from datetime import datetime, timedelta

# In-memory parking permit database.
permits = {}
ZONES = ["A", "B", "C"]


def register_permit(vehicle_plate, zone_id, zone_records=None):
    """Register a permit for a valid vehicle and parking zone."""
    if (
        not isinstance(vehicle_plate, str)
        or not vehicle_plate.strip()
        or zone_id not in ZONES
    ):
        return None

    if zone_records is None:
        zone_records = []

    existing_permits = {
        record.get("permit")
        for record in permits.values()
        if isinstance(record, dict)
    }

    permit_no = (
        f"P{secrets.randbelow(90000) + 10000}"
    )
    while permit_no in existing_permits:
        permit_no = f"P{secrets.randbelow(90000) + 10000}"

    expiry = datetime.now() + timedelta(days=180)
    permits[vehicle_plate] = {
        "zone": zone_id,
        "permit": permit_no,
        "expiry": expiry.strftime("%Y-%m-%d"),
    }
    zone_records.append((vehicle_plate, zone_id))
    return permit_no


def revoke_permit(vehicle_plate):
    """Remove a vehicle's permit if one exists."""
    permits.pop(vehicle_plate, None)


def is_expired(vehicle_plate):
    """Check whether a vehicle's permit has expired."""
    if vehicle_plate not in permits:
        return False

    try:
        expiry_text = permits[vehicle_plate]["expiry"]
        expiry = datetime.strptime(
            expiry_text, "%Y-%m-%d"
        )
    except (KeyError, TypeError, ValueError):
        return False

    return expiry.date() < datetime.now().date()


def scan_zone(zone_id, plates_seen):
    """Return plates that lack a valid permit for this zone."""
    flagged = []

    for plate in plates_seen:
        if (
            plate not in permits
            or permits[plate]["zone"] != zone_id
            or is_expired(plate)
        ):
            flagged.append(plate)

    return flagged


def load_permit_database(file="permits.json"):
    """Load permits from a JSON file."""
    try:
        with open(file, encoding="utf-8") as database_file:
            loaded_permits = json.load(database_file)
    except (OSError, json.JSONDecodeError):
        loaded_permits = {}

    permits.clear()
    if isinstance(loaded_permits, dict):
        permits.update(loaded_permits)


def save_permit_database(file="permits.json"):
    """Save permits to a JSON file."""
    with open(file, "w", encoding="utf-8") as database_file:
        json.dump(permits, database_file, indent=2)


def set_expiry(vehicle_plate, date_text):
    """Set a vehicle's permit expiry date in YYYY-MM-DD format."""
    if vehicle_plate not in permits:
        return False

    expiry = datetime.strptime(date_text, "%Y-%m-%d")
    permits[vehicle_plate]["expiry"] = expiry.strftime(
        "%Y-%m-%d"
    )
    return True


def main():
    """Run the parking permit demonstration."""
    load_permit_database()

    register_permit("KA01AB1234", "A")
    register_permit("KA05XY9999", "Z")
    register_permit("", "B")
    register_permit(None, "C")

    set_expiry("KA01AB1234", "2020-01-01")
    revoke_permit("MH12ZZ0000")

    print(
        "Flagged in zone A:",
        scan_zone(
            "A",
            ["KA01AB1234", "KA05XY9999", "TN09QQ1111"],
        ),
    )

    plate = input("Plate to revoke (Enter to skip): ").strip()
    if plate:
        revoke_permit(plate)

    save_permit_database()
    print("Permits on file:", len(permits))


if __name__ == "__main__":
    main()
