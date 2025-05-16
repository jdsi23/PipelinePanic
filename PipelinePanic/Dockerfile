# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy everything from your repo into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by Flask
EXPOSE 5000

# Set Flask environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask app
CMD ["flask", "run"]
