import os
import json
import time
from common_utils.s3_utils import get_size

def initEBS(WORKDIR):
    if os.getenv('EBSSIZE'):
        total_size = int(os.getenv('EBSSIZE')) * 1024**3 # EBS SIZE is in GB

    # Declare expected disk usage, triggers host's EBS script (ecs-ebs-manager)
    with open("/TOTAL_SIZE", "w") as text_file:
        text_file.write("{0}".format(total_size))

    # Wait for EBS to appear
    print('Wait EBS')
    while not os.path.isdir(WORKDIR):
        time.sleep(5)

    # Wait for mount verification
    while not os.path.ismount(WORKDIR):
        time.sleep(1)

    print('EBS found')
