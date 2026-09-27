import math
import re
import sqlite3
from datetime import datetime

from parking.database import connect, get_overview, write_transaction


HOURLY_RATE_KSH = 50
REGISTRATION_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9 -]{0,19}$")


class ParkingError(Exception):
    """A user-correctable parking operation error."""


def normalize_registration(registration):
    value = " ".join((registration or "").strip().upper().split())
    if not value or not REGISTRATION_PATTERN.fullmatch(value):
        raise ParkingError("Enter a valid registration (letters, numbers, spaces or hyphens).")
    return value


def parking_overview(database_path):
    return get_overview(database_path)


def park_vehicle(database_path, registration):
    vehicle = normalize_registration(registration)
    try:
        with connect(database_path) as connection:
            with write_transaction(connection):
                active = connection.execute(
                    "SELECT 1 FROM ParkingRecords "
                    "WHERE RegistrationNumber = ? AND ExitTime IS NULL",
                    (vehicle,),
                ).fetchone()
                if active:
                    raise ParkingError(f"{vehicle} already has an active parking record.")

                slot = connection.execute(
                    "SELECT SlotID FROM ParkingSlots "
                    "WHERE Status = 'Available' ORDER BY SlotID LIMIT 1"
                ).fetchone()
                if slot is None:
                    raise ParkingError("Parking lot is full. Entry has been denied.")

                entry_time = datetime.now().astimezone()
                connection.execute(
                    """INSERT INTO ParkingRecords
                       (RegistrationNumber, SlotNo, EntryTime)
                       VALUES (?, ?, ?)""",
                    (vehicle, slot["SlotID"], entry_time.isoformat(timespec="seconds")),
                )
                updated = connection.execute(
                    "UPDATE ParkingSlots SET Status = 'Occupied' "
                    "WHERE SlotID = ? AND Status = 'Available'",
                    (slot["SlotID"],),
                ).rowcount
                if updated != 1:
                    raise ParkingError("That slot is no longer available. Please try again.")

        return {
            "registration": vehicle,
            "slot_id": slot["SlotID"],
            "entry_time": entry_time.strftime("%b %d, %Y %H:%M:%S %Z"),
            "available_slots": parking_overview(database_path)["available_count"],
        }
    except sqlite3.IntegrityError as error:
        raise ParkingError("Could not create the parking record because the vehicle or slot is already active.") from error
    except sqlite3.Error as error:
        raise ParkingError("The parking database could not save this entry. Please try again.") from error


def check_out_vehicle(database_path, registration):
    vehicle = normalize_registration(registration)
    try:
        with connect(database_path) as connection:
            with write_transaction(connection):
                record = connection.execute(
                    """SELECT RecordID, SlotNo, EntryTime FROM ParkingRecords
                       WHERE RegistrationNumber = ? AND ExitTime IS NULL""",
                    (vehicle,),
                ).fetchone()
                if record is None:
                    raise ParkingError(f"No active parking record found for {vehicle}.")

                exit_time = datetime.now().astimezone()
                entry_time = datetime.fromisoformat(record["EntryTime"])
                duration_seconds = max(
                    0, math.ceil((exit_time - entry_time).total_seconds())
                )
                billable_hours = max(1, math.ceil(duration_seconds / 3600))
                amount_due = billable_hours * HOURLY_RATE_KSH
                duration_minutes = duration_seconds // 60
                hours, minutes = divmod(duration_minutes, 60)
                duration = f"{hours}h {minutes}m"

                connection.execute(
                    """UPDATE ParkingRecords
                       SET ExitTime = ?, AmountPaid = ? WHERE RecordID = ?""",
                    (
                        exit_time.isoformat(timespec="seconds"),
                        amount_due,
                        record["RecordID"],
                    ),
                )
                updated = connection.execute(
                    "UPDATE ParkingSlots SET Status = 'Available' "
                    "WHERE SlotID = ? AND Status = 'Occupied'",
                    (record["SlotNo"],),
                ).rowcount
                if updated != 1:
                    raise ParkingError("The assigned slot is not marked occupied; checkout was cancelled.")

        return {
            "registration": vehicle,
            "slot_id": record["SlotNo"],
            "duration": duration,
            "duration_seconds": duration_seconds,
            "billable_hours": billable_hours,
            "amount_due": amount_due,
            "exit_time": exit_time.strftime("%b %d, %Y %H:%M:%S %Z"),
            "available_slots": parking_overview(database_path)["available_count"],
        }
    except sqlite3.IntegrityError as error:
        raise ParkingError("The parking record could not be completed because of a data conflict.") from error
    except sqlite3.Error as error:
        raise ParkingError("The parking database could not complete checkout. Please try again.") from error