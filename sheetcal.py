import sys
import csv
import time
import logging
from datetime import datetime
from ics import Calendar, Event
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_data(headers, times, data):
    """
    Cleans the provided headers, times, and data.

    Parameters:
    headers (list of str): The list of header strings, typically dates, that need to be stripped of leading and trailing whitespace.
    times (list of str): The list of time strings that need to be stripped of leading and trailing whitespace. Empty strings or strings with only whitespace are removed.
    data (list of list of str): The 2D list representing rows of data, where each cell in a row needs to be stripped of leading and trailing whitespace. Empty cells are replaced with an empty string.

    Returns:
    tuple: A tuple containing three elements:
        - cleaned_headers (list of str): The cleaned list of headers.
        - cleaned_times (list of str): The cleaned list of times with no empty or whitespace-only strings.
        - cleaned_data (list of list of str): The cleaned 2D list of data with all cells stripped of whitespace and empty cells replaced with empty strings.
    """
    # Clean headers (dates)
    cleaned_headers = [header.strip() for header in headers]
    
    # Clean times
    cleaned_times = [time.strip() for time in times if time.strip()]
    
    # Clean data rows and remove empty cells
    cleaned_data = []
    for row in data:
        cleaned_row = [cell.strip() if cell else '' for cell in row]
        cleaned_data.append(cleaned_row)
    
    return cleaned_headers, cleaned_times, cleaned_data

def read_schedule(csv_file):
    """
    Reads a schedule from a CSV file and cleans the data.

    Parameters:
    csv_file (str): The path to the CSV file to be read.

    Returns:
    tuple: A tuple containing three elements:
        - headers (list of str): The cleaned list of headers from the CSV file.
        - times (list of str): The cleaned list of times from the first column of the CSV file, excluding the header.
        - data (list of list of str): The cleaned 2D list of data from the CSV file, excluding the first column and the header.
    """
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        
        # Read the times from the first column (excluding the header)
        times = []
        for row in reader:
            times.append(row[0])
        
        # Rewind the reader to the beginning to read the file again
        file.seek(0)
        reader = csv.reader(file)
        next(reader)  # skip the header
        
        # Read the data
        data = [row for row in reader]
        
    # Clean the data
    headers, times, data = clean_data(headers, times, data)
    
    return headers, times, data

def format_time(time_str):
    """
    Formats a time string from a 12-hour clock format without minutes to a standard 12-hour clock format with minutes.

    Parameters:
    time_str (str): A string representing the time in the format '%I%p', where '%I' is the hour (01 to 12) and '%p' is AM or PM.
    
    Returns:
    str: The formatted time string in the format '%I:%M %p', where '%I' is the hour (01 to 12), '%M' are minutes (always '00' in this case), and '%p' is AM or PM.
    """
    return datetime.strptime(time_str, '%I%p').strftime('%I:%M %p')

def convert_to_nested_dict(headers, times, data):
    """
    Converts provided data into a nested dictionary for readability and parsing.

    Parameters:
    headers (list of str): The list of header strings of dates
    times (list of str): The list of time strings
    data (list of list of str): The 2D list representing rows of data
    """
    schedule = {}
    
    def format_date(date_str):
        # Parse the date using the day and month
        day, month = date_str.split('/')
        
        # Create a datetime object assuming the current year
        date_obj = datetime(year=datetime.now().year, month=int(month), day=int(day))
        
        # Format the date to MM/DD/YYYY
        formatted_date = date_obj.strftime('%m/%d/%Y') # <- formats the output csv file like this

        return formatted_date

    headers = [format_date(date) for date in headers[1:]]  # Skip the first column header
    
    for i, time in enumerate(times):
        if ' - ' in time:
            start_time, end_time = time.split(' - ')
            start_time, end_time =format_time(start_time.strip()), format_time(end_time.strip())
            for j, date in enumerate(headers):
                if len(data[i]) > j+1 and data[i][j+1]:  # Ensure there's enough columns and data is present
                    employee_names = data[i][j+1].split(', ')
                    if date not in schedule:
                        schedule[date] = {}
                    for employee in employee_names:
                        employee = employee.strip()
                        if employee not in schedule[date]:
                            schedule[date][employee] = []
                        # Check for overlapping or contiguous shifts
                        if schedule[date][employee] and schedule[date][employee][-1][1] == start_time:
                            schedule[date][employee][-1] = (schedule[date][employee][-1][0], end_time)
                        else:
                            schedule[date][employee].append((start_time, end_time))
    return schedule

def convert_to_events(schedule):
    """
    Converts a schedule dictionary into a list of event dictionaries.

    Parameters:
    schedule (dict): A dictionary where keys are dates (str), and values are dictionaries.
                     The inner dictionaries have employee names (str) as keys and lists of tuples as values.
                     Each tuple represents a shift with a start time (str) and an end time (str).

    Returns:
    list of dict: A list of event dictionaries, where each dictionary contains:
        - 'Subject' (str): The name of the employee.
        - 'Start date' (str): The date of the shift.
        - 'Start time' (str): The start time of the shift.
        - 'End date' (str): The date of the shift (same as 'Start date').
        - 'End time' (str): The end time of the shift.
    """
    events = []
    for date, employees in schedule.items():
        for employee, shifts in employees.items():
            for start_time, end_time in shifts:
                events.append({
                    'Subject': employee,
                    'Start date': date,
                    'Start time': start_time,
                    'End date': date,
                    'End time': end_time
                })
    return events

def write_events_to_csv(events, output_file):
    """
    Writes a list of event dictionaries to a CSV file.

    Parameters:
    events (list of dict): A list of event dictionaries, where each dictionary contains:
        - 'Subject' (str): The name of the employee.
        - 'Start date' (str): The date of the shift.
        - 'Start time' (str): The start time of the shift.
        - 'End date' (str): The date of the shift (same as 'Start date').
        - 'End time' (str): The end time of the shift.
    output_file (str): The path to the output CSV file.

    Returns:
    None
    """
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Subject', 'Start date', 'Start time', 'End date', 'End time'])
        writer.writeheader()
        for event in events:
            writer.writerow(event)

def to_string(schedule):
    """
    Prints the schedule dictionary in a readable string format.

    Parameters:
    schedule (dict): A dictionary where keys are dates (str), and values are dictionaries.
                     The inner dictionaries have employee names (str) as keys and lists of tuples as values.
                     Each tuple represents a shift with a start time (str) and an end time (str).

    Returns:
    None
    """
    for date, employees in schedule.items():
        print(f"Date: {date}")
        for employee, shifts in employees.items():
            shift_str = ', '.join([f"{start} to {end}" for start, end in shifts])
            print(f"  Employee: {employee}, Shifts: {shift_str}")
        print()  # Add an empty line for better readability

def read_events_from_csv(csv_file):
    """
    Reads events from a CSV file and returns them as a list of dictionaries.

    Parameters:
    csv_file (str): The path to the input CSV file.

    Returns:
    list of dict: A list of event dictionaries, where each dictionary contains:
        - 'Subject' (str): The name of the employee.
        - 'Start date' (str): The date of the shift.
        - 'Start time' (str): The start time of the shift.
        - 'End date' (str): The date of the shift.
        - 'End time' (str): The end time of the shift.
    """
    events = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            events.append(row)
    return events

def create_ics_file(events, output_ics_file, timezone):
    """
    Creates an ICS file from a list of event dictionaries.

    Parameters:
    events (list of dict): A list of event dictionaries, where each dictionary contains:
        - 'Subject' (str): The name of the employee.
        - 'Start date' (str): The start date of the event in the format '%B %d, %Y'.
        - 'Start time' (str): The start time of the event in the format '%I:%M %p'.
        - 'End date' (str): The end date of the event in the format '%B %d, %Y'.
        - 'End time' (str): The end time of the event in the format '%I:%M %p'.
    output_ics_file (str): The path to the output ICS file.
    timezone (str): The timezone for the events (e.g., 'America/New_York').

    Returns:
    None
    """
    calendar = Calendar()
    time_zone = pytz.timezone(timezone)
    
    for event in events:
        cal_event = Event()
        cal_event.name = event['Subject']
        
        start_datetime_str = f"{event['Start date']} {event['Start time']}"
        end_datetime_str = f"{event['End date']} {event['End time']}"
        
        start_datetime = datetime.strptime(start_datetime_str, '%m/%d/%Y %I:%M %p')
        end_datetime = datetime.strptime(end_datetime_str, '%m/%d/%Y %I:%M %p')
        
        start_datetime = time_zone.localize(start_datetime)
        end_datetime = time_zone.localize(end_datetime)
        
        cal_event.begin = start_datetime
        cal_event.end = end_datetime
        
        calendar.events.add(cal_event)
    
    with open(output_ics_file, mode='w') as file:
        file.writelines(calendar)

def main(input_csv, timezone='America/Los_Angeles'):
    """
    Main function to process a schedule CSV file, convert it to a list of events, write the events to a CSV file, and then create an ICS file.

    Parameters:
    input_csv (str): The path to the input CSV file containing the schedule.
    timezone (str): The timezone for the events (e.g., 'America/Los_Angeles' Default).

    Returns:
    None
    """
    headers, times, data = read_schedule(input_csv)
    schedule = convert_to_nested_dict(headers, times, data)

    events = convert_to_events(schedule)
    write_events_to_csv(events, 'output_events.csv')

    time.sleep(1)

    formatted_events = read_events_from_csv('output_events.csv')
    create_ics_file(formatted_events, "output_ics.ics", timezone) # takes events, writes file, in given timezone

if __name__ == '__main__':
    input_csv = sys.argv[1]
    # timezone = sys.argv[2]
    main(input_csv) # input_file and timezone
