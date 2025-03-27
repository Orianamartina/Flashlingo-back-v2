FROM python:3.10

# Set the working directory
WORKDIR /flashlingo-back

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose ports
EXPOSE 8000 8001

# Disable Python output buffering for real-time logs
ENV PYTHONUNBUFFERED=1