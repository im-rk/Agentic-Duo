# Use a lightweight, modern Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# We do this before copying the rest of the code to cache the installation step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the temporary workspace directory where the agent will edit files
# chmod 777 ensures the Python subprocess has full read/write permissions
RUN mkdir -p /tmp/workspace && chmod 777 /tmp/workspace

# Copy the rest of your application code (including tasks, environment.py, etc.)
COPY . .

# Hugging Face Spaces requires a service to run on port 7860 to respond to health pings
# We use a tiny built-in Python HTTP server to pass this automated check
EXPOSE 7860
# Run the FastAPI server via Uvicorn
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]