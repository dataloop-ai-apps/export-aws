FROM hub.dataloop.ai/dtlpy-runner-images/cpu:python3.10_opencv

# Install boto3
RUN pip install boto3