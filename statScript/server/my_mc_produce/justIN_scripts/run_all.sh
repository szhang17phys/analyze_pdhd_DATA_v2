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



#nevt=10
#model=hn_br
#prefix=prodaddgenie_nnbar_${model}_dune10kt_1x2x6
#ifdh cp /pnfs/dune/persistent/users/lwan/nnbar/AddGENIE/${prefix}.root $CONDOR_DIR_INPUT
echo "again ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT"
ls -ltrha


lar -c prod_cosmics_radiologicals_protodunehd.fcl -o cosmic_gen_${jobid}.root
echo "finally ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT"
ls -ltrha

lar -c standard_g4_protodunehd_stage1.fcl -s cosmic_gen_${jobid}.root -o cosmic_g4_stage1_${jobid}.root
rm -f cosmic_gen_${jobid}.root
echo "after G1 step (Gen output deleted)"
ls -ltrha

lar -c standard_g4_protodunehd_stage2.fcl -s cosmic_g4_stage1_${jobid}.root -o cosmic_g4_stage2_${jobid}.root
rm -f cosmic_g4_stage1_${jobid}.root
echo "after G2 step (G1 output deleted)"
ls -ltrha


ifdh cp -D cosmic_g4_stage2_${jobid}.root /pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/MY_production/
rm -f cosmic_g4_stage2_${jobid}.root
echo "G4 output deleted. Job complete!"

