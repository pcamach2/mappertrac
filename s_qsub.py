#!/usr/bin/env python3
import argparse
import sys
from subscripts.utilities import *
from os.path import exists,join,split,splitext,abspath,basename,isdir
from os import system,mkdir,remove,environ,makedirs
from math import floor,ceil
from glob import glob

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    n = int(n)
    for i in range(0, len(l), n):
        yield l[i:i + n]

parser = argparse.ArgumentParser(description='Run parallel script using PBSBatchMaster')
parser.add_argument('subject_list',help='Text file with list of subject directories.')
parser.add_argument('output_dir',help='The super-directory that will contain output directories for each subject')
parser.add_argument('script',help='Script to run in parallel')
# parser.add_argument('--force',help='Force re-compute if output already exists',action='store_true')
# parser.add_argument('--output_time',help='Print completion time',action='store_true')
parser.add_argument('--use_input',help='Add an input argument before the subject dir argument',action='store_true')
parser.add_argument('--max_jobs',help='Max jobs per Moab batch script',default=36)
parser.add_argument('--max_time',help='Walltime of batch script',default=7)
parser.add_argument('--cpus_per_job',help='Number of CPUs per job',default=36)
parser.add_argument('--use_cuda8',help='Request a gpu per job, load CUDA 8.0',action='store_true')
# parser.add_argument('--bank',help='Name of SLURM bank',default='ccp')
args,unknownargs = parser.parse_known_args()
# args = parser.parse_args()
if unknownargs:
    print("Passing additional arguments to script: {}".format(unknownargs))
qsub = join('qsub','arguments')

# force = "--force" if args.force else ""
# output_time = "--output_time" if args.output_time else ""

odir = abspath(args.output_dir)
if not isdir(odir):
    makedirs(odir)

if not isdir("qsub"):
    mkdir("qsub")

lines = []
with open(args.subject_list) as f:
    for line in f.readlines():
        lines.append(line.strip())
input_dirs = list(chunks(lines, args.max_jobs))

i=0
for chunk in input_dirs:
    with open('{}{}.list'.format(qsub,i),'w') as f:
        for input_dir in chunk:
            sdir = join(odir, basename(input_dir))
            if not isdir(sdir):
                mkdir(sdir)
            if args.use_input:
                f.write(input_dir + ' ' + sdir + '\n')
            else:
                f.write(sdir + '\n')
    i+=1

i=0
gpu = "True" if args.use_cuda8 else "False"
qsubs = []
for chunk in input_dirs:
    pbs_cmd = ("python batch_scripts/PBSBatchMaster.py" 
               + " {}{}.list {} {} {} {}".format(qsub,i,len(chunk),args.cpus_per_job,gpu,args.max_time)
               + " python3 {}".format(args.script)
               + " --input"
               # + " --input {} {}".format(force, output_time)
               )
    for arg in unknownargs:
        pbs_cmd += " {}".format(arg)
    print(pbs_cmd)
    qsub_path = run(pbs_cmd)
    qsubs.append(qsub_path)
    # if args.load_cuda8:
        # run("sed -i '/date;/a module load cuda\/8.0' {}".format(join('qsub',script_name)))
    i+=1

for i in glob(join("qsub","*.list")):
    remove(i)

script_name = basename(splitext(args.script)[0])
batch = join("qsub",script_name + "_batch_all.sh")
with open(batch,"w") as f:
    f.write("#!/bin/bash\n")
with open(batch,"a") as f:
    for qsub_path in qsubs:
        f.write("msub {}\n".format(qsub_path))

