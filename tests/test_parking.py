import sqlite3
import tempfile
import unittest
from pathlib import Path

from parking.database import initialize_database
from parking.service import ParkingError, check_out_vehicle, park_vehicle, parking_overview


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
        receipt = check_out_vehicle(self.database_path, "KBC 456B")
        overview = parking_overview(self.database_path)
        self.assertEqual(receipt["slot_id"], ticket["slot_id"])
        self.assertGreaterEqual(receipt["amount_due"], 50)
        self.assertEqual(overview["available_count"], 2)
        self.assertEqual(overview["active_records"], [])
        completed = overview["recent_records"][0]
        self.assertIsNotNone(completed["ExitTime"])
        self.assertEqual(completed["AmountPaid"], receipt["amount_due"])

    def test_exit_without_active_record_is_rejected(self):
        with self.assertRaisesRegex(ParkingError, "No active parking record"):
            check_out_vehicle(self.database_path, "KBC 456B")

    def test_empty_or_invalid_registration_is_rejected(self):
        for registration in ("", "   ", "ABC!123"):
            with self.subTest(registration=registration):
                with self.assertRaises(ParkingError):
                    park_vehicle(self.database_path, registration)

    def test_records_persist_after_reinitializing_database(self):
        ticket = park_vehicle(self.database_path, "KBC 456B")
        initialize_database(self.database_path, 2)
        overview = parking_overview(self.database_path)
        self.assertEqual(overview["occupied_count"], 1)
        self.assertEqual(overview["active_records"][0]["RegistrationNumber"], "KBC 456B")
        self.assertEqual(overview["active_records"][0]["SlotNo"], ticket["slot_id"])

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


if __name__ == "__main__":
    unittest.main()