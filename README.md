# SheetCal

This Python script converts a CSV file with event details into an ICS (calender) file, so it can imported into any calendar application. The events are processed to ensure combine contiguous times for the same event for their respective days. The times are formatted correctly, and the events are set to the Pacific Standard Time (PST) (but can changed) time zone.

## Prerequisites

Make sure you have Python installed on your system. You also need to install the following Python libraries:

- `ics`
- `pytz`

You can install these libraries using `pip`:

```
pip install ics pytz
```

Input CSV Format
The input CSV file should have the following columns:

- Date (e.g., `"24-May"`, `"25-May"`)
- Times in 2-hour intervals (e.g., `"8AM - 10AM"`, `"10AM - 12PM"`)
- Employee names in the intersections of dates and times.

## Example

```
Date,24-May,25-May,26-May,27-May,28-May,29-May,30-May,31-May,1-Jun,2-Jun
8AM - 10AM,,Shennel,Enguun,Shennel,Enguun,Jeremiah,Mecedes,Tayah (8:00 AM-9:00 AM),,
10AM - 12PM,Dyrin,Shennel,Enguun,Dyrin,Enguun,Dyrin,Jeremiah,Tayah,,
12PM - 2PM,Lana,Dyrin,Nick,Dyrin,Tayah,Dyrin,Tayah,Lana,,
2PM - 4PM,Enguun,Jeremiah,Nick,Nick,Tayah,Jeremiah,Tayah,Nick,,
4PM - 6PM,Mecedes,Jeremiah,Lana,Lana,Nick,Lana,Nick,Enguun,,
6PM - 8PM,Jeremiah,Enguun,Lana,Enguun,Shennel,Enguun,Shennel,Shennel,,
8PM - 10PM,Jeremiah,Enguun,,Enguun,Shennel,Enguun,Shennel,Shennel,,
```
## Output ICS Format
The script outputs an ICS file with the following fields for each event:

- **Subject**: Event name
- **Start date**: The date of the event (e.g., "24 May, 2024")
- **Start time**: The start time of the event (e.g., "10:00 AM")
- **End date**: The end date of the event (e.g., "24 May, 2024")
- **End time**: The end time of the shift (e.g., "12:00 PM")

## How to Run
1. Place your input CSV file in the same directory as the script.
2. Update the script with the correct input and output file names, if necessary.
2. Run the script:
	```
	python sheetcal.py input_file.csv
	```

## Code Overview
The script performs the following steps:

**1. Read and Clean CSV Data:**
   - Reads the CSV file.
   - Cleans headers, times, and data cells.
   - Removes empty characters.

**2. Convert to Nested Dictionary:**
   - Constructs a nested dictionary with dates as keys connected to another dictionary with event names keys and their times as values.
   - Merges time blocks for the same event on the same date.
   - Formats dates and times correctly.

**3. Convert to Events:**
   - Converts the nested dictionary into a list of event dictionaries.

**4. Write to ICS File:**
   - Creates an ICS file from the list of events.
   - Sets the time zone to PST.

**5. Print Schedule:**
   - Prints the schedule to the console for verification.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

# Acknowledgments
- ics library
- pytz library
