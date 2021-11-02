#!/bin/python

import os
import subprocess
import shutil
#from utilities import templates



def freesurfer_resample_prep(fs_white, fs_pial, fs_sphere, group_sphere, fs_midthick, group_midthick, fs_sphere_gii):
    '''
    Wrapper for wb_shortcuts -freesurfer-resample-prep

    Parameters
    ----------
    fs_white: str
        Path to Individual space Freesurfer WHITE surface 

    fs_pial: str
        Path to Individual space Freesurfer PIAL surface 

    fs_sphere: str
        Path to Individual space Freesurfer SPHERE surface 

    group_sphere: str
        Path to the Group space sphere in the "standard_mesh_atlases/resample_fsaverage" directory

    fs_midthick: str
        Path for where to write the new Individual space Freesurfer MIDTHICKNESS surface 

    group_midthick: str
        Path for where to write the new Group space Freesurfer MIDTHICKNESS surface 

    fs_sphere_gii: str
        Path for where to write the new deformed Individual space registration SPHERE
    '''
    
    # execute
    subprocess.call([
        'wb_shortcuts', '-freesurfer-resample-prep', 
        fs_white, fs_pial, fs_sphere,
        group_sphere, 
        fs_midthick, group_midthick, 
        fs_sphere_gii])


def metric_resample(metric_in, current_sphere, new_sphere, metric_out, current_area, new_area):
    '''
    Wrapper for wb_shortcuts -freesurfer-resample-prep

    Parameters
    ----------
    metric_in: str

    current_sphere: str

    new_sphere: str

    metric_out: str

    current_area: str

    new_area: str

    '''
    # execute
    subprocess.call([
        'wb_command', '-metric-resample',
        metric_in,
        current_sphere,
        new_sphere,
        'ADAP_BARY_AREA',
        metric_out,
        '-area-surfs',
        current_area,
        new_area
        ])


def resample_fsIndiv_to_group(fs_dir, group_space, metric, out_dir):
    '''
    Resample a metric file (e.g. thickness) in Freesurfer Individual space to any Group surface

    Parameters
    ----------
    fs_dir: str
        Path to Individual Freesurfer directory (the one that contains /surf, /mri, /label, etc.)

    group_space: str
        Group surface to project to. 
        Can be: 'fsaverage', 'fsaverage6', 'fsaverage5', 'fsaverage4', 'fslr164k', 'fslr32k', 'fslr59k'

    metric: str or list of strings
        Which modality to convert.
        Can be: 'thickness', 'area', 'volume', 'curv'

    out_dir: str
        Directory to place all output files
    '''

    #fs_dir = '/fmri-qunex/research/imaging/datasets/embarc/processed_data/pf-pipelines/qunex-nbridge/studies/embarc-20201122-LHzJPHi4/sessions/MG0008_baseline/hcp/MG0008_baseline/T1w/MG0008_baseline'
    #out_dir = '/home/ubuntu/Projects/EMBARC/embarc_palm/work/MG0008_baseline'
    #group_space = 'fslr32k'
    #hemi = 'lh'
    if type(metric) == str:
        metric_list = [metric]
    else:
        metric_list = metric
    
    # temporary directory for intermediate files
    tmp_dir = os.path.join(out_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    for hemi in ['lh', 'rh']:
        # Define paths with static directory structure
        fs_white       = os.path.join(fs_dir, 'surf/{}.white'.format(hemi))
        fs_pial        = os.path.join(fs_dir, 'surf/{}.pial'.format(hemi))
        fs_sphere      = os.path.join(fs_dir, 'surf/{}.sphere'.format(hemi))
        fs_sphere_gii  = os.path.join(tmp_dir, '{}.sphere.reg.surf.gii'.format(hemi))
        fs_midthick    = os.path.join(tmp_dir, '{}.midthickness.surf.gii'.format(hemi))
        group_midthick = os.path.join(tmp_dir, '{}.midthickness.{}.surf.gii'.format(hemi, group_space))
        group_sphere   = templates[group_space][hemi]['sphere']

        # Prep for resampling by converting to gifti and creating midthickness files
        freesurfer_resample_prep(fs_white, fs_pial, fs_sphere, group_sphere, fs_midthick, group_midthick, fs_sphere_gii)
        
        for cur_metric in metric_list:
            # define metric i/o
            fs_metric_in = os.path.join(fs_dir, 'surf/{}.{}'.format(hemi, cur_metric))
            metric_in    = os.path.join(tmp_dir, '{}.{}.func.gii'.format(hemi, cur_metric))
            metric_out   = os.path.join(out_dir, '{}.{}.{}.func.gii'.format(hemi, group_space, cur_metric))

            # convert the individual freesurfer metric file to a gifti
            mgh_to_gii(input=fs_metric_in, white_file=fs_white, output=metric_in)
            
            # resample from individual freesurfer to group space
            metric_resample(metric_in=metric_in, 
                            current_sphere=fs_sphere_gii, 
                            new_sphere=group_sphere, 
                            metric_out=metric_out, 
                            current_area=fs_midthick, 
                            new_area=group_midthick)
    
    # remove intermediate files
    shutil.rmtree(tmp_dir)



def resample_fsavg_to_fslr(gii_input, fslr_mesh, fsavg_mesh, hemi, label_or_metric, out_file):
    '''
    Use HCP Connectome Workbench to resample a surface file from Freesurfer to HCP fslr space.

    Parameters
    ----------
    gii_input: str, path
        Freesurfer surface file in Gifti Format

    fslr_mesh: string
        Mesh resolution in HCP_fslr space. Can be: "164k", "59k", "32k"

    fsavg_mesh: string
        Mesh resolution in fsaverage space. Can be "fsaverage", "fsaverage6", "fsaverage5", "fsaverage4"

    hemi: string
        "lh" or "rh"

    label_or_metric : string
        "label" or "metric". Define the type of surface data being converted. 

    out_file: str, path
        Output file (e.g. my_output.label.gii)
    '''

    # keep track of the mesh resolution for each fsaverage space
    fsavg_dict = {
        'fsaverage': '164k',
        'fsaverage6': '41k',
        'fsaverage5': '10k',
        'fsaverage4': '3k'
    }

    # parse hemisphere
    if hemi == 'lh':
        HEMI='L'
    elif hemi == 'rh':
        HEMI='R'
    else:
        return 

    # parse whether we are resampling a label or 
    if label_or_metric == 'label':
        resample_type = '-label-resample'
    elif label_or_metric == 'metric':
        resample_type = '-metric-resample'
    else: 
        return

    # define relative paths to files
    resample_dir = '../data/standard_mesh_atlases/resample_fsaverage'
    
    orig_sphere = os.path.join(resample_dir, 'fsaverage_std_sphere.{}.{}_fsavg_{}.surf.gii'.format(HEMI, fsavg_dict[fsavg_mesh], HEMI))
    orig_area   = os.path.join(resample_dir, 'fsaverage.{}.midthickness_va_avg.{}_fsavg_{}.shape.gii'.format(HEMI, fsavg_dict[fsavg_mesh], HEMI))
    
    new_sphere = os.path.join(resample_dir, 'fs_LR-deformed_to-fsaverage.{}.sphere.{}_fs_LR.surf.gii'.format(HEMI, fslr_mesh))
    new_area   = os.path.join(resample_dir, 'fs_LR.{}.midthickness_va_avg.{}_fs_LR.shape.gii'.format(HEMI, fslr_mesh))

    # execute
    subprocess.call([
        'wb_command', 
        resample_type,
        gii_input,
        orig_sphere,
        new_sphere,
        'ADAP_BARY_AREA',
        out_file,
        '-area-metrics',
        orig_area,
        new_area
        ])



def wb_resample_label(label_in, label_out, cur_sphere, cur_area, new_sphere, new_area):
    '''
    Wrapper for resampling label file using workbench
    '''
    subprocess.call(['wb_command',
                '-label-resample',
                label_in, 
                cur_sphere,
                new_sphere,
                'ADAP_BARY_AREA',
                label_out,
                '-area-metrics',
                cur_area,
                new_area])


def split_dlabel(cifti_file, gii_left, gii_right):
    '''
    HCP workbench function call to split a dlabel cifti file into cortex only giftis
    '''
    subprocess.call(['wb_command',
                '-cifti-separate',
                cifti_file, 
                'COLUMN',
                '-label', 'CORTEX_LEFT', gii_left, 
                '-label', 'CORTEX_RIGHT', gii_right])
    return gii_left, gii_right


def gii_to_annot(gii_file, white_file, annot_file):
    cmd = [
        'mris_convert',
        '--annot', gii_file, white_file, annot_file
    ]
    print(' '.join(cmd))
    subprocess.call(cmd)


def mgh_to_gii(input, white_file, output):
    '''
    Wrapper for Freesurfer mris_convert. 

    Convert a Freesurfer surface file (e.g. lh.thickness) to Gifti format

    Parameters
    ----------
    input: string, path
        Full path to the input file

    output: string, path
        Full path to the output file
    '''
    subprocess.call([
        'mris_convert', '-c', input, white_file, output
    ])


def aparc_to_gii(gii_file, white_file, aparc_file):
    subprocess.call([
        'mris_convert',
        '--annot', gii_file, white_file, aparc_file
    ])


def resample_fslr_to_fsavg(gii_input, fslr_mesh, fsavg_mesh, hemi, label_or_metric, out_file):
    '''
    Use HCP Connectome Workbench to resample a surface atlas from HCP

    @param gii_input: GiFTI formatted surface input file (freesurfer space)
    @param fslr_mesh: Mesh resolution (32k, 59k, 164k) in fslr space to resample to
    @param fsavg_mesh: Resolution of the freesurfer input gifti file (fsaverage, fsaverage6, fsaverage5, etc...)
    @param hemi: "lh" or "rh"
    @label_or_metric: "label" or "metric"
    @out_file: full path to the output file (e.g. my_output.label.gii)
    '''

    # keep track of the mesh resolution for each fsaverage space
    fsavg_dict = {
        'fsaverage': '164k',
        'fsaverage6': '41k',
        'fsaverage5': '10k',
        'fsaverage4': '3k'
    }

    # parse hemisphere
    if hemi == 'lh':
        HEMI='L'
    elif hemi == 'rh':
        HEMI='R'
    else:
        return 

    # parse whether we are resampling a label or 
    if label_or_metric == 'label':
        resample_type = '-label-resample'
    elif label_or_metric == 'metric':
        resample_type = '-metric-resample'
    else: 
        return

    # define relative paths to files
    resample_dir = '../data/standard_mesh_atlases/resample_fsaverage'
    
    orig_sphere = os.path.join(resample_dir, 'fsaverage_std_sphere.{}.{}_fsavg_{}.surf.gii'.format(HEMI, fsavg_dict[fsavg_mesh], HEMI))
    orig_area   = os.path.join(resample_dir, 'fsaverage.{}.midthickness_va_avg.{}_fsavg_{}.shape.gii'.format(HEMI, fsavg_dict[fsavg_mesh], HEMI))
    
    new_sphere = os.path.join(resample_dir, 'fs_LR-deformed_to-fsaverage.{}.sphere.{}_fs_LR.surf.gii'.format(HEMI, fslr_mesh))
    new_area   = os.path.join(resample_dir, 'fs_LR.{}.midthickness_va_avg.{}_fs_LR.shape.gii'.format(HEMI, fslr_mesh))

    # execute
    subprocess.call([
        'wb_command', 
        resample_type,
        gii_input,
        orig_sphere,
        new_sphere,
        'ADAP_BARY_AREA',
        out_file,
        '-area-metrics',
        orig_area,
        new_area
        ])


# -----------------
# Dictionary with Freesurfer/FSLR reference files
# -----------------
resample_dir = '../data/standard_mesh_atlases/resample_fsaverage'
fs_dir = '../data/surface/Freesurfer7.1.1'

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