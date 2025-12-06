#######################################################################################
#######################################################################################
#!/bin/bash

echo "[INFO] Starting custom software setup from tarball..."

# Get a unique job ID (works with jobsub or justin)
#logical_jobid="${CLUSTER_PROCESS:-$$}"  # fallback to PID if undefined
# Logical job index: PROCESS (jobsub) -> CLUSTER_PROCESS (older) -> CLI arg
logical_jobid="${PROCESS:-${CLUSTER_PROCESS:-$1}}"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)_$RANDOM


# Simulation settings
RUN_ID=${RUN_ID:-1}
EVENTS_PER_JOB=5

# PROCESS goes 0, 1, ..., N-1 automatically in jobsub
FIRSTEVENT=$(( PROCESS * EVENTS_PER_JOB + 1 ))
START_EVENT_STRING="${RUN_ID}:0:${FIRSTEVENT}"

# Print basic environment info
echo "[INFO] Hostname: $(hostname)"
echo "[INFO] Start time: $(date)"

# Print current directory and contents
echo "[INFO] Initial working directory:"
pwd
ls -lh

echo ""
echo "[INFO] CONDOR_DIR_INPUT = ${CONDOR_DIR_INPUT}"
echo "[INFO] INPUT_TAR_DIR_LOCAL = ${INPUT_TAR_DIR_LOCAL}"
echo ""

# Print contents of CONDOR_DIR_INPUT (for debug)
echo "[INFO] Contents of CONDOR_DIR_INPUT:"
ls -lh "${CONDOR_DIR_INPUT}"
echo "[INFO] Contents of INPUT_TAR_DIR_LOCAL:"
ls -lh "${INPUT_TAR_DIR_LOCAL}"

# ------------------------------------------------
# Setup environment from unpacked tarball location
# ------------------------------------------------
if [ -e "${INPUT_TAR_DIR_LOCAL}/setup_Grid.sh" ]; then
    echo "[INFO] Found setup_Grid.sh. Sourcing..."
    source "${INPUT_TAR_DIR_LOCAL}/setup_Grid.sh"
else
    echo "[ERROR] setup_Grid.sh not found in ${INPUT_TAR_DIR_LOCAL}"
    exit 99
fi

# Check if lar command is available
which lar
if [ $? -ne 0 ]; then
    echo "[ERROR] lar not found in PATH after setup. Exiting."
    exit 98
fi

echo "[INFO] Local software setup complete"
voms-proxy-info -all






# -----------
# GEN STAGE
# -----------
GEN_FCL="${INPUT_TAR_DIR_LOCAL}/work/my_pdhd_production/scripts/prod_cosmics_radiologicals_protodunehd.fcl"
if [ ! -f "$GEN_FCL" ]; then
    echo "ERROR: $GEN_FCL not found!"
    exit 80
fi

echo "[INFO] Running GEN stage with FHiCL: $GEN_FCL"
#lar -c "$GEN_FCL" -o cosmic_gen_${logical_jobid}_${timestamp}.root -n 5
lar -c "$GEN_FCL" -o cosmic_gen_${logical_jobid}_${timestamp}.root -n $EVENTS_PER_JOB -e "$START_EVENT_STRING" 
GEN_STATUS=$?
if [ $GEN_STATUS -ne 0 ]; then
    echo "[ERROR] GEN stage failed with status $GEN_STATUS"
    exit 10
fi
echo "GEN stage completed successfully."
pwd
ls -lh



# ----------------
# G4 STAGE 1 & 2
# ----------------
G4_FCL="${INPUT_TAR_DIR_LOCAL}/work/my_pdhd_production/scripts/photonlibrary_g4_protodunehd.fcl"
if [ ! -f "$G4_FCL" ]; then
    echo "ERROR: $G4_FCL not found!"
    exit 81
fi

lar -c "$G4_FCL" -s cosmic_gen_${logical_jobid}_${timestamp}.root -o cosmic_g4_${logical_jobid}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "G4 Stage 1 & 2 failed"
    exit 11
fi
ls -lh
echo "G4 (photonLibrary) stage completed. Removing GEN output..."
rm -f cosmic_gen_${logical_jobid}_${timestamp}.root




# ------------------
# Detsim Stage 1
# ------------------
DETSIM_ONE_FCL="${INPUT_TAR_DIR_LOCAL}/work/my_pdhd_production/scripts/standard_detsim_protodunehd_stage1.fcl"
if [ ! -f "$DETSIM_ONE_FCL" ]; then
    echo "ERROR: $DETSIM_ONE_FCL not found!"
    exit 82
fi

lar -c "$DETSIM_ONE_FCL" -s cosmic_g4_${logical_jobid}_${timestamp}.root -o cosmic_detsim_stage1_${logical_jobid}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "Detsim Stage 1 failed"
    exit 12
fi
ls -lh
echo "Detsim Stage 1 completed. Removing input file from G4 stage..."
rm -f cosmic_g4_${logical_jobid}_${timestamp}.root




# ------------------
# Detsim Stage 2
# ------------------
DETSIM_TWO_FCL="${INPUT_TAR_DIR_LOCAL}/work/my_pdhd_production/scripts/standard_detsim_protodunehd_stage2.fcl"
if [ ! -f "$DETSIM_TWO_FCL" ]; then
    echo "ERROR: $DETSIM_TWO_FCL not found!"
    exit 83
fi

lar -c "$DETSIM_TWO_FCL" -s cosmic_detsim_stage1_${logical_jobid}_${timestamp}.root -o cosmic_detsim_stage2_${logical_jobid}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "Detsim Stage 2 failed"
    exit 13
fi
ls -lh
echo "Detsim Stage 2 completed. Removing input file from Detsim stage 1..."
rm -f cosmic_detsim_stage1_${logical_jobid}_${timestamp}.root




# ------------------
# Reco STAGE
# ------------------
RECO_FCL="${INPUT_TAR_DIR_LOCAL}/work/my_pdhd_production/scripts/standard_reco_protodunehd_MC.fcl"
if [ ! -f "$RECO_FCL" ]; then
    echo "ERROR: $RECO_FCL not found!"
    exit 84
fi

lar -c "$RECO_FCL" -s cosmic_detsim_stage2_${logical_jobid}_${timestamp}.root -o cosmic_reco_${logical_jobid}_eventID${FIRSTEVENT}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "Reco Stage failed"
    exit 14
fi
ls -lh
echo "Reco completed. Removing input file from Detsim stage 2..."

rm -f cosmic_detsim_stage2_${logical_jobid}_${timestamp}.root





# ------------------
# Michelt0
# ------------------
MICHEL_FCL="${INPUT_TAR_DIR_LOCAL}/work/my_pdhd_production/scripts/runmicheltime.fcl"
if [ ! -f "$MICHEL_FCL" ]; then
    echo "ERROR: $MICHEL_FCL not found!"
    exit 85
fi

lar -c "$MICHEL_FCL" -s cosmic_reco_${logical_jobid}_eventID${FIRSTEVENT}_${timestamp}.root
if [ $? -ne 0 ]; then
    echo "Michelt0 Stage failed"
    exit 15
fi
ls -lh
echo "Michel Timing completed."



# --------------------
# MC Truth extraction
# --------------------
MCTRUTH_FCL="${INPUT_TAR_DIR_LOCAL}/work/my_pdhd_production/scripts/pdhd_Truechecks.fcl"
if [ ! -f "$MCTRUTH_FCL" ]; then
    echo "ERROR: $MCTRUTH_FCL not found!"
    exit 86
fi

lar -c "$MCTRUTH_FCL" -s cosmic_reco_${logical_jobid}_eventID${FIRSTEVENT}_${timestamp}.root > print.txt
if [ $? -ne 0 ]; then
    echo "MC Truth Stage failed"
    exit 16
fi
ls -lh
echo "MC Truth extraction completed."





# -------------------
# Copy final output
# -------------------
#copy michelt0 result (the output always has the same name)---
[ -f michelt0_Decon.root ] || { echo "Missing michelt0_Decon.root"; exit 25; }
mv michelt0_Decon.root michelt0_run${RUN_ID}_job${logical_jobid}_event${FIRSTEVENT}_${timestamp}.root
ifdh cp -D michelt0_run${RUN_ID}_job${logical_jobid}_event${FIRSTEVENT}_${timestamp}.root /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/new_michelt0/
if [ $? -ne 0 ]; then
    echo "Output (Michelt0) copy failed!"
    exit 26
fi

[ -f print.txt ] || { echo "Missing print.txt"; exit 27; }
mv print.txt mcTruth_run${RUN_ID}_job${logical_jobid}_event${FIRSTEVENT}_${timestamp}.txt
ifdh cp -D mcTruth_run${RUN_ID}_job${logical_jobid}_event${FIRSTEVENT}_${timestamp}.txt /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/new_mcTruth/
if [ $? -ne 0 ]; then
    echo "Output (MC truth) copy failed!"
    exit 28
fi

ls -lh
echo "Final output copied. Removing Reco output..."


#Modified on 20251109, to save the ART root file--------
ifdh cp -D cosmic_reco_${logical_jobid}_eventID${FIRSTEVENT}_${timestamp}.root /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/new_mcTruth/

if [ $? -ne 0 ]; then
    echo "Output (ART root file) copy failed!"
    exit 29
fi
#-------------------------------------------------------


rm -f cosmic_reco_${logical_jobid}_eventID${FIRSTEVENT}_${timestamp}.root
rm -f michelt0_run${RUN_ID}_job${logical_jobid}_event${FIRSTEVENT}_${timestamp}.root
rm -f mcTruth_run${RUN_ID}_job${logical_jobid}_event${FIRSTEVENT}_${timestamp}.txt



echo "Final output (michelt0 and mcTruth) stored at: /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel"
echo "All steps completed successfully. Job done!"
