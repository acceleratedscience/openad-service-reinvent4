FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime AS runtime

# Set the environment variables for the container system
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=America/Los_Angeles \
    PYTHONUNBUFFERED=1

# Install the required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common \
    build-essential curl git ssh libxrender1 libxext6\
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Install the requirements for REINVENT4 then install REINVENT4
RUN git clone https://github.com/MolecularAI/REINVENT4.git
RUN rm REINVENT4/pyproject.toml
COPY pyproject.toml REINVENT4/ 
COPY requirements_reinvent.txt /app/requirements_reinvent.txt
RUN python -m pip install --no-cache-dir -r requirements_reinvent.txt
RUN python -m pip install REINVENT4/. 

# Install the OpenAD Service Utilities
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the network port
EXPOSE 8080

# Set the environment variables for the application
ENV HF_HOME="" \
    MPLCONFIGDIR="/tmp/.config/matplotlib" \
    LOGGING_CONFIG_PATH="/tmp/app.log" \
    gt4sd_local_cache_path="/tmp/.openad_models" \
    GT4SD_S3_HOST="" \
    gt4sd_s3_bucket_algorithms=""\
    gt4sd_s3_bucket_properties=""\
    GT4SD_S3_SECRET_KEY="" \
    GT4SD_S3_ACCESS_KEY="" \
    GT4SD_S3_HOST_HUB="" \
    GT4SD_S3_ACCESS_KEY_HUB="" \
    GT4SD_S3_SECRET_KEY_HUB="" \
    gt4sd_s3_bucket_hub_algorithms=""\
    gt4sd_s3_bucket_hub_properties=""

# Specify the command to run when the container starts
CMD ["python", "app.py"]
