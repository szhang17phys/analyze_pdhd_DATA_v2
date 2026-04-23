#######################################################################################
#######################################################################################
#!/bin/bash

echo "doing general software setup"
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunesw v09_85_00d00 -q e26:prof
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setup
setup fife_utils
#get info about current grid proxy
voms-proxy-info -all
echo "software setup complete"

echo "echo-ing JOBSUBID: $JOBSUBJOBID"
echo $JOBSUBJOBID | sed 's/.*\.\([0-9]*\)\@[0-9]*.*/\1/p;d'
jobid=`echo $JOBSUBJOBID | sed 's/.*\.\([0-9]*\)\@[0-9]*.*/\1/p;d'`
echo "the number is: $jobid"

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

nevt=100
model=hn_br
prefix=prodaddgenie_nnbar_${model}_dune10kt_1x2x6
ifdh cp /pnfs/dune/persistent/users/lwan/nnbar/AddGENIE/${prefix}.root $CONDOR_DIR_INPUT
echo "again ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT"
ls -ltrha

lar -c standard_g4_dune10kt_1x2x6.fcl -s ${prefix}.root -n $nevt --nskip $(($nevt*$jobid)) -o ${prefix}_G4_${jobid}.root
echo "finally ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT"
ls -ltrha

lar -c standard_detsim_dune10kt_1x2x6.fcl -n $nevt -s ${prefix}_G4_${jobid}.root -o ${prefix}_G4_detsim_${jobid}.root
ls -ltrha

lar -c standard_reco1_dune10kt_1x2x6.fcl -n $nevt -s ${prefix}_G4_detsim_${jobid}.root -o ${prefix}_G4_detsim_reco1_${jobid}.root
ls -ltrha

lar -c standard_reco2_dune10kt_1x2x6.fcl -n $nevt -s ${prefix}_G4_detsim_reco1_${jobid}.root -o ${prefix}_G4_detsim_reco1_reco2_${jobid}.root
ls -ltrha

lar -c standard_ana_dune10kt_1x2x6_hist.fcl -n $nevt -s ${prefix}_G4_detsim_reco1_reco2_${jobid}.root 
ls -ltrha

mv ana_hist.root ${prefix}_G4_detsim_reco1_reco2_anahist_${jobid}.root

ifdh cp -D ${prefix}_G4_detsim_reco1_reco2_${jobid}.root /pnfs/dune/scratch/users/lwan/v09_85_00/nnbar/${model}/reco2/
ifdh cp -D ${prefix}_G4_detsim_reco1_reco2_anahist_${jobid}.root /pnfs/dune/scratch/users/lwan/v09_85_00/nnbar/${model}/anahist
