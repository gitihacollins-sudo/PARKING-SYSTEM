ALGORITHM
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


USE OF DATA STRUCTURES IN THE PARKING SYSTEM
 Array - Will be used to Track parking slots and their status 
 Structure-Will Store information about one vehicle eg registration number, entry time etc
 Array-Store information about many vehicles 
 Queue - Manage vehicles waiting for parking  using the principle of first in first out


Database design

Table 1: ParkingSlots

Field	       Data Type	   Key

Slot ID	     Integer     	Primary Key
Status       Text         	—

Table 2: ParkingRecords

Field                        	Data Type        	Key

Record ID                    	Integer	          Primary Key
Registration Number          	Text             	—
Slot ID                      	Integer           Foreign Key
EntryTime                    	Date/Time        	—
Exit Time                    	Date/Time	        —
Amount Paid                  	Decimal	          —


the primary key in both tables make the data to be unique
the foreign links both tables
