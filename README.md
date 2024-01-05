# meld_fe_io
This is a repository for shared data loaders and housekeeping tools for the MELD focal epilepsy project

** How to run MRI QC scripts **

1. export Freesurfer V7.4 for syntheseg
```bash
export FREESURFER_HOME=/home/mathilde/Programs/freesurfer_v7.4
source $FREESURFER_HOME/SetUpFreeSurfer.sh
```

2. activate environment compatible with synthseg GPU
conda activate synthseg_38

3. modify the parameter script (scripts/qc/meld_mri_qc/parameters.py) and run script
python scripts/qc/meld_mri_qc/main.py




Contributors - Mathilde Ripart, Niccolo McConnell , Sophie Adler, Konrad wagstyl
