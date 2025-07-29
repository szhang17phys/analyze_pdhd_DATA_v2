#######################################################################################
#######################################################################################
#!/bin/bash

echo "doing general software setup"
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunesw v10_08_02d00 -q e26:prof
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setup
setup fife_utils
#get info about current grid proxy
voms-proxy-info -all
echo "software setup complete"

# Get a unique job ID (works with jobsub or justin)
jobid="${CLUSTER_PROCESS:-$$}"  # fallback to PID if undefined
echo "Resolved job ID: $jobid"


#Make sure we know where we are working and where to look for certain files
echo "printing working directory of grid node"
pwd
local_dir=`pwd`
#see whats there
echo "the local repo has the following folders and files:"
ls -ltrha
echo "now cd-ing to CONDOR_DIR_INPUT AT $CONDOR_DIR_INPUT"
cd $CONDOR_DIR_INPUT
echo "now printing the CONDOR_DIR_INPUT path:"
pwd
echo "now ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT"
ls -ltrha




# -------------------------------
# GEN STAGE
# -------------------------------
lar -c prod_cosmics_radiologicals_protodunehd.fcl -o cosmic_gen_${jobid}.root
if [ $? -ne 0 ]; then
    echo "GEN stage failed"
    exit 10
fi
echo "Gen successfully made!"
ls -ltrha

# -------------------------------
# G4 STAGE 1
# -------------------------------
lar -c standard_g4_protodunehd_stage1.fcl -s cosmic_gen_${jobid}.root -o cosmic_g4_stage1_${jobid}.root
if [ $? -ne 0 ]; then
    echo "G4 Stage 1 failed"
    exit 11
fi
echo "G4 Stage 1 completed. Removing input file from GEN stage..."
rm -f cosmic_gen_${jobid}.root

# -------------------------------
# G4 STAGE 2
# -------------------------------
lar -c standard_g4_protodunehd_stage2.fcl -s cosmic_g4_stage1_${jobid}.root -o cosmic_g4_stage2_${jobid}.root
if [ $? -ne 0 ]; then
    echo "G4 Stage 2 failed"
    exit 12
fi
echo "G4 Stage 2 completed. Removing G4 Stage 1 output..."
rm -f cosmic_g4_stage1_${jobid}.root

# -------------------------------
# Copy final output
# -------------------------------
ifdh cp -D cosmic_g4_stage2_${jobid}.root /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/MY_production/
if [ $? -ne 0 ]; then
    echo "Output copy failed!"
    exit 13
fi
echo "Final output copied. Removing G4 Stage 2 output..."
rm -f cosmic_g4_stage2_${jobid}.root

echo "All steps completed successfully. Job done!"