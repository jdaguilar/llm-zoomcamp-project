# Use the official Apache Airflow image as base
FROM apache/airflow:2.10.2

# Switch to root user to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow


# Install Python dependencies
# COPY requirements.txt /requirements.txt
# RUN pip install --no-cache-dir -r /requirements.txt

# Install additional requirements
RUN pip install --no-cache-dir \
    unstructured==0.15.13 \
    elasticsearch==8.15.1 \
    beautifulsoup4==4.12.3 \
    lxml==5.3.0 \
    sentence-transformers==3.1.1

RUN mkdir -p /opt/airflow/data/docs && mkdir -p /opt/airflow/data/clean_docs
RUN chmod -R a+rwx /opt/airflow/data

# Set the working directory
WORKDIR /opt/airflow


# The entrypoint and cmd are inherited from the base image
