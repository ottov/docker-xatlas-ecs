FROM python:3-slim

# Metadata
LABEL container.base.image="python"
LABEL software.name="xatlas"
LABEL software.version=0.0.5
LABEL tags="Genomics"


# software dependencies
RUN pip install boto3 awscli

# Add pre-built binary
COPY bin/xatlas /usr/bin/

# Application entry point
COPY run_xatlas.py /run_xatlas.py
COPY common_utils /common_utils

ENTRYPOINT ["python", "-u", "/run_xatlas.py"]
