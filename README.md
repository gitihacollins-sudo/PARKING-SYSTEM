# Parkline Parking Management

A local web application for checking parking availability, recording vehicle entry and exit, calculating parking charges, and retaining transaction history in SQLite. The application follows the tables and KSh 50-per-hour rate described in [algorithm.md](algorithm.md).

## Requirements

- Python 3.10 or later
- pip

## Install and run

From the project directory, create and activate a virtual environment if you do not already have one:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application dependency and start the server:

```powershell
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. The SQLite database is created automatically at `instance/parking.db`. On first run the system creates 24 slots. Set `PARKING_SLOT_COUNT` before the first run to choose a different lot size. Existing slot rows and parking records are retained when the application restarts; changing the slot-count setting does not resize an already-created lot.

For local development, `PARKING_DATABASE` can point to a different SQLite file. Set `PARKING_SECRET_KEY` to a private value before exposing the application beyond the local machine.

## Use

- The dashboard shows live available and occupied counts, a status tile for every slot, active vehicles, and the latest parking records.
- Enter a registration to assign the next available slot and record the local entry time. A full lot and duplicate active registrations are rejected.
- Enter or select an active registration in Vehicle exit to calculate duration and charges, complete its record, and release its slot.
- Charges use the documented KSh 50 hourly rate. Any started hour is billed as a full hour, with a one-hour minimum. Amounts are stored as whole KSh in `AmountPaid`.
- All completed visits remain in `ParkingRecords`; active visits have an empty `ExitTime` and `AmountPaid` until checkout.

## Database

SQLite creates the documented `ParkingSlots` (`SlotID`, `Status`) and `ParkingRecords` (`RecordID`, `RegistrationNumber`, `SlotNo`, `EntryTime`, `ExitTime`, `AmountPaid`) tables automatically. `SlotNo` is a foreign key to `ParkingSlots.SlotID`. Database transactions and indexes prevent a slot or vehicle from having multiple active records.

## Tests

Run the service tests with:

```powershell
python -m unittest discover -s tests -v
```