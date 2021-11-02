#!/bin/python

import os 

# -----------------
# Dictionary with Freesurfer/FSLR reference files
# -----------------
resample_dir = '../templates/surface/standard_mesh_atlases/resample_fsaverage'
fs_dir = '../templates/surface/Freesurfer7.1.1'

# keep track of the mesh resolution for each fsaverage space
fsavg_dict = {
    'fsaverage': '164k',
    'fsaverage6': '41k',
    'fsaverage5': '10k',
    'fsaverage4': '3k'
}

templates = dict()
for fsavg in fsavg_dict.keys():
    templates[fsavg] = dict()

    for hemi_iter in (('lh', 'L'), ('rh', 'R')):
        hemi, HEMI = hemi_iter
        templates[fsavg][hemi] = dict()
        templates[fsavg][hemi]['sphere'] = os.path.join(resample_dir, '{}_std_sphere.{}.{}_fsavg_{}.surf.gii'.format(fsavg, HEMI, fsavg_dict[fsavg], HEMI))
        templates[fsavg][hemi]['area']   = os.path.join(resample_dir, '{}.{}.midthickness_va_avg.{}_fsavg_{}.shape.gii'.format(fsavg, HEMI, fsavg_dict[fsavg], HEMI))
        templates[fsavg][hemi]['white']  = os.path.join(fs_dir, fsavg, 'surf/{}.white'.format(hemi))

# fslr ref files
for fslr_iter in (('fslr164k', '164'), ('fslr32k', '32k'), ('fslr59k', '59k')):
    fslr, fslr_mesh = fslr_iter
    templates[fslr] = dict()

    for hemi_iter in (('lh', 'L'), ('rh', 'R')):
        hemi, HEMI = hemi_iter
        templates[fslr][hemi] = dict()
        templates[fslr][hemi]['sphere'] = os.path.join(resample_dir, 'fs_LR-deformed_to-fsaverage.{}.sphere.{}_fs_LR.surf.gii'.format(HEMI, fslr_mesh))
        templates[fslr][hemi]['area']   = os.path.join(resample_dir, 'fs_LR.{}.midthickness_va_avg.{}_fs_LR.shape.gii'.format(HEMI, fslr_mesh))
# -----------------
# -----------------