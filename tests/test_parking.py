import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from os import environ
from pathlib import Path
from unittest.mock import patch

from app import create_app
from parking.database import connect, initialize_database
from parking.service import (
    ParkingError,
    calculate_parking_fee,
    check_out_vehicle,
    park_vehicle,
    parking_overview,
)


class ParkingServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "parking.db"
        initialize_database(self.database_path, 2)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_entry_assigns_slot_and_updates_availability(self):
        ticket = park_vehicle(self.database_path, " kbc 456b ")
        overview = parking_overview(self.database_path)
        self.assertEqual(ticket["registration"], "KBC 456B")
        self.assertEqual(ticket["slot_id"], 1)
        self.assertEqual(overview["available_count"], 1)
        self.assertEqual(overview["active_records"][0]["SlotNo"], 1)

    def test_entry_is_rejected_when_lot_is_full(self):
        park_vehicle(self.database_path, "KBC 456B")
        park_vehicle(self.database_path, "KDA 789C")
        with self.assertRaisesRegex(ParkingError, "lot is full"):
            park_vehicle(self.database_path, "KDD 123A")

    def test_duplicate_active_vehicle_is_rejected(self):
        park_vehicle(self.database_path, "KBC 456B")
        with self.assertRaisesRegex(ParkingError, "already has an active"):
            park_vehicle(self.database_path, "kbc 456b")

    def test_exit_completes_record_and_releases_slot(self):
        ticket = park_vehicle(self.database_path, "KBC 456B")
        entry_time = datetime(2025, 1, 1, 8, tzinfo=timezone.utc)
        exit_time = datetime(2025, 1, 1, 9, 30, tzinfo=timezone.utc)
        with connect(self.database_path) as connection:
            connection.execute(
                "UPDATE ParkingRecords SET EntryTime = ? "
                "WHERE RegistrationNumber = ? AND ExitTime IS NULL",
                (entry_time.isoformat(), "KBC 456B"),
            )
        receipt = check_out_vehicle(self.database_path, "KBC 456B", exit_time)
        overview = parking_overview(self.database_path)
        self.assertEqual(receipt["slot_id"], ticket["slot_id"])
        self.assertEqual(receipt["duration_seconds"], 5400)
        self.assertEqual(receipt["duration"], "1h 30m 0s")
        self.assertEqual(receipt["amount_due"], Decimal("75.00"))
        self.assertEqual(overview["available_count"], 2)
        self.assertEqual(overview["active_records"], [])
        completed = overview["recent_records"][0]
        self.assertIsNotNone(completed["ExitTime"])
        self.assertEqual(Decimal(str(completed["AmountPaid"])), Decimal("75.00"))

    def test_fee_prorates_short_one_hour_and_multi_hour_durations(self):
        self.assertEqual(calculate_parking_fee(60), Decimal("0.83"))
        self.assertEqual(calculate_parking_fee(3600), Decimal("50.00"))
        self.assertEqual(calculate_parking_fee(9000), Decimal("125.00"))

    def test_exit_without_active_record_is_rejected(self):
        with self.assertRaisesRegex(ParkingError, "No active parking record"):
            check_out_vehicle(self.database_path, "KBC 456B")

    def test_empty_or_invalid_registration_is_rejected(self):
        for registration in ("", "   ", "ABC!123"):
            with self.subTest(registration=registration):
                with self.assertRaises(ParkingError):
                    park_vehicle(self.database_path, registration)

    def test_records_persist_after_reinitializing_database(self):
        park_vehicle(self.database_path, "KBC 456B")
        entry_time = datetime(2025, 1, 1, 8, tzinfo=timezone.utc)
        with connect(self.database_path) as connection:
            connection.execute(
                "UPDATE ParkingRecords SET EntryTime = ? "
                "WHERE RegistrationNumber = ? AND ExitTime IS NULL",
                (entry_time.isoformat(), "KBC 456B"),
            )
        check_out_vehicle(
            self.database_path,
            "KBC 456B",
            datetime(2025, 1, 1, 9, tzinfo=timezone.utc),
        )
        park_vehicle(self.database_path, "KDA 789C")
        initialize_database(self.database_path, 2)
        overview = parking_overview(self.database_path)
        self.assertEqual(overview["occupied_count"], 1)
        self.assertEqual(overview["available_count"], 1)
        self.assertEqual(overview["active_records"][0]["RegistrationNumber"], "KDA 789C")
        completed = next(
            record for record in overview["recent_records"]
            if record["RegistrationNumber"] == "KBC 456B"
        )
        self.assertIsNotNone(completed["ExitTime"])
        self.assertEqual(Decimal(str(completed["AmountPaid"])), Decimal("50.00"))

    def test_schema_has_documented_tables_and_foreign_key(self):
        connection = sqlite3.connect(self.database_path)
        try:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(ParkingRecords)")
            }
            foreign_keys = connection.execute(
                "PRAGMA foreign_key_list(ParkingRecords)"
            ).fetchall()
        finally:
            connection.close()
        self.assertTrue({"ParkingSlots", "ParkingRecords"}.issubset(tables))
        self.assertTrue(
            {"RecordID", "RegistrationNumber", "SlotNo", "EntryTime", "ExitTime", "AmountPaid"}
            .issubset(columns)
        )
        self.assertEqual(foreign_keys[0][2:5], ("ParkingSlots", "SlotNo", "SlotID"))

    def test_database_constraints_reject_invalid_foreign_key_and_duplicate_active_rows(self):
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """INSERT INTO ParkingRecords
                       (RegistrationNumber, SlotNo, EntryTime)
                       VALUES ('BAD 1', 99, '2025-01-01T08:00:00+00:00')"""
                )

            connection.execute(
                """INSERT INTO ParkingRecords
                   (RegistrationNumber, SlotNo, EntryTime)
                   VALUES ('KBC 456B', 1, '2025-01-01T08:00:00+00:00')"""
            )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """INSERT INTO ParkingRecords
                       (RegistrationNumber, SlotNo, EntryTime)
                       VALUES ('KDA 789C', 1, '2025-01-01T08:05:00+00:00')"""
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """INSERT INTO ParkingRecords
                       (RegistrationNumber, SlotNo, EntryTime)
                       VALUES ('KBC 456B', 2, '2025-01-01T08:05:00+00:00')"""
                )
        finally:
            connection.close()

    def test_database_rejects_invalid_slot_status(self):
        with connect(self.database_path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE ParkingSlots SET Status = 'Reserved' WHERE SlotID = 1"
                )


class ParkingWebTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "web-parking.db"
        app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-only-secret",
                "DATABASE": str(self.database_path),
                "SLOT_COUNT": 2,
            }
        )
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dashboard_renders_capacity_slots_and_fee(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Parkline", response.data)
        self.assertIn(b"2<span> / 2</span>", response.data)
        self.assertIn(b"Parking slots", response.data)
        self.assertIn(b"Vehicle entry", response.data)
        self.assertIn(b"Vehicle exit", response.data)
        self.assertIn(b"KSh", response.data)
        self.assertIn(b"LIVE LOT STATUS", response.data)
        self.assertIn(b"exact time parked", response.data)

    def test_default_capacity_is_ten_and_environment_can_configure_it(self):
        default_path = Path(self.temp_dir.name) / "default-capacity.db"
        with patch.dict(environ, {}, clear=True):
            default_app = create_app(
                {"TESTING": True, "DATABASE": str(default_path), "SECRET_KEY": "test"}
            )
        self.assertEqual(default_app.config["SLOT_COUNT"], 10)
        self.assertEqual(parking_overview(default_path)["total_count"], 10)

        configured_path = Path(self.temp_dir.name) / "configured-capacity.db"
        with patch.dict(environ, {"PARKING_SLOT_COUNT": "3"}):
            configured_app = create_app(
                {"TESTING": True, "DATABASE": str(configured_path), "SECRET_KEY": "test"}
            )
        self.assertEqual(configured_app.config["SLOT_COUNT"], 3)
        self.assertEqual(parking_overview(configured_path)["total_count"], 3)

    def test_entry_and_exit_routes_render_messages_and_updated_counts(self):
        invalid = self.client.post(
            "/entry", data={"registration": ""}, follow_redirects=True
        )
        self.assertIn(b"Enter a valid registration", invalid.data)

        response = self.client.post(
            "/entry", data={"registration": "KBC 456B"}, follow_redirects=True
        )
        self.assertIn(b"KBC 456B parked in slot 1", response.data)
        self.assertIn(b"Available spaces: 1", response.data)
        self.assertIn(b"Occupied", response.data)

        duplicate = self.client.post(
            "/entry", data={"registration": "KBC 456B"}, follow_redirects=True
        )
        self.assertIn(b"already has an active parking record", duplicate.data)

        self.client.post(
            "/entry", data={"registration": "KDA 789C"}, follow_redirects=True
        )
        full = self.client.post(
            "/entry", data={"registration": "KDD 123A"}, follow_redirects=True
        )
        self.assertIn(b"Parking lot is full", full.data)

        unknown = self.client.post(
            "/exit", data={"registration": "KDX 111A"}, follow_redirects=True
        )
        self.assertIn(b"No active parking record", unknown.data)

        checkout = self.client.post(
            "/exit", data={"registration": "KBC 456B"}, follow_redirects=True
        )
        self.assertIn(b"checked out. Duration:", checkout.data)
        self.assertIn(b"Amount due: KSh", checkout.data)
        self.assertIn(b"Available spaces: 1", checkout.data)
        self.assertIn(b"Complete", checkout.data)


if __name__ == "__main__":
    unittest.main()