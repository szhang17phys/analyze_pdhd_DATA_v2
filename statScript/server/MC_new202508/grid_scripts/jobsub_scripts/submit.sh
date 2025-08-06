#jobsub_submit -G dune --mail_never -N 10 --memory=16000MB --disk=10GB --cpu=1 --expected-lifetime=30h --resource-provides=usage_model=DEDICATED,OPPORTUNISTIC,OFFSITE -l '+SingularityImage=\"/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest\"' --append_condor_requirements='(TARGET.HAS_Singularity==true&&TARGET.HAS_CVMFS_dune_opensciencegrid_org==true&&TARGET.HAS_CVMFS_larsoft_opensciencegrid_org==true&&TARGET.CVMFS_dune_opensciencegrid_org_REVISION>=1105)' file:///exp/dune/app/users/szh2/michel_Jun2025/work/my_mc_production/jobsub/run_all.sh

jobsub_submit -G dune \
  --mail_never \
  -N 10 \
  --memory=16000MB \
  --disk=10GB \
  --cpu=1 \
  --expected-lifetime=30h \
  --resource-provides=usage_model=DEDICATED,OPPORTUNISTIC,OFFSITE \
  -l '+SingularityImage="/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest"' \
  --append_condor_requirements='(TARGET.HAS_Singularity==true&&TARGET.HAS_CVMFS_dune_opensciencegrid_org==true&&TARGET.HAS_CVMFS_larsoft_opensciencegrid_org==true&&TARGET.CVMFS_dune_opensciencegrid_org_REVISION>=1105)' \
  -f /exp/dune/app/users/szh2/michel_Jun2025/work/my_mc_production/jobsub/pds_detsim.fcl \
  -f /exp/dune/app/users/szh2/michel_Jun2025/work/my_mc_production/jobsub/pds_recoNew.fcl \
  file:///exp/dune/app/users/szh2/michel_Jun2025/work/my_mc_production/jobsub/run_all.sh

