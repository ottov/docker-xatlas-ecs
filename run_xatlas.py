#!/usr/bin/env python
from __future__ import print_function

import os
import time
import json
from argparse import ArgumentParser
from common_utils.xatlas_run import run_xatlas_basic
from common_utils.s3_utils import download_file,upload_folder
from common_utils.ebs_utils import initEBS

WORKDIR = '/scratch'

##
# ENV: DEBUG, GETEBS, EBSSIZE

def parse_args(argparser = ArgumentParser()):
    file_path_group = argparser.add_argument_group(title='File paths')
    file_path_group.add_argument('--ref_s3_path', type=str, help='ref genome s3 path', required=True)
    file_path_group.add_argument('--sample_s3_path', type=str, help='input file s3 path', required=True)
    file_path_group.add_argument('--results_s3_path', type=str, help='results s3 path', required=True)
    file_path_group.add_argument('--sample_name', type=str, help='sample name', required=True)

    app_args_group = argparser.add_argument_group(title='XATLAS Arguments')
    app_args_group.add_argument('--threads', type=str, default=1, help='xatlas threads', required=False)
    app_args_group.add_argument('--regions', type=str, default='', help='xatlas regions file in BED format', required=False)

    return argparser

def download_required_files(download_dir, *args):

    fList = []
    for f in args:
        print("Downloading {}".format(f))
        downloaded_path = download_file(f, download_dir)
        print("file downloaded to {}".format(downloaded_path))
        fList.append(downloaded_path)

    return fList

def main():
    argparser = parse_args()
    args, extr = argparser.parse_known_args()
    print(args)

    ref_idx = args.ref_s3_path + '.fai'

    if args.sample_s3_path.rpartition('.')[-1] == 'bam':
      input_idx = args.sample_s3_path + '.bai'
    elif args.sample_s3_path.rpartition('.')[-1] == 'cram':
      input_idx = args.sample_s3_path + '.crai'
    else:
      raise Exception("Unknown input type")


    if os.getenv('GETEBS'):
        initEBS(WORKDIR)
    else:
        if not os.path.exists(WORKDIR):
            os.mkdir(WORKDIR)

    ref_path, ref_idx_path, input_path, idx_path, region_path = download_required_files(WORKDIR,
                                               args.ref_s3_path, ref_idx,
                                               args.sample_s3_path,
                                               input_idx,
                                               args.regions
                                               )

    output_dir = WORKDIR + '/results'
    os.mkdir(output_dir)
    output_prefix = output_dir + '/{SAMPLE}.hg38.realign.bqsr'.format(SAMPLE=args.sample_name)

    # Run program
    run_xatlas_basic(args.sample_name, input_path, ref_path, args.threads, region_path, output_prefix, output_dir)

    if not os.getenv('SKIP_UPLOAD'):
      print("Uploading to %s" % (args.results_s3_path) )
      upload_folder(args.results_s3_path, output_dir)

    print ("Completed xatlas for %s" % args.sample_name)


if __name__ == '__main__':
    main()
