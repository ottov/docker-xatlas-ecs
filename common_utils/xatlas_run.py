from __future__ import print_function
import os
import sys
import shlex
import socket
import subprocess
from common_utils.s3_utils import download_file,get_aws_session,file_exists

def fixResolv():
    """
    Fix issue with gethostname() in MPI calls
    """
    with open("/etc/hosts", "a") as hostsfile:
       hostsfile.write('127.0.0.1 %s\n' % (socket.gethostname()) )

def exportSession():
    if not os.getenv('AWS_SESSION_TOKEN'):
        cred = get_aws_session()
        os.environ['AWS_ACCESS_KEY_ID'] = cred.access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = cred.secret_key
        os.environ['AWS_SESSION_TOKEN'] = cred.token

        fixResolv()

def run_xatlas_basic(sample_name, input_path, ref_path, output_prefix, log_dir):
    """
    Runs xatlas (/usr/bin/xatlas)
    :param sample_name: sample name
    :param input_path: input BAM/CRAM requires associated index
    :param ref_path: reference sequence in FASTA with index
    :param output_prefix: results file prefix
    """
    print ("Running xatlas")
    exportSession()

    cmd = 'xatlas -g -z -r {REF} -i {INPUT} -s {SAMPLE} -p {OUTPUT} '.format(
                 REF=ref_path,
                 INPUT=input_path,
                 SAMPLE=sample_name,
                 OUTPUT=output_prefix)

    print('Running cmd:= ', end='')
    print(cmd)

    try:
        #subprocess.check_call(shlex.split(cmd))
        process = subprocess.Popen(shlex.split(cmd), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with open(log_dir + '/xatlas-{SAMPLE}.log'.format(SAMPLE=sample_name), 'w') as log_file:
          for line in process.stdout:
             print(line, end='')
             log_file.write(line)

        return True
    except subprocess.CalledProcessError as e:
        raise


def checkUploadExists(localFileName, results_path):
    uploadFileName = os.path.basename(localFileName)
    return file_exists(results_path.rstrip('/') + '/' + uploadFileName.lstrip('/'))

