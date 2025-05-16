# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy everything from your repo into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Cloud Run requires
EXPOSE 8080

# Run the app using Python instead of flask CLI so PORT works
CMD ["python", "main.py"]
