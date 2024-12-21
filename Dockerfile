FROM python:3.10-slim

# Set the working directory to /backend inside the container
WORKDIR /

# Copy only requirements.txt first to leverage Docker cache for dependencies
COPY requirements.txt /requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files into the container
COPY ./backend/ /
COPY .env /.env

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]