FROM python:3.11-slim

# Install git for cloning (optional if you pull dependencies)
RUN apt-get update && apt-get install -y git

WORKDIR /app

# Copy source
COPY distobject/ distobject/
COPY examples/ examples/
COPY setup.py .

# Install as editable package
RUN pip install --upgrade pip
RUN pip install -e .

# Default command: run the main async example
CMD ["python3", "examples/main.py"]
