#!/bin/bash

echo "Running on $(hostname) at ${GLIDEIN_Site}. GLIDEIN_DUNESite = ${GLIDEIN_DUNESite}"

# set the output location for copyback. There are many possibilities; here each submission would have its own subdir. 
# REMINDER: do not place more than about 1000 files or subdirectories within any single directory level.

#Change each time-------------------
OUTDIR=/pnfs/dune/scratch/users/${GRID_USER}/computingT2024/pdvd_v5/${CLUSTER}


#Let's rename the output file so it's unique in case we send multiple jobs.
OUTFILE=RSL100cm_${CLUSTER}_${PROCESS}_$(date -u +%Y%m%dT%H%M%SZ).dat

#Added by Shu, 20240621---
#INPUT_TAR_DIR_LOCAL=/exp/dune/date/users/szh2

#Added by Shu, 20240621---
echo ""
echo "Shu: Location of GRID_USER: ${GRID_USER}"
echo "Shu: Location of CONDOR_DIR_INPUT: ${CONDOR_DIR_INPUT}"
echo "Shu: Location of INPUT_TAR_DIR_LOCAL: ${INPUT_TAR_DIR_LOCAL}"
echo ""
echo "Shu: Output directory: ${OUTDIR}"
echo "Shu: Output filename: ${OUTFILE}"
echo ""

#make sure we see what we expect
echo ""
echo "pwd: "
pwd
echo ""

ls -l $CONDOR_DIR_INPUT

if [ -e ${INPUT_TAR_DIR_LOCAL}/setup_Grid.sh ]; then    
    . ${INPUT_TAR_DIR_LOCAL}/setup_Grid.sh
else
  echo "Error, setup script not found. Exiting."
  exit 1
fi

# cd back to the top-level directory since we know that's writable
cd ${_CONDOR_JOB_IWD}

#Added by Shu, Jun 21, 2024---
echo ""
echo "Shu: Location of _CONDOR_JOB_IWD: ${_CONDOR_JOB_IWD}"
echo ""


#Change each time-------------------------------
#symlink the desired fcl to the current directory
ln -s ${INPUT_TAR_DIR_LOCAL}/work/pdvd_v5_comp/photonFull_module0_sim.fcl .


# set some other very useful environment variables for xrootd and IFDH
export IFDH_CP_MAXRETRIES=2
export XRD_CONNECTIONRETRY=32
export XRD_REQUESTTIMEOUT=14400
export XRD_REDIRECTLIMIT=255
export XRD_LOADBALANCERTTL=7200
export XRD_STREAMTIMEOUT=14400 # many vary for your job/file type

#get the xrootd URI for the input file. Not necessary for SAM inputs when using ifdh_art, etc.
#myinfile=$(samweb get-file-access-url --schema=root PDSPProd4a_protoDUNE_sp_reco_stage1_p1GeV_35ms_sce_datadriven_18800650_2_20210414T012053Z.root)

#now we should be in the work dir if setupmay2021tutorial-grid.sh worked

#added by Shu, Jun 21, 2024---
echo ""
echo "Shu: Test command before lar: pwd"
pwd
echo ""


#Change each time-----------------------------------
lar -c photonFull_module0_sim.fcl -n 100
LAR_RESULT=$?   # ALWAYS kepe track of the exit status or your main command!!!


if [ $LAR_RESULT -ne 0 ]; then
    echo "lar exited with abnormal status $LAR_RESULT. See error outputs."
    exit $LAR_RESULT
fi

#Added by Shu, 20240621---
echo ""
echo "Shu: Lar command is well executed!"
echo ""



if [ -f phinf.dat ]; then

    mv phinf.dat $OUTFILE
    
    #and copy our output file back

    ifdh cp -D $OUTFILE $OUTDIR

    #check the exit status to see if the copyback actually worked. Print a message if it did not.
    IFDH_RESULT=$?
    if [ $IFDH_RESULT -ne 0 ]; then
	echo "Error during output copyback. See output logs."
	exit $IFDH_RESULT
    fi
fi

#If we got this far, we succeeded.
echo "Completed successfully."
exit 0
