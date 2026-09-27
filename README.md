# Parkline Parking Management

A local web application for checking parking availability, recording vehicle entry and exit, calculating parking charges, and retaining transaction history in SQLite. The application follows the tables and KSh 50-per-hour rate described in [algorithm.md](algorithm.md).

## Requirements

- Python 3.10 or later
- pip

## Install and run

From the project directory, create a virtual environment with the Python interpreter available in this Windows workspace, then activate it in PowerShell:

```powershell
& 'C:\python314\python.exe' -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, activation is optional; use `.\.venv\Scripts\python.exe` in the commands below instead of `python`.

Install the application dependency and start the server:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. The SQLite database and tables are created automatically at `instance/parking.db`. A new database starts with 10 slots. Set `PARKING_SLOT_COUNT` before the first run to choose a different lot size; the algorithm does not prescribe a capacity. Existing slot rows and parking records are retained on restart, and changing the setting does not resize an already-created lot.

For example, to create a new lot with 12 slots in PowerShell:

```powershell
$env:PARKING_SLOT_COUNT = "12"
python app.py
```

For local development, `PARKING_DATABASE` can point to a different SQLite file. Set `PARKING_SECRET_KEY` to a private value before exposing the application beyond the local machine.

## Use

- The dashboard shows live available and occupied counts, a status tile for every slot, active vehicles, and the latest parking records.
- Enter a registration to assign the next available slot and record the local entry time. A full lot and duplicate active registrations are rejected.
- Enter or select an active registration in Vehicle exit to calculate duration and charges, complete its record, and release its slot.
- Charges follow `time spent × KSh 50 per hour`: partial hours are prorated by elapsed seconds and the resulting KSh amount is rounded to the nearest cent. This cent-rounding convention is an implementation choice because the algorithm does not specify currency precision.
- All completed visits remain in `ParkingRecords`; active visits have an empty `ExitTime` and `AmountPaid` until checkout.

## Database

SQLite creates the documented `ParkingSlots` (`SlotID`, `Status`) and `ParkingRecords` (`RecordID`, `RegistrationNumber`, `SlotNo`, `EntryTime`, `ExitTime`, `AmountPaid`) tables automatically. `SlotNo` is an enforced foreign key to `ParkingSlots.SlotID`. Database transactions and indexes prevent a slot or vehicle from having multiple active records. Entry and checkout update the slot and parking record together in one transaction.

## Tests

Run the service tests with:

```powershell
python -m unittest discover -s tests -v
```