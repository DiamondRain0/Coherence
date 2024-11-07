# Use an official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements into the container (optional)
COPY requirements.txt .

# Install the necessary Python dependencies
RUN pip install -U pip \
    && pip install -r requirements.txt

# Copy your script or source code into the container
COPY . .

# Run your Python script when the container launches
CMD ["python", "your_script.py"]
