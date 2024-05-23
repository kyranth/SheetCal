import sys
import csv
import time
from datetime import datetime
from ics import Calendar, Event
from datetime import datetime
import pytz

def clean_data(headers, times, data):
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
    return datetime.strptime(time_str, '%I%p').strftime('%I:%M %p')

def convert_to_nested_dict(headers, times, data):
    schedule = {}
    
    def format_date(date_str):
        date_obj = datetime.strptime(date_str, '%d-%b')
        formatted_date = date_obj.strftime('%B %d, 2024')
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
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Subject', 'Start date', 'Start time', 'End date', 'End time'])
        writer.writeheader()
        for event in events:
            writer.writerow(event)

def to_string(schedule):
    for date, employees in schedule.items():
        print(f"Date: {date}")
        for employee, shifts in employees.items():
            shift_str = ', '.join([f"{start} to {end}" for start, end in shifts])
            print(f"  Employee: {employee}, Shifts: {shift_str}")
        print()  # Add an empty line for better readability

# Reads the calendar formatted csv file
def read_events_from_csv(csv_file):
    events = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            events.append(row)
    return events

# Creates ics file
def create_ics_file(events, output_ics_file):
    calendar = Calendar()
    pst = pytz.timezone('America/Los_Angeles') # TODO: Make this option in command line
    
    for event in events:
        cal_event = Event()
        cal_event.name = event['Subject']
        
        start_datetime_str = f"{event['Start date']} {event['Start time']}"
        end_datetime_str = f"{event['End date']} {event['End time']}"
        
        start_datetime = datetime.strptime(start_datetime_str, '%B %d, %Y %I:%M %p')
        end_datetime = datetime.strptime(end_datetime_str, '%B %d, %Y %I:%M %p')
        
        start_datetime = pst.localize(start_datetime)
        end_datetime = pst.localize(end_datetime)
        
        cal_event.begin = start_datetime
        cal_event.end = end_datetime
        
        calendar.events.add(cal_event)
    
    with open(output_ics_file, mode='w') as file:
        file.writelines(calendar)

def main(input_csv):
    headers, times, data = read_schedule(input_csv)
    schedule = convert_to_nested_dict(headers, times, data)

    events = convert_to_events(schedule)
    write_events_to_csv(events, 'output_events.csv')

    time.sleep(1)

    formatted_events = read_events_from_csv('output_events.csv')
    create_ics_file(formatted_events, "output_ics.ics")

if __name__ == '__main__':
    input_csv = sys.argv[1]
    main(input_csv)
