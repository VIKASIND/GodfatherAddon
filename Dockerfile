FROM python:2.7-slim

# Update the package manager and install necessary dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python-pip \
    ffmpeg \
    && apt-get clean

# Upgrade pip for Python 2
RUN pip install --upgrade pip

# Install Node.js
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs

# Install npm
RUN npm install -g npm

# Copy the application code into the container
COPY . /app/

# Set the working directory
WORKDIR /app/

# Install Python 2 dependencies from requirements.txt
RUN pip install -r requirements.txt

# Define the default command to run when the container starts
CMD ["bash", "start.sh"]
