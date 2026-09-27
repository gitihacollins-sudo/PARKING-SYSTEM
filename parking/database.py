import sqlite3
from contextlib import contextmanager
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS ParkingSlots (
    SlotID INTEGER PRIMARY KEY,
    Status TEXT NOT NULL DEFAULT 'Available'
        CHECK (Status IN ('Available', 'Occupied'))
);

CREATE TABLE IF NOT EXISTS ParkingRecords (
    RecordID INTEGER PRIMARY KEY,
    RegistrationNumber TEXT NOT NULL,
    SlotNo INTEGER NOT NULL REFERENCES ParkingSlots(SlotID),
    EntryTime TEXT NOT NULL,
    ExitTime TEXT,
    AmountPaid REAL CHECK (AmountPaid IS NULL OR AmountPaid >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_record_per_slot
    ON ParkingRecords(SlotNo) WHERE ExitTime IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS one_active_record_per_vehicle
    ON ParkingRecords(RegistrationNumber) WHERE ExitTime IS NULL;
CREATE INDEX IF NOT EXISTS records_by_registration
    ON ParkingRecords(RegistrationNumber);
"""


@contextmanager
def connect(database_path):
    connection = sqlite3.connect(database_path, timeout=10, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def write_transaction(connection):
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()


def initialize_database(database_path, slot_count):
    if slot_count < 1:
        raise ValueError("The parking lot must have at least one slot")
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as connection:
        connection.executescript(SCHEMA)
        existing_slots = connection.execute(
            "SELECT COUNT(*) FROM ParkingSlots"
        ).fetchone()[0]
        if existing_slots == 0:
            connection.executemany(
                "INSERT INTO ParkingSlots (SlotID, Status) VALUES (?, 'Available')",
                ((slot_id,) for slot_id in range(1, slot_count + 1)),
            )


def get_overview(database_path):
    with connect(database_path) as connection:
        slots = connection.execute(
            "SELECT SlotID, Status FROM ParkingSlots ORDER BY SlotID"
        ).fetchall()
        active_records = connection.execute(
            """SELECT RecordID, RegistrationNumber, SlotNo, EntryTime
               FROM ParkingRecords WHERE ExitTime IS NULL
               ORDER BY EntryTime"""
        ).fetchall()
        recent_records = connection.execute(
            """SELECT RecordID, RegistrationNumber, SlotNo, EntryTime, ExitTime, AmountPaid
               FROM ParkingRecords ORDER BY RecordID DESC LIMIT 8"""
        ).fetchall()
    return {
        "slots": [dict(row) for row in slots],
        "active_records": [dict(row) for row in active_records],
        "recent_records": [dict(row) for row in recent_records],
        "available_count": sum(row["Status"] == "Available" for row in slots),
        "occupied_count": sum(row["Status"] == "Occupied" for row in slots),
        "total_count": len(slots),
    }