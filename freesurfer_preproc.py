from sys import argv
from os.path import exists,join,split,splitext,abspath
from os import system,mkdir,remove,environ
from shutil import *
from glob import glob


cortical_dir = "label_cortical"
vol_dir = "volumes_cortical"
sub_vol_dir = "volumes_subcortical"

if len(argv) < 3:
    print "Usage: %s <freeSurfer-dir> <T1.nii.gz> [force]" % argv[0]
    exit(0)

T1 = abspath(argv[2])
output_dir = split(abspath(argv[2]))[0]
subject = split(output_dir)[1]

# Shall we force a re-computation
force = ((len(argv) > 3) and argv[3] == 'force')

# Make the output directories if necessary    
if not exists(join(output_dir,"mri")):
    mkdir(join(output_dir,"mri"))

if not exists(join(output_dir,"mri/orig")):
    mkdir(join(output_dir,"mri/orig"))

fs_dir = abspath(argv[1])
environ['FREESURFER_HOME'] = fs_dir
environ['SUBJECTS_DIR'] = split(output_dir)[0]

if force or not exists(join(output_dir,"mri/orig/001.mgz")):
    system(join(fs_dir,'bin/mri_convert') + " %s %s" % (abspath(argv[2]),join(output_dir,"mri/orig/001.mgz")))


if force or not exists(join(output_dir,"mri","aparc+aseg.mgz")):
    system(join(fs_dir,'bin/recon-all') + " -s %s -all -no-isrunning" % subject)


if force or not exists(join(output_dir,"T12FA.mat")):
    system(join(fs_dir,'bin/mri_convert') + " %s %s " % (join(output_dir,"mri","brain.mgz"),abspath(argv[2])))
    
if force or not exists(join(output_dir,"FA2T1.mat")):
    system(join(fs_dir,'bin/flirt') + " -in %s -ref %s -omat %s" % (join(output_dir,"FA.mgz"),abspath(argv[2]),join(output_dir,"FA2T1.mat")))
    
if force or not exists(join(output_dir,"T12FA.mat")):
    system(join(fs_dir,'bin/convert_xfm') + " -omat %s -inverse %s" % (join(output_dir,"T12FA.mat"),join(output_dir,"FA2T1.mat")))
    
if not exists(join(output_dir,"EDI")):
    mkdir(join(output_dir,"EDI"))


if force or not exists(join(output_dir,"%s_s2fa/lh_thalamus_s2fa.nii.gz")):
        
    if not exists(join(output_dir,"label_cortical")):
        mkdir(join(output_dir,"label_cortical"))    
    
    # extract cortical labels (extralabels) 
    if force or not exists(join(output_dir,"volumes_subcortical/rh_thalamus.nii.gz")):
        system(join(fs_dir,'mri_annotation2label') + " --subject %s --hemi rh --annotation aparc --outdir label_cortical" % subject)
        
    if force or not exists(join(output_dir,"volumes_subcortical/lh_thalamus.nii.gz")):
        system(join(fs_dir,'mri_annotation2label') + " --subject %s --hemi lh --annotation aparc --outdir label_cortical" % subject)
        
    
    # extract volume labels (label2vol)
    for label in glob(join(output_dir,"label_cortical","*.label")):
        vol_name = splitext(split(label)[1])[0] + ".nii.gz"
        
        if force or not exists(join(output_dir,"volumes_cortical",vol_name)):
            system(join(fs_dir,'mri_label2vol') + " --label %s --temp %s --identity --o %s" % (label,T1,join(output_dir,"volumes_cortical",vol_name)))
    
    
    # make_subcortical_vols
    #if force or not exists(join(output_dir,"mri","aseg.nii.mgz"))
    

