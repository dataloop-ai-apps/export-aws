FROM dataloopai/dtlpy-agent:cpu.py3.10.opencv

# Install boto3
RUN pip install boto3