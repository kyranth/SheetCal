# Use the official Python base image with Alpine Linux
FROM python:3.9-alpine

# Install any additional dependencies if necessary
RUN apk add --no-cache git
RUN pip install ics
RUN pip install pytz

# Set the default command to run Python
CMD ["python"]
