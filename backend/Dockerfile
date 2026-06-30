# Use Microsoft's official Playwright image which has Python and all browser system dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.41.1-jammy

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend source code to container
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run uvicorn server in container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
