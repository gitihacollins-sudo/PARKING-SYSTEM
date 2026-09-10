 Modern Parking System — Algorithms, Data Structures and Database Design


 1. 

### Vehicle Entry

1. **Start.**
2. Check whether there is an available parking slot.
3. If there is no available slot:
   - Deny entry.
   - Inform the driver that the parking lot is full.
4. If a slot is available:
   - Allow the vehicle to enter.
   - Assign an available parking slot to the vehicle.
   - Record the vehicle registration number.
   - Record the entry time.
   - Mark the assigned slot as **Occupied**.
   - Decrease the number of available slots by 1.

### Vehicle Exit

5. When the vehicle wants to leave, identify the vehicle using its registration number or parking record.
6. Record the exit time.
7. Calculate the time spent in the parking lot.
8. Calculate the amount to pay.
9. Display the amount to the driver.
10. Receive/record the payment.
11. Mark the vehicle's parking slot as **Available**.
12. Increase the number of available slots by 1.
13. Update the vehicle's parking record.
14. **Stop** for that transaction.

---

# 3. Example of the Algorithm

Assume a parking lot has **5 slots**.

Initially:

- Slot 1 = Occupied
- Slot 2 = Available
- Slot 3 = Available
- Slot 4 = Occupied
- Slot 5 = Available

Therefore:

**Available slots = 3**

A new vehicle arrives.

### Entry

1. The system checks available slots.
2. There are 3 available slots.
3. The system allows entry.
4. It assigns, for example, Slot 2.
5. It records the vehicle's registration number.
6. It records the entry time.
7. Slot 2 becomes Occupied.
8. Available slots decrease from 3 to 2.

### Exit

Suppose the vehicle entered at **8:00 AM** and leaves at **11:00 AM**.

Time spent:

**11:00 AM − 8:00 AM = 3 hours**

If the parking rate is **KSh 50 per hour**:

**Amount = 3 × 50 = KSh 150**

After the vehicle leaves:

- Slot 2 becomes Available.
- Available slots increase from 2 to 3.
- The exit time and amount paid are recorded.

---

# 4. Important Variables

The system can use variables such as:

| Variable | Meaning |
|---|---|
| `availableSlots` | Number of parking spaces currently available |
| `slotNo` | Parking slot assigned to a vehicle |
| `registrationNumber` | Vehicle identification number |
| `entryTime` | Time the vehicle enters |
| `exitTime` | Time the vehicle leaves |
| `timeSpent` | Total time the vehicle stayed |
| `ratePerHour` | Parking charge for one hour |
| `amountPaid` | Total amount charged/paid |

For example:

```text
availableSlots = 3
ratePerHour = 50
entryTime = 08:00
exitTime = 11:00
```

---

# 5. Pseudocode

## 5.1 Meaning of Pseudocode

**Pseudocode** is an algorithm written in a programming-like form using simple English.

It is not a specific programming language. It is used to show the logic of a program before writing actual code.

Common pseudocode words include:

- `START`
- `IF`
- `THEN`
- `ELSE`
- `END IF`
- `STOP`

## 5.2 Parking System Pseudocode

```text
START

CHECK available parking slots

IF available slots = 0 THEN
    DENY entry
    DISPLAY "Parking lot is full"

ELSE
    ALLOW entry
    ASSIGN an available parking slot
    RECORD vehicle registration number
    RECORD entry time
    MARK the slot as OCCUPIED
    DECREASE available slots by 1

END IF

WHEN vehicle wants to exit:
    ENTER/IDENTIFY registration number
    RECORD exit time
    CALCULATE time spent
    CALCULATE amount to pay
    DISPLAY amount to pay
    RECORD payment
    MARK the parking slot as AVAILABLE
    INCREASE available slots by 1
    UPDATE parking record

STOP
```

---

# 6. Data Structures

## 6.1 Meaning of a Data Structure

A **data structure** is a way of organizing and storing data so that a computer program can use the data efficiently.

The parking system contains different types of data, so more than one data structure can be useful.

The main data structures are:

1. Array
2. Structure/Record
3. List/Array of Records
4. Queue

A stack is **not necessary** for the basic parking system.

---

# 7. Array

## 7.1 Meaning

An **array** stores multiple values of the same general type in an organized sequence.

An array is suitable for tracking parking slots because each slot can have a status such as:

- Available
- Occupied

Example:

```text
Slots = [Occupied, Available, Available, Occupied, Available]
```

This represents:

| Slot | Status |
|---|---|
| 1 | Occupied |
| 2 | Available |
| 3 | Available |
| 4 | Occupied |
| 5 | Available |

There are therefore **3 available slots**.

## 7.2 Why an Array is Suitable

An array makes it easy for the system to:

- Keep track of all parking slots.
- Find an available slot.
- Change a slot from Available to Occupied.
- Change a slot from Occupied to Available.

---

# 8. Structure/Record

## 8.1 Meaning

A **structure/record** groups different pieces of information belonging to one entity.

A vehicle needs several different types of information, so a structure/record is suitable.

Example:

```text
Vehicle:
    RegistrationNumber
    SlotNo
    EntryTime
    ExitTime
    AmountPaid
```

One vehicle could therefore have:

```text
RegistrationNumber = KBC 456B
SlotNo = 5
EntryTime = 08:00
ExitTime = 11:00
AmountPaid = 150
```

## 8.2 Why a Structure/Record is Suitable

The information belongs to the same vehicle.

Instead of treating the registration number, slot number, entry time, exit time and payment as unrelated pieces of information, a record groups them together.

---

# 9. List/Array of Records

A single structure/record stores information about **one vehicle**.

But a parking lot contains many vehicles.

Therefore, we can use a **list or array of records**.

Example:

```text
ParkingRecords = [
    Vehicle 1,
    Vehicle 2,
    Vehicle 3,
    Vehicle 4
]
```

Each vehicle can have:

```text
Vehicle:
    RegistrationNumber
    SlotNo
    EntryTime
    ExitTime
    AmountPaid
```

This allows the system to store information about many vehicles.

### Important distinction

- **Structure/Record** → stores details of one vehicle.
- **Array/List of Records** → stores details of many vehicles.

---

# 10. Queue

## 10.1 Meaning

A **queue** follows the principle:

**FIFO = First In, First Out**

The vehicle that enters the waiting queue first should be considered first when a parking slot becomes available.

Example:

```text
Waiting Queue:

Front → KCA 101A → KCB 202B → KDC 303C → Rear
```

If a parking slot becomes available, **KCA 101A** is handled first.

## 10.2 Why a Queue is Useful

A queue is useful when:

- The parking lot is full.
- Vehicles are waiting to enter.
- The system wants to process waiting vehicles fairly in arrival order.

---

# 11. Why a Stack is Not the Best Choice

A **stack** follows:

**LIFO = Last In, First Out**

This means the last item added is the first item removed.

That does not naturally represent a normal parking system because vehicles do not necessarily leave in reverse order of arrival.

For example:

```text
Car A enters
Car B enters
Car C enters
```

A stack would expect:

```text
C leaves first
B leaves second
A leaves last
```

But in a normal parking lot, Car A could leave before Car C.

Therefore:

**Stack is not the best primary data structure for tracking normal parking vehicles.**

---

# 12. Data Structure Summary

| Data Structure | Purpose in Parking System |
|---|---|
| Array | Track parking slots and their status |
| Structure/Record | Store information about one vehicle |
| Array/List of Records | Store information about many vehicles |
| Queue | Manage vehicles waiting for parking |
| Stack | Not normally required for the basic system |

---

# 13. Database

## 13.1 Meaning of a Database

A **database** is an organized collection of data that can be stored, retrieved, updated and managed by a computer system.

The database allows the parking system to keep information even after the program is closed.

This is different from a temporary data structure used while the program is running.

### Simple distinction

**Data structure:**

> How data is organized for processing by the program.

**Database:**

> Where data is stored and managed persistently.

---

# 14. Database Tables

For this parking system, two important tables are:

1. `ParkingSlots`
2. `ParkingRecords`

---

# 15. ParkingSlots Table

This table stores information about the parking spaces.

| Column | Description |
|---|---|
| `SlotID` | Unique number identifying a parking slot |
| `Status` | Shows whether the slot is Available or Occupied |

Example:

| SlotID | Status |
|---:|---|
| 1 | Occupied |
| 2 | Available |
| 3 | Available |
| 4 | Occupied |
| 5 | Available |

## Primary Key

`SlotID` is the **Primary Key**.

A primary key uniquely identifies each row in a table.

For example:

```text
SlotID = 1
SlotID = 2
SlotID = 3
```

Each slot has its own unique ID.

---

# 16. ParkingRecords Table

This table stores information about vehicles and their parking transactions.

| Column | Description |
|---|---|
| `RecordID` | Unique identifier for a parking transaction |
| `RegistrationNumber` | Vehicle registration number |
| `SlotNo` | Parking slot used by the vehicle |
| `EntryTime` | Time the vehicle entered |
| `ExitTime` | Time the vehicle left |
| `AmountPaid` | Amount charged/paid |

Example:

| RecordID | RegistrationNumber | SlotNo | EntryTime | ExitTime | AmountPaid |
|---:|---|---:|---|---|---:|
| 1 | KBC 456B | 5 | 08:00 | 11:00 | 150 |
| 2 | KDA 789C | 2 | 09:30 | 12:30 | 150 |

---

# 17. Primary Key and Foreign Key

## Primary Key

A **Primary Key** uniquely identifies a record in a table.

In `ParkingRecords`:

```text
RecordID
```

is the primary key.

In `ParkingSlots`:

```text
SlotID
```

is the primary key.

## Foreign Key

A **Foreign Key** is a field used to connect one table to another.

In this system:

```text
ParkingRecords.SlotNo
```

can reference:

```text
ParkingSlots.SlotID
```

This tells the database which parking slot is associated with a vehicle's parking record.

---

# 18. Relationship Between the Tables

The relationship can be represented as:

```text
ParkingSlots
-----------------
SlotID (PK)
Status
       |
       | SlotID
       |
       ↓
ParkingRecords
-----------------
RecordID (PK)
RegistrationNumber
SlotNo (FK)
EntryTime
ExitTime
AmountPaid
```

### Example

Suppose:

```text
ParkingSlots
SlotID = 5
Status = Occupied
```

and:

```text
ParkingRecords
RegistrationNumber = KBC 456B
SlotNo = 5
```

The `SlotNo = 5` tells us that vehicle **KBC 456B** is using parking slot **5**.

---

# 19. Why Vehicle Details Should Not Be Stored in ParkingSlots

The `ParkingSlots` table should mainly describe the parking spaces.

For example:

```text
SlotID | Status
5      | Occupied
```

The detailed vehicle information belongs in `ParkingRecords`:

```text
RegistrationNumber
EntryTime
ExitTime
AmountPaid
```

This keeps the database organized and separates:

- Information about parking spaces.
- Information about vehicle parking transactions.

---

# 20. Complete System Flow

The complete system can be understood as:

```text
                 START
                    |
                    ↓
        Check available parking slots
                    |
          ┌─────────┴─────────┐
          ↓                   ↓
       No slot             Slot available
          |                   |
          ↓                   ↓
     Deny entry          Allow entry
                              |
                              ↓
                       Assign parking slot
                              |
                              ↓
                       Record vehicle
                              |
                              ↓
                       Record entry time
                              |
                              ↓
                    Mark slot as Occupied
                              |
                              ↓
                  Decrease available slots
                              |
                              ↓
                    Vehicle eventually exits
                              |
                              ↓
                     Record exit time
                              |
                              ↓
                    Calculate time spent
                              |
                              ↓
                     Calculate amount
                              |
                              ↓
                    Record amount paid
                              |
                              ↓
                    Mark slot Available
                              |
                              ↓
                  Increase available slots
                              |
                              ↓
                             STOP
```

---

# 21. Parking Fee Calculation

The basic formula is:

```text
Time Spent = Exit Time - Entry Time
```

Then:

```text
Amount to Pay = Time Spent × Rate Per Hour
```

Example:

```text
Entry Time = 8:00 AM
Exit Time = 11:00 AM
Rate = KSh 50 per hour
```

Therefore:

```text
Time Spent = 3 hours

Amount = 3 × 50

Amount = KSh 150
```

---

# 22. Important System Updates

When a vehicle **enters**:

```text
Available slots = Available slots - 1
```

When a vehicle **exits**:

```text
Available slots = Available slots + 1
```

Example:

```text
Before entry:
Available slots = 3

Vehicle enters:
3 - 1 = 2

Available slots = 2
```

When that vehicle leaves:

```text
2 + 1 = 3

Available slots = 3
```

This is important because the system must always display the correct number of available spaces.

---

# 23. Complete Assignment Answer Structure

If submitting this as an assignment, organize the work in this order:

## 1. Problem Statement

Describe what the parking system must do.

## 2. Algorithm

Explain the step-by-step process for vehicle entry and exit.

## 3. Pseudocode

Convert the algorithm into programming-style English.

## 4. Data Structures

Describe:

- Array
- Structure/Record
- List/Array of Records
- Queue

Also explain why a stack is not the best choice.

## 5. Database Design

Create:

- `ParkingSlots`
- `ParkingRecords`

Identify:

- Primary Keys
- Foreign Key
- Fields/attributes
- Relationship between tables

## 6. Fee Calculation

Show how parking duration and payment are calculated.

---

# 24. Key Concepts to Remember

### Algorithm

**Step-by-step instructions for solving a problem.**

### Pseudocode

**An algorithm written in simple programming-like English.**

### Array

**Used to organize multiple values, such as parking slot statuses.**

### Structure/Record

**Used to group information belonging to one vehicle.**

### List/Array of Records

**Used to store information about many vehicles.**

### Queue

**FIFO — First In, First Out. Useful for vehicles waiting to enter.**

### Stack

**LIFO — Last In, First Out. Not normally required for the basic parking system.**

### Database

**Organized storage for persistent system data.**

### Table

**A structured collection of related records in a database.**

### Primary Key

**Uniquely identifies a record in a table.**

### Foreign Key

**Connects related tables.**

### ParkingSlots

**Stores information about parking spaces.**

### ParkingRecords

**Stores information about vehicles and their parking transactions.**

---

# 25. Final Mental Model

Think of the system as four connected parts:

```text
ALGORITHM
    ↓
Tells the system what steps to perform.

DATA STRUCTURES
    ↓
Organize the data while the system processes it.

DATABASE
    ↓
Permanently stores important information.

USER/SYSTEM OUTPUT
    ↓
Shows availability, entry information, time spent,
and amount to pay.
```

The complete parking system therefore works like this:

```text
Vehicle arrives
      ↓
Check availability
      ↓
Assign slot
      ↓
Record vehicle + entry time
      ↓
Mark slot occupied
      ↓
Vehicle parks
      ↓
Vehicle exits
      ↓
Record exit time
      ↓
Calculate duration
      ↓
Calculate payment
      ↓
Record transaction
      ↓
Free the slot
      ↓
Increase available slots
```

This is the core logic of the modern parking system discussed.
