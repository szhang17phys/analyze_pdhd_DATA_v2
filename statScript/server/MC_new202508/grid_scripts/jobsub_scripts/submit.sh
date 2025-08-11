jobsub_submit -G dune \
  --mail_never \
  -N 100 \
  --memory=16000MB \
  --disk=15GB \
  --cpu=3 \
  --expected-lifetime=8h \
  --tar_file_name=dropbox:///exp/dune/app/users/szh2/michel_Jul2025/michel20250808.tar.gz \
  --resource-provides=usage_model=DEDICATED,OPPORTUNISTIC,OFFSITE \
  --singularity-image /cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest \
  --append_condor_requirements='(TARGET.HAS_Singularity==true && TARGET.HAS_CVMFS_dune_opensciencegrid_org==true && TARGET.HAS_CVMFS_larsoft_opensciencegrid_org==true && TARGET.CVMFS_dune_opensciencegrid_org_REVISION>=1105)' \
  -e GFAL_PLUGIN_DIR=/usr/lib64/gfal2-plugins \
  -e GFAL_CONFIG_DIR=/etc/gfal2.d \
  file:///exp/dune/app/users/szh2/michel_Jul2025/work/my_pdhd_production/run_all.sh

