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
timestamp=$(date -u +%Y%m%dT%H%M%SZ)



#Make sure we know where we are working and where to look for certain files
echo "printing working directory of grid node"
pwd
local_dir=$(pwd)
#see whats there
echo "the local repo has the following folders and files:"
ls -ltrha
echo "now cd-ing to CONDOR_DIR_INPUT AT $CONDOR_DIR_INPUT"
cd $CONDOR_DIR_INPUT
echo "now printing the CONDOR_DIR_INPUT path:"
pwd
echo "now ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT"
ls -ltrha



# -----------
# GEN STAGE
# -----------
lar -c prod_cosmics_radiologicals_protodunehd.fcl -o cosmic_gen_${jobid}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "GEN stage failed"
    exit 10
fi
echo "Gen successfully made!"
pwd
ls -ltrha



# ----------------
# G4 STAGE 1 & 2
# ----------------
lar -c photonlibrary_g4_protodunehd.fcl -s cosmic_gen_${jobid}_${timestamp}.root -o cosmic_g4_${jobid}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "G4 Stage 1 & 2 failed"
    exit 11
fi
ls -ltrha
echo "G4 (photonLibrary) completed. Removing input file from GEN stage..."
rm -f cosmic_gen_${jobid}_${timestamp}.root



# ------------------
# PDS Detsim STAGE
# ------------------
if [ ! -f "pds_detsim.fcl" ]; then
    echo "ERROR: pds_detsim.fcl not found!"
    exit 99
fi

lar -c pds_detsim.fcl -s cosmic_g4_${jobid}_${timestamp}.root -o cosmic_detsim_${jobid}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "Detsim Stage failed"
    exit 12
fi
ls -ltrha
echo "Detsim (PDS only) completed. Removing input file from G4 stage..."
rm -f cosmic_g4_${jobid}_${timestamp}.root



# ------------------
# PDS RecoNew STAGE
# ------------------
lar -c pds_recoNew.fcl -s cosmic_detsim_${jobid}_${timestamp}.root -o cosmic_recoNew_${jobid}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "RecoNew Stage failed"
    exit 13
fi
ls -ltrha
echo "RecoNew (PDS only) completed. Removing input file from Detsim stage..."
rm -f cosmic_detsim_${jobid}_${timestamp}.root



# -------------------
# Copy final output
# -------------------
ifdh cp -D cosmic_recoNew_${jobid}_${timestamp}.root /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/MY_production/
if [ $? -ne 0 ]; then
    echo "Output copy failed!"
    exit 14
fi
ls -ltrha
echo "Final output copied. Removing RecoNew output..."
rm -f cosmic_recoNew_${jobid}_${timestamp}.root



echo "Final output stored at: /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/MY_production/cosmic_recoNew_${jobid}_${timestamp}.root"
echo "All steps completed successfully. Job done!"